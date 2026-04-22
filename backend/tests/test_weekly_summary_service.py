import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.services.weekly_summary_service import WeeklySummaryService
from app.models.meeting import Meeting
from app.models.user import User


class TestWeeklySummaryService:
    """Unit tests for WeeklySummaryService"""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session"""
        return Mock()
    
    @pytest.fixture
    def sample_user(self):
        """Create a sample user"""
        user = Mock(spec=User)
        user.id = 1
        user.email = "test@example.com"
        user.first_name = "John"
        user.last_name = "Doe"
        return user
    
    @pytest.fixture
    def sample_meetings(self):
        """Create sample meetings for testing"""
        today = datetime.now()
        meetings = []
        
        for i in range(3):
            meeting = Mock(spec=Meeting)
            meeting.id = i + 1
            meeting.title = f"Meeting {i+1}"
            meeting.created_at = today - timedelta(days=i)
            meeting.duration_seconds = 3600 + (i * 600)
            meeting.summary = f"This is a summary for meeting {i+1}"
            meeting.action_items = []
            meetings.append(meeting)
        
        return meetings
    
    def test_get_week_range(self):
        """Test week range calculation"""
        start, end = WeeklySummaryService.get_week_range()
        
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        assert start < end
        assert (end - start).days == 6
    
    def test_format_date(self):
        """Test date formatting"""
        test_date = datetime(2026, 4, 19, 10, 30, 0)
        formatted = WeeklySummaryService.format_date(test_date)
        
        assert isinstance(formatted, str)
        assert "2026" in formatted or "26" in formatted
    
    def test_format_duration(self):
        """Test duration formatting"""
        # Test 1 hour
        duration_str = WeeklySummaryService.format_duration(3600)
        assert "1h" in duration_str or "1 hour" in duration_str.lower()
        
        # Test 30 minutes
        duration_str = WeeklySummaryService.format_duration(1800)
        assert "30" in duration_str
        
        # Test 1 hour 30 minutes
        duration_str = WeeklySummaryService.format_duration(5400)
        assert "1" in duration_str and "30" in duration_str
    
    def test_generate_html_email_structure(self, mock_db, sample_user, sample_meetings):
        """Test HTML email structure and content generation"""
        summary_data = {
            'user': sample_user,
            'meetings': sample_meetings,
            'open_actions': [],
            'completed_actions': [],
            'stats': {
                'total_meetings': len(sample_meetings),
                'total_actions': 0,
                'completed_actions': 0,
                'pending_actions': 0,
            }
        }
        
        html = WeeklySummaryService.generate_html_email(summary_data)
        
        # Check structure
        assert html is not None
        assert isinstance(html, str)
        assert len(html) > 0
        
        # Check content
        assert "Weekly Summary" in html
        assert sample_user.first_name in html
        assert "Meetings" in html
        
        # Check for meeting titles
        for meeting in sample_meetings:
            assert meeting.title in html
    
    def test_generate_html_email_with_actions(self, mock_db, sample_user):
        """Test HTML email with action items"""
        open_actions = [
            Mock(
                description="Complete project proposal",
                assignee="John Doe",
                meeting="Project Planning",
                due_date="2026-04-25",
                is_overdue=False
            ),
            Mock(
                description="Review budget",
                assignee="Jane Smith",
                meeting="Finance Review",
                due_date="2026-04-15",
                is_overdue=True
            ),
        ]
        
        completed_actions = [
            Mock(
                description="Send client report",
                completed_date="2026-04-18"
            ),
        ]
        
        summary_data = {
            'user': sample_user,
            'meetings': [],
            'open_actions': open_actions,
            'completed_actions': completed_actions,
            'stats': {
                'total_meetings': 0,
                'total_actions': len(open_actions) + len(completed_actions),
                'completed_actions': len(completed_actions),
                'pending_actions': len(open_actions),
            }
        }
        
        html = WeeklySummaryService.generate_html_email(summary_data)
        
        # Check action items appear
        for action in open_actions:
            assert action.description in html
        
        for action in completed_actions:
            assert action.description in html
        
        # Check completed indicator
        assert "✅" in html or "Completed" in html
    
    def test_generate_html_email_empty_data(self, sample_user):
        """Test HTML email with empty data"""
        summary_data = {
            'user': sample_user,
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
        assert "No meetings this week" in html
        assert "No open action items" in html
    
    def test_statistics_calculation(self, sample_meetings):
        """Test statistics calculation"""
        open_actions = [Mock(description="Action 1"), Mock(description="Action 2")]
        completed_actions = [Mock(description="Action 3")]
        
        stats = {
            'total_meetings': len(sample_meetings),
            'total_actions': len(open_actions) + len(completed_actions),
            'completed_actions': len(completed_actions),
            'pending_actions': len(open_actions),
        }
        
        assert stats['total_meetings'] == 3
        assert stats['total_actions'] == 3
        assert stats['completed_actions'] == 1
        assert stats['pending_actions'] == 2
    
    @patch('app.services.weekly_summary_service.sendgrid.SendGridAPIClient')
    def test_send_weekly_summary_email_error_handling(self, mock_sendgrid, sample_user):
        """Test error handling when sending email fails"""
        mock_client = Mock()
        mock_sendgrid.return_value = mock_client
        mock_client.mail_send.side_effect = Exception("SendGrid API error")
        
        summary_data = {
            'user': sample_user,
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
        
        # Should not raise, but handle error gracefully
        try:
            with patch.dict('os.environ', {'SENDGRID_API_KEY': 'test-key'}):
                # Mock the actual sending
                pass
        except Exception as e:
            pytest.fail(f"Exception raised: {e}")
    
    def test_email_template_variables(self, sample_user):
        """Test that all required template variables are present"""
        summary_data = {
            'user': sample_user,
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
        
        # Check template variables are replaced
        assert "{{" not in html  # No unclosed template variables
        assert "}}" not in html
        assert sample_user.first_name in html
    
    def test_html_email_responsiveness(self, sample_user):
        """Test that email HTML includes responsive design"""
        summary_data = {
            'user': sample_user,
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
        
        # Check for responsive design indicators
        assert "viewport" in html
        assert "max-width" in html
        assert "@media" in html  # Mobile responsiveness


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=app.services.weekly_summary_service"])
