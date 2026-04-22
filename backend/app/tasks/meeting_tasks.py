import asyncio
import os
from .celery_app import celery_app
from ..agents.orchestrator import MeetingIntelligenceOrchestrator
from ..models.base import SessionLocal
from ..models.meeting import Meeting, Transcription, Summary, ActionItem, MeetingStatus
from ..services.zoom_service import ZoomService
from ..services.transcription_service import TranscriptionService
from langchain_openai import ChatOpenAI

@celery_app.task
def process_zoom_meeting_recording(meeting_id: int):
    """
    Task to download, transcribe and analyze a Zoom meeting recording.
    """
    db = SessionLocal()
    try:
        meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
        if not meeting:
            print(f"Meeting {meeting_id} not found.")
            return

        user = meeting.user
        if not user:
            print(f"User not found for meeting {meeting_id}.")
            return

        # 1. Get Download URL
        print(f"Fetching download URL for meeting {meeting.zoom_meeting_id}...")
        download_url = ZoomService.get_audio_download_url(db, user, meeting.zoom_meeting_id)
        
        if not download_url:
            print(f"No audio download URL found for meeting {meeting_id}.")
            return

        # 2. Transcribe
        print(f"Starting transcription for meeting {meeting_id} from URL...")
        transcription_service = TranscriptionService()
        # Direct URL transcription (assuming AssemblyAI can access the signed URL)
        result = transcription_service.transcribe_audio_url(download_url)
        
        # 3. Save Transcription
        transcription = Transcription(
            meeting_id=meeting_id,
            full_text=result["full_text"],
            speaker_segments=result["speaker_segments"]
        )
        db.add(transcription)
        meeting.status = MeetingStatus.COMPLETED
        db.commit() # Commit to get transcription ID and update state
        db.refresh(meeting)
        
        print(f"Transcription saved for meeting {meeting_id}. Starting analysis...")

        # 4. Analyze (Meeting Intelligence)
        process_meeting_analysis_internal(meeting.id, db)

    except Exception as e:
        print(f"Error processing Zoom meeting {meeting_id}: {str(e)}")
        # Optionally update meeting status to FAILED
    finally:
        db.close()

def process_meeting_analysis_internal(meeting_id: int, db):
    """
    Internal function to run analysis synchronously (called by task).
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting or not meeting.transcription:
        return

    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL")
    )
    
    orchestrator = MeetingIntelligenceOrchestrator(llm)
    
    # Run async analysis in sync context
    try:
        # Create a new event loop for this thread if needed, or use asyncio.run
        results = asyncio.run(orchestrator.process_meeting(
            transcription=meeting.transcription.full_text,
            metadata={
                "title": meeting.title,
                "duration": meeting.duration_minutes
            }
        ))
        
        # Save Summary
        summary = Summary(
            meeting_id=meeting_id,
            executive_summary=results["summary"]["executive_summary"],
            decisions=results["decisions"],
            questions=results["questions"],
            full_markdown=results["summary"]["full_markdown"]
        )
        db.add(summary)
        
        # Save Actions
        for action_in in results["actions"]["items"]: # Assuming structure
            action = ActionItem(
                meeting_id=meeting_id,
                description=action_in.get("action", action_in.get("description", "")),
                assigned_to=action_in.get("assigned_to"),
                deadline=action_in.get("deadline"),
                priority=action_in.get("priority"),
                status="pending"
            )
            db.add(action)
            
        db.commit()
        print(f"Analysis completed for meeting {meeting_id}.")
        
    except Exception as e:
        print(f"Analysis failed for meeting {meeting_id}: {str(e)}")
        db.rollback()

@celery_app.task
def process_meeting_intelligence(meeting_id: int):
    """
    Standalone task for re-analyzing an existing transcription.
    """
    db = SessionLocal()
    try:
        process_meeting_analysis_internal(meeting_id, db)
    finally:
        db.close()


@celery_app.task
def send_weekly_summary_emails():
    """
    Celery Beat task to send weekly summary emails every Monday at 9 AM.
    Scheduled via Celery Beat configuration.
    """
    from ..services.weekly_summary_service import WeeklySummaryService
    
    print("Starting weekly summary email dispatch...")
    service = WeeklySummaryService()
    count = service.send_to_all_users()
    print(f"Weekly summary dispatch completed. Emails sent: {count}")
    return {"status": "completed", "emails_sent": count}