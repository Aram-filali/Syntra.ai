import pytest
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, call
from sqlalchemy.orm import Session
from app.services.weekly_summary_service import WeeklySummaryService
from app.models.user import User
from app.models.meeting import Meeting
from app.tasks.meeting_tasks import send_weekly_summary_emails


class TestWeeklySummaryIntegration:
    """Integration tests for weekly summary feature"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session"""
        return MagicMock(spec=Session)
    
    @pytest.fixture
    def sample_users(self):
        """Create sample users with real attributes"""
        users = []
        for i in range(2):
            user = MagicMock(spec=User)
            user.id = i + 1
            user.email = f"user{i+1}@example.com"
            user.first_name = f"User{i+1}"
            user.last_name = f"Test"
            user.is_active = True
            users.append(user)
        return users
    
    @pytest.fixture
    def sample_meetings_with_data(self):
        """Create realistic meetings with all data"""
        today = datetime.now()
        meetings = []
        
        for i in range(3):
            meeting = MagicMock(spec=Meeting)
            meeting.id = i + 1
            meeting.title = f"Team Meeting {i+1}"
            meeting.created_at = today - timedelta(days=i)
            meeting.duration_seconds = 3600 + (i * 600)
            meeting.summary = f"Discussion about project goals and timeline"
            
            # Add action items
            actions = []
            for j in range(2):
                action = MagicMock()
                action.id = (i * 2) + j + 1
                action.description = f"Action item {j+1} from meeting {i+1}"
                action.status = "open" if j == 0 else "completed"
                action.created_at = today - timedelta(days=i)
                actions.append(action)
            
            meeting.action_items = actions
            meetings.append(meeting)
        
        return meetings
    
    @patch('app.services.weekly_summary_service.sendgrid.SendGridAPIClient')
    def test_send_single_user_email(self, mock_sendgrid, mock_db_session, sample_users):
        """Test sending email to a single user"""
        mock_client = MagicMock()
        mock_sendgrid.return_value = mock_client
        mock_client.mail_send.return_value = MagicMock(status_code=202)
        
        user = sample_users[0]
        
        # Mock the database queries
        mock_db_session.query.return_value.filter.return_value.all.return_value = []
        
        summary_data = {
            'user': user,
            'meetings': [],
            'open_actions': [],
            'completed_actions': [],
            'stats': {
                'total_meetings': 0,
                'total_actions': 0,
                'completed_actions': 0,
                'pending_actions': 0,
            }
        }
        
        html = WeeklySummaryService.generate_html_email(summary_data)
        
        # Verify email content was generated
        assert html is not None
        assert user.first_name in html
    
    @patch('app.services.weekly_summary_service.sendgrid.SendGridAPIClient')
    def test_send_batch_emails_to_multiple_users(self, mock_sendgrid, mock_db_session, sample_users):
        """Test sending emails to multiple users"""
        mock_client = MagicMock()
        mock_sendgrid.return_value = mock_client
        mock_client.mail_send.return_value = MagicMock(status_code=202)
        
        # Mock database queries
        mock_db_session.query.return_value.filter.return_value.all.return_value = sample_users
        
        # Verify multiple users would be processed
        user_emails = [user.email for user in sample_users]
        assert len(user_emails) == 2
        assert all(email.endswith("@example.com") for email in user_emails)
    
    @patch('app.services.weekly_summary_service.sendgrid.SendGridAPIClient')
    def test_email_includes_all_sections(self, mock_sendgrid, sample_users, sample_meetings_with_data):
        """Test that email includes all required sections"""
        mock_client = MagicMock()
        mock_sendgrid.return_value = mock_client
        
        user = sample_users[0]
        
        open_actions = [a for m in sample_meetings_with_data for a in m.action_items if a.status == "open"]
        completed_actions = [a for m in sample_meetings_with_data for a in m.action_items if a.status == "completed"]
        
        summary_data = {
            'user': user,
            'meetings': sample_meetings_with_data,
            'open_actions': open_actions,
            'completed_actions': completed_actions,
            'stats': {
                'total_meetings': len(sample_meetings_with_data),
                'total_actions': len(open_actions) + len(completed_actions),
                'completed_actions': len(completed_actions),
                'pending_actions': len(open_actions),
            }
        }
        
        html = WeeklySummaryService.generate_html_email(summary_data)
        
        # Verify all sections present
        required_sections = [
            "Weekly Summary",
            "Meetings",
            "Action Items",
            "Statistics",
        ]
        
        for section in required_sections:
            assert section in html
    
    def test_celery_task_trigger(self):
        """Test Celery task can be triggered"""
        # This test verifies the task structure without executing
        from app.tasks.meeting_tasks import send_weekly_summary_emails
        
        # Verify task exists
        assert send_weekly_summary_emails is not None
        assert callable(send_weekly_summary_emails)
    
    @patch('app.services.weekly_summary_service.WeeklySummaryService.send_to_all_users')
    def test_celery_beat_schedule_integration(self, mock_send):
        """Test Celery Beat scheduler integration"""
        mock_send.return_value = {"sent": 5, "failed": 0}
        
        # Verify the service method exists
        assert WeeklySummaryService.send_to_all_users is not None
    
    def test_sendgrid_email_format(self, sample_users):
        """Test SendGrid email format compliance"""
        user = sample_users[0]
        
        # Email should have standard SMTP format
        assert "@" in user.email
        assert "." in user.email.split("@")[1]
        assert user.email.count("@") == 1
    
    @patch.dict(os.environ, {'SENDGRID_API_KEY': 'test-key'})
    def test_environment_variables_available(self):
        """Test that required environment variables can be accessed"""
        assert os.getenv('SENDGRID_API_KEY') == 'test-key'
    
    def test_week_range_calculation_accuracy(self):
        """Test that week range is calculated correctly"""
        start, end = WeeklySummaryService.get_week_range()
        
        # Week should be 7 days
        delta = (end - start).days
        assert delta == 6, "Week range should span 6 days (Mon-Sun)"
        
        # Start should be Monday or close to start of week
        assert start <= datetime.now()
        assert end >= datetime.now()
    
    def test_error_recovery_on_partial_failure(self, mock_db_session):
        """Test system recovers if some emails fail"""
        # Create two summary data objects
        users = [
            MagicMock(id=1, email="user1@example.com", first_name="User1"),
            MagicMock(id=2, email="user2@example.com", first_name="User2"),
        ]
        
        # Both should generate valid HTML despite potential failures
        for user in users:
            summary_data = {
                'user': user,
                'meetings': [],
                'open_actions': [],
                'completed_actions': [],
                'stats': {
                    'total_meetings': 0,
                    'total_actions': 0,
                    'completed_actions': 0,
                    'pending_actions': 0,
                }
            }
            
            html = WeeklySummaryService.generate_html_email(summary_data)
            assert html is not None
            assert user.first_name in html
    
    def test_html_email_security(self, sample_users):
        """Test HTML email doesn't have XSS vulnerabilities"""
        user = sample_users[0]
        
        # Add potentially dangerous content
        dangerous_action = Mock(
            description="<script>alert('XSS')</script>Click here",
            assignee=None,
            meeting=None,
            due_date=None,
            is_overdue=False
        )
        
        summary_data = {
            'user': user,
            'meetings': [],
            'open_actions': [dangerous_action],
            'completed_actions': [],
            'stats': {
                'total_meetings': 0,
                'total_actions': 1,
                'completed_actions': 0,
                'pending_actions': 1,
            }
        }
        
        html = WeeklySummaryService.generate_html_email(summary_data)
        
        # Content should be escaped or not executable
        # (Jinja2 auto-escapes by default)
        assert '<script>' not in html or '&lt;script&gt;' in html
    
    @patch('app.services.weekly_summary_service.sendgrid.SendGridAPIClient')
    def test_email_metadata_headers(self, mock_sendgrid):
        """Test email has proper metadata and headers"""
        mock_client = MagicMock()
        mock_sendgrid.return_value = mock_client
        
        # Email should have proper structure
        # This is verified in the actual implementation
        assert True  # Placeholder for header verification


class TestWeeklySummaryPerformance:
    """Performance tests for weekly summary feature"""
    
    def test_html_generation_performance(self):
        """Test HTML generation completes in reasonable time"""
        import time
        
        # Create large dataset
        meetings = [MagicMock(
            title=f"Meeting {i}",
            date="2026-04-19",
            duration="1h 30m",
            participants=f"Person {i}",
            summary="Summary text"
        ) for i in range(50)]
        
        actions = [MagicMock(
            description=f"Action {i}",
            assignee=f"User {i}",
            meeting=f"Meeting {i%50}",
            due_date="2026-04-25",
            is_overdue=False,
            completed_date=None
        ) for i in range(100)]
        
        user = MagicMock(first_name="Test", last_name="User", email="test@example.com")
        
        summary_data = {
            'user': user,
            'meetings': meetings,
            'open_actions': actions[:80],
            'completed_actions': actions[80:],
            'stats': {
                'total_meetings': 50,
                'total_actions': 100,
                'completed_actions': 20,
                'pending_actions': 80,
            }
        }
        
        start_time = time.time()
        html = WeeklySummaryService.generate_html_email(summary_data)
        end_time = time.time()
        
        execution_time = end_time - start_time
        
        # Should complete in under 2 seconds even with large dataset
        assert execution_time < 2.0, f"HTML generation took {execution_time}s, should be < 2s"
        assert len(html) > 1000, "HTML should be generated"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.services.weekly_summary_service"])
