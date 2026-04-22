from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import os
import shutil
import tempfile

from ..models.base import get_db, SessionLocal
from ..models.user import User
from ..models.meeting import Meeting, Transcription, Summary, ActionItem, MeetingStatus
from ..services.transcription_service import TranscriptionService
from ..services.email_service import EmailService
from ..utils.dependencies import get_current_user
from ..agents.orchestrator import MeetingIntelligenceOrchestrator
from langchain_openai import ChatOpenAI

router = APIRouter()

# --- Background Task ---

async def process_meeting_file_upload(meeting_id: int, file_path: str, user_id: int):
    """
    Tâche de fond pour transcrire un fichier uploadé manuellement.
    """
    db = SessionLocal()
    try:
        # 1. Transcrire le fichier
        transcriber = TranscriptionService()
        result = transcriber.transcribe_file(file_path)
        
        # 2. Enregistrer la transcription
        db_transcription = Transcription(
            meeting_id=meeting_id,
            full_text=result["full_text"],
            speaker_segments=result["speaker_segments"]
        )
        db.add(db_transcription)
        
        # 3. Mettre à jour le statut du meeting
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if meeting:
            meeting.status = MeetingStatus.COMPLETED
            
        db.commit()
    except Exception as e:
        print(f"Error in background transcription: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
        db.close()

# Schemas
class MeetingCreate(BaseModel):
    title: str
    scheduled_time: datetime
    duration_minutes: int
    zoom_meeting_id: Optional[str] = None

class TranscriptionCreate(BaseModel):
    full_text: str
    speaker_segments: Optional[dict] = None

class ActionStatusUpdate(BaseModel):
    status: str

class ActionItemUpdate(BaseModel):
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None

class ShareMeeting(BaseModel):
    recipient_emails: List[str]
    message: Optional[str] = None

class MeetingUpdate(BaseModel):
    participants: Optional[List[dict]] = None
    title: Optional[str] = None

# --- Routes ---

@router.post("/", status_code=201)
def create_meeting(
    meeting: MeetingCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau meeting pour l'utilisateur connecté"""
    new_meeting = Meeting(
        title=meeting.title,
        scheduled_time=meeting.scheduled_time,
        duration_minutes=meeting.duration_minutes,
        zoom_meeting_id=meeting.zoom_meeting_id,
        user_id=current_user.id,
        status=MeetingStatus.SCHEDULED
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)
    
    return {
        "id": new_meeting.id,
        "title": new_meeting.title,
        "status": new_meeting.status.value,
        "scheduled_time": new_meeting.scheduled_time,
        "created_at": new_meeting.created_at
    }

@router.post("/upload")
async def create_meeting_with_file(
    background_tasks: BackgroundTasks,
    title: str = Form(...),
    scheduled_time: Optional[str] = Form(None),
    duration_minutes: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un nouveau meeting avec upload de fichier audio/vidéo"""
    
    # 1. Sauvegarder le fichier temporairement
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, f"manual_upload_{datetime.now().timestamp()}_{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Créer le meeting en base
    try:
        if scheduled_time:
            scheduled_at = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        else:
            scheduled_at = datetime.utcnow()
    except Exception:
        scheduled_at = datetime.utcnow()

    new_meeting = Meeting(
        title=title,
        scheduled_time=scheduled_at,
        duration_minutes=duration_minutes,
        user_id=current_user.id,
        status=MeetingStatus.IN_PROGRESS
    )
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)

    # 3. Lancer la transcription en arrière-plan
    background_tasks.add_task(
        process_meeting_file_upload,
        new_meeting.id,
        file_path,
        current_user.id
    )

    return {
        "id": new_meeting.id,
        "title": new_meeting.title,
        "status": new_meeting.status.value,
        "message": "Fichier reçu. La transcription a commencé en arrière-plan."
    }

@router.get("/")
def list_meetings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste uniquement les meetings de l'utilisateur connecté"""
    meetings = db.query(Meeting).filter(Meeting.user_id == current_user.id).order_by(Meeting.scheduled_time.desc()).all()
    return [
        {
            "id": m.id,
            "title": m.title,
            "status": m.status.value,
            "scheduled_time": m.scheduled_time,
            "duration_minutes": m.duration_minutes,
            "has_transcription": m.transcription is not None,
            "has_summary": m.summary is not None,
            "actions_count": len(m.action_items),
            "created_at": m.created_at
        }
        for m in meetings
    ]

@router.get("/{meeting_id}")
def get_meeting(
    meeting_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère un meeting spécifique avec vérification de propriété"""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id, 
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting non trouvé ou accès refusé")
    
    return {
        "id": meeting.id,
        "title": meeting.title,
        "status": meeting.status.value,
        "scheduled_time": meeting.scheduled_time,
        "duration_minutes": meeting.duration_minutes,
        "has_transcription": meeting.transcription is not None,
        "has_summary": meeting.summary is not None,
        "actions_count": len(meeting.action_items),
        "participants": meeting.participants or [],
        "created_at": meeting.created_at
    }

@router.get("/{meeting_id}/transcription")
def get_transcription(
    meeting_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère la transcription avec vérification de propriété"""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id, 
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting or not meeting.transcription:
        raise HTTPException(status_code=404, detail="Transcription non trouvée")
    
    return {
        "id": meeting.transcription.id,
        "meeting_id": meeting_id,
        "full_text": meeting.transcription.full_text,
        "speaker_segments": meeting.transcription.speaker_segments,
        "created_at": meeting.transcription.created_at
    }

@router.get("/{meeting_id}/summary")
def get_summary(
    meeting_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère le résumé avec vérification de propriété"""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id, 
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting or not meeting.summary:
        raise HTTPException(status_code=404, detail="Résumé non trouvé")
    
    return {
        "id": meeting.summary.id,
        "meeting_id": meeting_id,
        "executive_summary": meeting.summary.executive_summary,
        "decisions": meeting.summary.decisions,
        "questions": meeting.summary.questions,
        "full_markdown": meeting.summary.full_markdown,
        "created_at": meeting.summary.created_at
    }

@router.post("/{meeting_id}/analyze")
async def analyze_meeting(
    meeting_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Analyse manuellement un meeting avec IA"""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id, 
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting non trouvé")
    
    if not meeting.transcription:
        raise HTTPException(status_code=400, detail="Aucune transcription disponible pour l'analyse")
    
    if meeting.summary:
        raise HTTPException(status_code=400, detail="Ce meeting a déjà été analysé")

    # Initialiser l'IA
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    orchestrator = MeetingIntelligenceOrchestrator(llm)
    
    try:
        # Lancer l'analyse
        result = await orchestrator.process_meeting(
            transcription=meeting.transcription.full_text,
            metadata={
                "title": meeting.title,
                "duration": meeting.duration_minutes
            }
        )
        
        # Sauvegarder le résumé
        summary = Summary(
            meeting_id=meeting_id,
            executive_summary=result["summary"]["executive_summary"],
            decisions=result["decisions"],
            questions=result["questions"],
            full_markdown=result["summary"]["full_markdown"]
        )
        db.add(summary)
        
        # Sauvegarder les actions
        for action_data in result["actions"]["items"]:
            action = ActionItem(
                meeting_id=meeting_id,
                description=action_data["action"],
                assigned_to=action_data["assigned_to"],
                deadline=action_data["deadline"],
                priority=action_data["priority"],
                status="pending"
            )
            db.add(action)
        
        db.commit()
        return {"status": "success", "message": "Analyse terminée avec succès"}
        
    except Exception as e:
        db.rollback()
        print(f"AI Analysis Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'analyse IA : {str(e)}")

@router.delete("/{meeting_id}")
def delete_meeting(
    meeting_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprime un meeting et toutes ses données associées"""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id, 
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting non trouvé ou accès refusé")
    
    db.delete(meeting)
    db.commit()
    
    return {"status": "success", "message": "Meeting supprimé avec succès"}

# --- Actions Routes ---

@router.get("/{meeting_id}/actions")
def get_actions(
    meeting_id: int, 
    status: Optional[str] = None, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les actions d'un meeting avec vérification de propriété"""
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id, 
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting non trouvé")
    
    query = db.query(ActionItem).filter(ActionItem.meeting_id == meeting_id)
    if status:
        query = query.filter(ActionItem.status == status)
    
    actions = query.all()
    
    return [
        {
            "id": a.id,
            "description": a.description,
            "assigned_to": a.assigned_to,
            "deadline": a.deadline,
            "priority": a.priority,
            "status": a.status,
            "created_at": a.created_at
        }
        for a in actions
    ]

@router.patch("/actions/{action_id}")
def update_action_item(
    action_id: int, 
    update_data: ActionItemUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mettre à jour un action item (status, priority, assigned_to, due_date)
    """
    action = db.query(ActionItem).join(Meeting).filter(
        ActionItem.id == action_id,
        Meeting.user_id == current_user.id
    ).first()
    
    if not action:
        raise HTTPException(status_code=404, detail="Action non trouvée")
    
    # Mettre à jour les champs fournis
    if update_data.status is not None:
        action.status = update_data.status
    if update_data.priority is not None:
        action.priority = update_data.priority
    if update_data.assigned_to is not None:
        action.assigned_to = update_data.assigned_to
    if update_data.due_date is not None:
        action.due_date = update_data.due_date
    if update_data.description is not None:
        action.description = update_data.description
    
    action.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "id": action_id,
        "description": action.description,
        "status": action.status,
        "priority": action.priority,
        "assigned_to": action.assigned_to,
        "due_date": action.due_date,
        "updated_at": action.updated_at
    }

@router.get("/search/global")
def search_meetings(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    🔍 Recherche globale dans les meetings de l'utilisateur
    Cherche dans: titres, transcriptions complètes, summaries, et action items
    """
    if not q or len(q.strip()) < 2:
        raise HTTPException(status_code=400, detail="Requête trop courte (minimum 2 caractères)")
    
    search_term = f"%{q.lower()}%"
    
    # Query pour les meetings correspondant à la recherche
    # Cherche dans title ET transcription ET summary
    results = db.query(Meeting).filter(
        and_(
            Meeting.user_id == current_user.id,
            or_(
                Meeting.title.ilike(search_term),
                Meeting.transcription.has(Transcription.full_text.ilike(search_term)),
                Meeting.summary.has(Summary.executive_summary.ilike(search_term)),
                Meeting.summary.has(Summary.full_markdown.ilike(search_term)),
                Meeting.action_items.any(ActionItem.description.ilike(search_term))
            )
        )
    ).order_by(Meeting.created_at.desc()).all()
    
    # Formater les résultats avec info additionnelle
    formatted_results = []
    for meeting in results:
        # Vérifier quels champs correspondent à la recherche
        match_fields = []
        
        if meeting.title.lower().find(q.lower()) != -1:
            match_fields.append("title")
        
        if meeting.transcription and meeting.transcription.full_text.lower().find(q.lower()) != -1:
            match_fields.append("transcription")
        
        if meeting.summary:
            if meeting.summary.executive_summary.lower().find(q.lower()) != -1:
                match_fields.append("summary")
            if meeting.summary.full_markdown.lower().find(q.lower()) != -1:
                match_fields.append("markdown")
        
        actions_matches = [a for a in meeting.action_items if q.lower() in a.description.lower()]
        if actions_matches:
            match_fields.append(f"actions ({len(actions_matches)})")
        
        formatted_results.append({
            "id": meeting.id,
            "title": meeting.title,
            "status": meeting.status.value,
            "scheduled_time": meeting.scheduled_time,
            "created_at": meeting.created_at,
            "has_transcription": meeting.transcription is not None,
            "has_summary": meeting.summary is not None,
            "actions_count": len(meeting.action_items),
            "match_fields": match_fields,
            "preview": f"Trouvé dans : {', '.join(match_fields)}"
        })
    
    return {
        "query": q,
        "total_results": len(formatted_results),
        "results": formatted_results
    }

@router.post("/{meeting_id}/share")
def share_meeting(
    meeting_id: int,
    share_data: ShareMeeting,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📧 Partage un meeting par email avec le résumé et les actions
    """
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting non trouvé")
    
    if not meeting.summary:
        raise HTTPException(status_code=400, detail="Ce meeting n'a pas de résumé pour être partagé")
    
    # Préparer les actions pour l'email
    actions = []
    if meeting.action_items:
        for action in meeting.action_items:
            actions.append({
                "description": action.description,
                "status": action.status
            })
    
    # Envoyer l'email
    success = EmailService.send_meeting_share_email(
        recipient_emails=share_data.recipient_emails,
        meeting_title=meeting.title,
        sender_name=current_user.full_name or current_user.username,
        summary_text=meeting.summary.executive_summary,
        meeting_id=meeting_id,
        actions=actions
    )
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de l'envoi de l'email. Vérifiez que SMTP est configuré."
        )
    
    return {
        "status": "success",
        "message": f"Email envoyé à {len(share_data.recipient_emails)} destinataire(s)",
        "recipients": share_data.recipient_emails
    }

@router.patch("/{meeting_id}")
def update_meeting(
    meeting_id: int,
    update_data: MeetingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    👥 Met à jour les métadonnées d'un meeting (participants, titre, etc.)
    """
    meeting = db.query(Meeting).filter(
        Meeting.id == meeting_id,
        Meeting.user_id == current_user.id
    ).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting non trouvé")
    
    # Mettre à jour les participants
    if update_data.participants is not None:
        meeting.participants = update_data.participants
    
    # Mettre à jour le titre si fourni
    if update_data.title is not None:
        meeting.title = update_data.title
    
    db.commit()
    db.refresh(meeting)
    
    return {
        "id": meeting.id,
        "title": meeting.title,
        "participants": meeting.participants,
        "status": meeting.status.value,
        "updated_at": datetime.utcnow()
    }