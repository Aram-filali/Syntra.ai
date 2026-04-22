from celery import Celery
from celery.schedules import crontab
import os

celery_app = Celery(
    "meeting_intelligence",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0")
)

celery_app.conf.task_routes = {
    "app.tasks.meeting_tasks.*": {"queue": "meetings"}
}

# Configure Celery Beat Schedule
celery_app.conf.beat_schedule = {
    'send-weekly-summary-emails': {
        'task': 'app.tasks.meeting_tasks.send_weekly_summary_emails',
        # Run every Monday at 9 AM UTC
        'schedule': crontab(hour=9, minute=0, day_of_week=1),
    },
}