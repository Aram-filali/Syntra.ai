from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks, File, UploadFile, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import os
import shutil
import tempfile

from ..models.base import get_db, SessionLocal
from ..models.user import User
from ..models.meeting import Meeting, Transcription, MeetingStatus, Summary, ActionItem
from ..services.zoom_service import ZoomService
from ..services.transcription_service import TranscriptionService
from ..utils.dependencies import get_current_user
from ..agents.orchestrator import MeetingIntelligenceOrchestrator
from langchain_openai import ChatOpenAI
from datetime import datetime, timedelta

router = APIRouter()

# --- Background Task Implementation ---

async def process_zoom_import(meeting_id: int, zoom_meeting_id: str, user_id: int):
    """
    Tâche de fond pour transcrire et analyser un meeting Zoom.
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"User {user_id} not found")
            return

        # 1. Récupérer l'URL audio Zoom
        audio_url = ZoomService.get_audio_download_url(db, user, zoom_meeting_id)
        if not audio_url:
            print(f"No audio URL found for Zoom meeting {zoom_meeting_id}")
            return

        # 2. Récupérer les participants Zoom
        participants = ZoomService.get_meeting_participants(db, user, zoom_meeting_id)
        participant_names = [f"{p.get('user_name')} ({p.get('user_email')})" for p in participants]

        # 3. Transcrire avec AssemblyAI
        transcriber = TranscriptionService()
        result = transcriber.transcribe_audio_url(audio_url)
        
        # 4. Enregistrer la transcription
        db_transcription = Transcription(
            meeting_id=meeting_id,
            full_text=result["full_text"],
            speaker_segments=result["speaker_segments"]
        )
        db.add(db_transcription)
        
        # 5. On s'arrête ICI. On ne lance pas l'orchestrateur IA automatiquement.
        
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            meeting.status = MeetingStatus.COMPLETED
            
        db.commit()
    except Exception as e:
        print(f"Error in background process for meeting {meeting_id}: {str(e)}")
    finally:
        db.close()

# --- Routes ---

@router.get("/login")
async def zoom_login(current_user: User = Depends(get_current_user)):
    """
    🔗 Redirige vers la page d'autorisation de Zoom
    """
    # On passe l'ID de l'utilisateur dans le 'state' pour le récupérer au callback
    auth_url = ZoomService.get_auth_url(state=str(current_user.id))
    return {"url": auth_url}

@router.get("/callback")
async def zoom_callback(code: str, state: Optional[str] = None, db: Session = Depends(get_db)):
    """
    ↩️ Callback Zoom pour récupérer les tokens OAuth
    """
    try:
        if not state:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le paramètre 'state' est manquant. Veuillez recliquer sur le bouton de connexion Zoom."
            )
        # 1. Échanger le code contre les tokens
        tokens = ZoomService.exchange_code_for_token(code)
        
        # 2. Récupérer l'utilisateur grâce au state (user_id)
        user_id = int(state)
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
        
        # 3. Enregistrer les tokens
        user.zoom_access_token = tokens["access_token"]
        user.zoom_refresh_token = tokens["refresh_token"]
        user.zoom_token_expires_at = datetime.utcnow() + timedelta(seconds=tokens["expires_in"])
        
        db.commit()
        
        # Redirection vers le dashboard frontend (ou une page de succès)
        return RedirectResponse(url="http://localhost:3001/dashboard?zoom=connected")
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de l'échange du token: {str(e)}"
        )

@router.get("/me/token-info")
async def get_token_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔍 [DEBUG] Récupère les informations du token (scopes inclus)
    """
    try:
        token = ZoomService.get_valid_access_token(db, current_user)
        
        # Appel à l'endpoint Zoom pour obtenir les infos du token
        import requests
        response = requests.get(
            "https://api.zoom.us/v2/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Récupérer les scopes du token (pas directement accessible, mais on peut voir l'erreur)
        return {
            "status": "Token is valid",
            "user_info": response.json() if response.ok else None,
            "token_expires_at": current_user.zoom_token_expires_at.isoformat() if current_user.zoom_token_expires_at else None,
            "note": "Si vous obtenez une erreur 400 avec 'Invalid access token, does not contain scopes', vous devez vous reconnecter à Zoom pour obtenir un nouveau token avec les scopes mis à jour."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur token info: {str(e)}"
        )

@router.get("/account-type")
async def get_account_type(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🏢 Récupère le type de compte Zoom de l'utilisateur (basic, pro, business)
    """
    try:
        if not current_user.zoom_access_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Zoom account not connected"
            )
        
        account_type = ZoomService.get_user_account_type(db, current_user)
        
        # Mettre à jour en base aussi
        current_user.zoom_account_type = account_type
        db.commit()
        
        return {
            "account_type": account_type,
            "is_basic": account_type == "basic",
            "is_pro": account_type == "pro",
            "is_business": account_type == "business"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erreur lors de la récupération du type de compte: {str(e)}"
        )

@router.get("/me/recordings")
async def get_my_recordings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📹 Récupère les enregistrements Zoom de l'utilisateur connecté
    """
    try:
        return ZoomService.get_user_recordings(db, current_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Impossible de récupérer les enregistrements: {str(e)}"
        )

@router.post("/import")
async def import_zoom_recording(
    recording_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🚀 Importe un enregistrement Zoom et lance la transcription + analyse
    """
    zoom_meeting_id = recording_data.get("id")
    if not zoom_meeting_id:
        raise HTTPException(status_code=400, detail="Missing Zoom meeting ID")

    # 1. Créer le meeting en base avec statut 'in_progress'
    scheduled_time = recording_data.get("start_time")
    if scheduled_time:
        scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))

    new_meeting = Meeting(
        user_id=current_user.id,
        zoom_meeting_id=str(zoom_meeting_id),
        title=recording_data.get("topic", "Réunion Zoom"),
        scheduled_time=scheduled_time,
        duration_minutes=recording_data.get("duration", 0),
        status=MeetingStatus.IN_PROGRESS
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    # 2. Lancer la tâche de fond
    background_tasks.add_task(
        process_zoom_import, 
        new_meeting.id, 
        str(zoom_meeting_id), 
        current_user.id
    )

    return {
        "status": "processing",
        "meeting_id": new_meeting.id,
        "message": "La transcription et l'analyse IA ont été lancées en arrière-plan."
    }

async def process_hybrid_import(meeting_id: int, zoom_meeting_id: str, file_path: str, user_id: int):
    """
    Tâche de fond pour traiter l'upload hybride (Fichier manuel + Meta Zoom)
    """
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            print(f"User {user_id} not found")
            return

        # 1. Récupérer les participants Zoom
        participants = ZoomService.get_meeting_participants(db, user, zoom_meeting_id)
        participant_names = [f"{p.get('user_name')} ({p.get('user_email')})" for p in participants]

        # 2. Transcrire (le SDK gère l'upload automatiquement)
        transcriber = TranscriptionService()
        result = transcriber.transcribe_file(file_path)
        
        # 3. Enregistrer transcription
        db_transcription = Transcription(
            meeting_id=meeting_id,
            full_text=result["full_text"],
            speaker_segments=result["speaker_segments"]
        )
        db.add(db_transcription)
        
        # 5. On s'arrête là pour laisser l'utilisateur lancer l'analyse manuellement
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            meeting.status = MeetingStatus.COMPLETED
            
        db.commit()
    except Exception as e:
        print(f"Error in hybrid process: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        db.close()

@router.post("/upload-hybrid")
async def upload_zoom_audio(
    background_tasks: BackgroundTasks,
    zoom_id: str = Form(...),
    topic: str = Form(...),
    start_time: str = Form(...),
    duration: int = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📬 Reçoit le fichier audio manuel et les métadonnées Zoom.
    Gère intelligemment les doublons.
    """
    # 1. Sauvegarder le fichier temporairement
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"upload_{zoom_id}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Vérifier si le meeting existe déjà pour cet utilisateur
    existing_meeting = db.query(Meeting).filter(
        Meeting.zoom_meeting_id == zoom_id,
        Meeting.user_id == current_user.id
    ).first()

    try:
        scheduled_at = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    except:
        scheduled_at = datetime.utcnow()

    if existing_meeting:
        # On met à jour le meeting existant
        existing_meeting.title = topic
        existing_meeting.scheduled_time = scheduled_at
        existing_meeting.duration_minutes = duration
        existing_meeting.status = MeetingStatus.IN_PROGRESS
        # Supprimer l'ancienne transcription/résumé si on veut tout refaire
        if existing_meeting.transcription:
            db.delete(existing_meeting.transcription)
        if existing_meeting.summary:
            db.delete(existing_meeting.summary)
        
        meeting_id = existing_meeting.id
        db.commit()
    else:
        # On crée un nouveau meeting
        new_meeting = Meeting(
            user_id=current_user.id,
            zoom_meeting_id=zoom_id,
            title=topic,
            scheduled_time=scheduled_at,
            duration_minutes=duration,
            status=MeetingStatus.IN_PROGRESS
        )
        db.add(new_meeting)
        db.commit()
        db.refresh(new_meeting)
        meeting_id = new_meeting.id

    # 3. Task de fond
    background_tasks.add_task(
        process_hybrid_import,
        meeting_id,
        zoom_id,
        file_path,
        current_user.id
    )

    return {"status": "success", "message": "Fichier reçu. Analyse en cours..."}

