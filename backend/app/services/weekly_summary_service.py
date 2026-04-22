"""
Weekly Summary Service
Generates and sends weekly digest emails to users
"""
import os
import re
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.base import SessionLocal
from ..models.user import User
from ..models.meeting import Meeting, ActionItem
from ..models.base import engine, Base
from .email_service import EmailService
from jinja2 import Environment, FileSystemLoader
import logging
import asyncio

logger = logging.getLogger(__name__)
EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class WeeklySummaryService:
    """Service to generate and send weekly summaries to users"""

    def __init__(self):
        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
    
    @staticmethod
    def get_week_range():
        """Get week range (Monday to Sunday)"""
        today = datetime.now()
        # Monday is weekday 0
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
        return start, end
    
    @staticmethod
    def format_date(date_obj: datetime, format_str: str = '%d %b %Y') -> str:
        """Format date for display"""
        if not date_obj:
            return "N/A"
        return date_obj.strftime(format_str)
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in human readable format"""
        if not seconds:
            return "0m"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        
        if hours > 0:
            if minutes > 0:
                return f"{hours}h {minutes}m"
            return f"{hours}h"
        return f"{minutes}m"

    @staticmethod
    def _extract_concerned_emails(owner: User, meetings: list, open_actions: list, completed_actions: list) -> list[str]:
        """Build recipient list: owner + participants + assignees that look like emails."""
        recipients = set()

        if owner and owner.email and EMAIL_REGEX.match(owner.email):
            recipients.add(owner.email.strip().lower())

        for meeting in meetings:
            participants = getattr(meeting, "participants", None)
            if not participants:
                continue

            # Supports participant formats: dict with email, plain email string, or mixed lists.
            if isinstance(participants, list):
                for participant in participants:
                    email_candidate = None
                    if isinstance(participant, dict):
                        email_candidate = participant.get("email")
                    elif isinstance(participant, str):
                        email_candidate = participant

                    if email_candidate:
                        email_candidate = email_candidate.strip().lower()
                        if EMAIL_REGEX.match(email_candidate):
                            recipients.add(email_candidate)

        for action in [*open_actions, *completed_actions]:
            assigned_to = getattr(action, "assigned_to", None)
            if assigned_to and isinstance(assigned_to, str):
                assigned_to = assigned_to.strip().lower()
                if EMAIL_REGEX.match(assigned_to):
                    recipients.add(assigned_to)

        return sorted(recipients)

    def get_user_weekly_summary(self, db: Session, user_id: int):
        """
        Get weekly summary data for a user
        Returns meetings and action items from the past 7 days
        """
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)

        # Get meetings from past week
        meetings = db.query(Meeting).filter(
            Meeting.user_id == user_id,
            Meeting.created_at >= week_ago,
            Meeting.created_at <= now
        ).order_by(Meeting.created_at.desc()).all()

        # Get open action items
        open_actions = db.query(ActionItem).join(
            Meeting, ActionItem.meeting_id == Meeting.id
        ).filter(
            Meeting.user_id == user_id,
            ActionItem.status != "completed"
        ).order_by(ActionItem.due_date).all()

        # Get completed action items from past week
        completed_actions = db.query(ActionItem).join(
            Meeting, ActionItem.meeting_id == Meeting.id
        ).filter(
            Meeting.user_id == user_id,
            ActionItem.status == "completed",
            ActionItem.updated_at >= week_ago
        ).all()

        return {
            "meetings": meetings,
            "open_actions": open_actions,
            "completed_actions": completed_actions,
            "period_start": week_ago,
            "period_end": now,
        }

    def generate_html_email(self, summary_data: dict) -> str:
        """
        Generate HTML email content using Jinja2 template
        """
        try:
            template = self.jinja_env.get_template('weekly_summary_email.html')
            
            user = summary_data.get('user')
            user_first_name = user.first_name if hasattr(user, 'first_name') and user.first_name else 'User'
            
            week_start, week_end = self.get_week_range()
            
            meetings = summary_data.get('meetings', [])
            open_actions = summary_data.get('open_actions', [])
            completed_actions = summary_data.get('completed_actions', [])
            stats = summary_data.get('stats', {})
            
            # Format meetings for template
            formatted_meetings = []
            for meeting in meetings:
                formatted_meetings.append({
                    'title': meeting.title if hasattr(meeting, 'title') else 'Unknown',
                    'date': self.format_date(meeting.created_at if hasattr(meeting, 'created_at') else datetime.now(), '%d %b %Y'),
                    'duration': self.format_duration(meeting.duration_seconds if hasattr(meeting, 'duration_seconds') else 0),
                    'participants': getattr(meeting, 'participants', 'N/A'),
                    'summary': (meeting.summary if hasattr(meeting, 'summary') and meeting.summary else 'No summary available')[:200],
                })
            
            # Format action items
            formatted_open_actions = []
            for action in open_actions:
                formatted_open_actions.append({
                    'description': action.description if hasattr(action, 'description') else 'Unknown action',
                    'assignee': action.assignee if hasattr(action, 'assignee') else None,
                    'meeting': getattr(action, 'meeting_title', 'Unknown meeting'),
                    'due_date': self.format_date(action.due_date if hasattr(action, 'due_date') else None, '%d %b %Y') if hasattr(action, 'due_date') and action.due_date else None,
                    'is_overdue': (action.due_date < datetime.now() if hasattr(action, 'due_date') and action.due_date else False),
                })
            
            formatted_completed_actions = []
            for action in completed_actions:
                formatted_completed_actions.append({
                    'description': action.description if hasattr(action, 'description') else 'Unknown action',
                    'completed_date': self.format_date(action.updated_at if hasattr(action, 'updated_at') else datetime.now(), '%d %b %Y'),
                })
            
            # Render template
            html = template.render(
                user_first_name=user_first_name,
                user_email=user.email if hasattr(user, 'email') else 'user@example.com',
                week_start=self.format_date(week_start, '%d %b %Y'),
                week_end=self.format_date(week_end, '%d %b %Y'),
                meetings=formatted_meetings,
                open_actions=formatted_open_actions,
                completed_actions=formatted_completed_actions,
                stats=stats,
                dashboard_url=f"{os.getenv('FRONTEND_URL', 'https://syntra.ai')}/dashboard",
                settings_url=f"{os.getenv('FRONTEND_URL', 'https://syntra.ai')}/settings",
                unsubscribe_url=f"{os.getenv('FRONTEND_URL', 'https://syntra.ai')}/unsubscribe",
                current_year=datetime.now().year,
            )
            
            return html
        except Exception as e:
            logger.error(f"Error generating HTML email: {e}")
            raise

    async def send_weekly_summary_email(self, user_id: int, db: Session = None):
        """
        Send weekly summary email to a user
        """
        if db is None:
            db = SessionLocal()

        try:
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user or not user.email:
                logger.info(f"User {user_id} not found or has no email")
                return False

            # Get summary data
            summary_data = self.get_user_weekly_summary(db, user_id)

            # Skip if no activity
            if not summary_data["meetings"] and not summary_data["open_actions"]:
                logger.info(f"No activity for user {user_id}, skipping email")
                return True

            # Generate HTML
            html_content = self.generate_html_email({
                'user': user,
                'meetings': summary_data['meetings'],
                'open_actions': summary_data['open_actions'],
                'completed_actions': summary_data['completed_actions'],
                'stats': {
                    'total_meetings': len(summary_data['meetings']),
                    'total_actions': len(summary_data['open_actions']) + len(summary_data['completed_actions']),
                    'completed_actions': len(summary_data['completed_actions']),
                    'pending_actions': len(summary_data['open_actions']),
                }
            })

            recipients = self._extract_concerned_emails(
                owner=user,
                meetings=summary_data["meetings"],
                open_actions=summary_data["open_actions"],
                completed_actions=summary_data["completed_actions"],
            )

            if not recipients:
                logger.info(f"No concerned recipients found for user {user_id}, skipping email")
                return True

            subject = f"📊 Weekly Summary - {datetime.utcnow().strftime('%d %b %Y')}"
            success_count = 0
            for recipient_email in recipients:
                sent = EmailService.send_email(
                    recipient_email=recipient_email,
                    subject=subject,
                    html_content=html_content,
                )
                if sent:
                    success_count += 1

            if success_count == len(recipients):
                logger.info(f"Weekly summary sent to {len(recipients)} recipient(s): {', '.join(recipients)}")
                return True

            logger.error(
                f"Weekly summary partial failure for user {user_id}: sent {success_count}/{len(recipients)}"
            )
            return False

        except Exception as e:
            logger.error(f"Error sending weekly summary email to {user_id}: {e}")
            return False
        finally:
            db.close()

    def send_to_all_users(self):
        """
        Send weekly summary emails to all users who have activity
        """
        db = SessionLocal()
        try:
            users = db.query(User).filter(User.is_active == True).all()
            sent_count = 0
            failed_count = 0

            for user in users:
                # Check if user has activities
                summary_data = self.get_user_weekly_summary(db, user.id)
                if summary_data["meetings"] or summary_data["open_actions"]:
                    try:
                        result = asyncio.run(self.send_weekly_summary_email(user.id, db))
                        if result:
                            sent_count += 1
                        else:
                            failed_count += 1
                    except Exception as e:
                        logger.error(f"Error sending to user {user.id}: {e}")
                        failed_count += 1

            logger.info(f"Weekly summary emails sent to {sent_count} users (failed: {failed_count})")
            return {
                'sent': sent_count,
                'failed': failed_count,
                'total': sent_count + failed_count
            }

        finally:
            db.close()
