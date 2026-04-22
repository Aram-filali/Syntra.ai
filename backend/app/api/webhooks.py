from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
import hmac
import hashlib
import json
import os

from ..models.base import get_db
from ..models.meeting import Meeting, MeetingStatus, Transcription
from ..models.user import User
from ..tasks.meeting_tasks import process_zoom_meeting_recording

router = APIRouter()

ZOOM_WEBHOOK_SECRET = os.getenv("ZOOM_WEBHOOK_SECRET")

@router.post("/zoom")
async def zoom_webhook(
    request: Request,
    db: Session = Depends(get_db),
    x_zm_signature: str = Header(None),
    x_zm_request_timestamp: str = Header(None)
):
    """
    ⚓ Webhook Zoom pour recevoir les notifications d'enregistrements terminés
    """
    body = await request.body()
    data = json.loads(body)

    # 1. Validation de l'URL (Zoom demande une validation lors de la config)
    if data.get("event") == "endpoint.url_validation":
        plain_token = data["payload"]["plainToken"]
        mess = f"{plain_token}{ZOOM_WEBHOOK_SECRET}"
        hasher = hmac.new(ZOOM_WEBHOOK_SECRET.encode(), mess.encode(), hashlib.sha256)
        sig = hasher.hexdigest()
        return {
            "plainToken": plain_token,
            "encryptedToken": sig
        }

    # 2. Traitement des événements
    if data.get("event") == "recording.completed":
        payload = data["payload"]["object"]
        zoom_id = str(payload["id"])
        user_email = data["payload"]["object"]["host_email"]
        
        # Trouver l'utilisateur
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            print(f"User with email {user_email} not found. Ignoring webhook.")
            return {"status": "user not found"}

        # Créer ou mettre à jour la réunion
        meeting = db.query(Meeting).filter(Meeting.zoom_meeting_id == zoom_id).first()
        if not meeting:
            meeting = Meeting(
                user_id=user.id,
                zoom_meeting_id=zoom_id,
                title=payload.get("topic", "Réunion Zoom"),
                status=MeetingStatus.IN_PROGRESS,  # Marquer comme en cours de traitement
                duration_minutes=payload.get("duration", 0),
                scheduled_time=payload.get("start_time")
            )
            db.add(meeting)
            db.commit()
            db.refresh(meeting)
        else:
            # Si le meeting existait, on met à jour le statut
            meeting.status = MeetingStatus.IN_PROGRESS
            db.commit()

        # Lancer le traitement asynchrone (Téléchargement -> Transcription -> Analyse)
        process_zoom_meeting_recording.delay(meeting.id)
        
        return {"status": "processing_started"}

    return {"status": "ignored"}
