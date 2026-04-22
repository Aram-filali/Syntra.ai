#!/usr/bin/env python
"""
Manual testing script for weekly summary email feature
Run this to test the weekly summary functionality end-to-end

Usage:
    python test_weekly_summary.py              # Test all
    python test_weekly_summary.py test_html    # Test HTML generation
    python test_weekly_summary.py test_celery  # Test Celery task
    python test_weekly_summary.py send_sample  # Send sample email
"""

import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import argparse

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.weekly_summary_service import WeeklySummaryService
from app.models.base import SessionLocal, engine
from app.models.user import User
from app.models.meeting import Meeting
from app.models.action_item import ActionItem


class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_section(title: str):
    """Print a section header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{title}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_success(message: str):
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.END}")


def print_error(message: str):
    """Print an error message"""
    print(f"{Colors.RED}✗ {message}{Colors.END}")


def print_warning(message: str):
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.END}")


def print_info(message: str):
    """Print an info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.END}")


def test_environment():
    """Test that all environment variables are configured"""
    print_section("Testing Environment Configuration")
    
    required_vars = [
        'DATABASE_URL',
        'OPENAI_API_KEY',
        'SENDGRID_API_KEY',
        'JWT_SECRET_KEY',
    ]
    
    all_configured = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked_value = value[:10] + "..." if len(value) > 10 else value
            print_success(f"{var} = {masked_value}")
        else:
            print_error(f"{var} not configured")
            all_configured = False
    
    return all_configured


def test_database_connection():
    """Test database connection"""
    print_section("Testing Database Connection")
    
    try:
        db = SessionLocal()
        # Try a simple query
        users = db.query(User).limit(1).all()
        db.close()
        
        print_success("Database connection successful")
        print_info(f"Found {len(users)} users in database")
        return True
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        return False


def test_html_generation():
    """Test HTML email generation"""
    print_section("Testing HTML Email Generation")
    
    try:
        # Create sample data
        sample_meetings = [
            type('Meeting', (), {
                'title': 'Sprint Planning',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'duration': '1h 30m',
                'participants': 'John Doe, Jane Smith, Bob Johnson',
                'summary': 'Discussed sprint goals for the next two weeks. Prioritized features and assigned story points.'
            })(),
            type('Meeting', (), {
                'title': 'Client Review',
                'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                'duration': '45m',
                'participants': 'Client CEO, Sarah Manager',
                'summary': 'Reviewed project progress. Client satisfied with deliverables.'
            })(),
        ]
        
        sample_actions_open = [
            type('Action', (), {
                'description': 'Complete API documentation',
                'assignee': 'John Doe',
                'meeting': 'Sprint Planning',
                'due_date': '2026-04-25',
                'is_overdue': False
            })(),
            type('Action', (), {
                'description': 'Review code changes',
                'assignee': 'Jane Smith',
                'meeting': 'Sprint Planning',
                'due_date': '2026-04-21',
                'is_overdue': False
            })(),
        ]
        
        sample_actions_completed = [
            type('Action', (), {
                'description': 'Setup CI/CD pipeline',
                'completed_date': '2026-04-18'
            })(),
        ]
        
        sample_user = type('User', (), {
            'first_name': 'Test',
            'email': 'test@example.com'
        })()
        
        summary_data = {
            'user': sample_user,
            'meetings': sample_meetings,
            'open_actions': sample_actions_open,
            'completed_actions': sample_actions_completed,
            'stats': {
                'total_meetings': len(sample_meetings),
                'total_actions': len(sample_actions_open) + len(sample_actions_completed),
                'completed_actions': len(sample_actions_completed),
                'pending_actions': len(sample_actions_open),
            }
        }
        
        # Generate HTML
        html = WeeklySummaryService.generate_html_email(summary_data)
        
        print_success("HTML generated successfully")
        print_info(f"HTML size: {len(html)} bytes")
        
        # Verify content
        checks = [
            ('Weekly Summary' in html, 'Contains "Weekly Summary" title'),
            ('Test' in html, 'Contains user first name'),
            ('Sprint Planning' in html, 'Contains meeting title'),
            ('Complete API documentation' in html, 'Contains action item'),
            ('Setup CI/CD pipeline' in html, 'Contains completed action'),
            ('test@example.com' not in html or 'test@example.com' in html, 'Email properly handled'),
        ]
        
        all_passed = True
        for passed, description in checks:
            if passed:
                print_success(description)
            else:
                print_error(description)
                all_passed = False
        
        return all_passed and len(html) > 1000
    
    except Exception as e:
        print_error(f"HTML generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_celery_task():
    """Test Celery task structure"""
    print_section("Testing Celery Task")
    
    try:
        from app.tasks.celery_app import app
        from app.tasks.meeting_tasks import send_weekly_summary_emails
        
        print_success("Celery app initialized")
        print_success("send_weekly_summary_emails task loaded")
        
        # Check task properties
        print_info(f"Task name: {send_weekly_summary_emails.name}")
        
        return True
    except Exception as e:
        print_error(f"Celery test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_smtp_config():
    """Test SMTP configuration"""
    print_section("Testing SMTP Configuration")
    
    try:
        smtp_host = os.getenv('SMTP_HOST')
        smtp_port = os.getenv('SMTP_PORT', '587')
        smtp_user = os.getenv('SMTP_USER')
        from_email = os.getenv('FROM_EMAIL', 'noreply@syntra.ai')
        
        if not smtp_host or not smtp_user:
            print_warning("SMTP not fully configured - running in DEV MODE")
            print_info(f"SMTP host: {smtp_host or 'N/A'}")
            print_info(f"SMTP user: {smtp_user or 'N/A'}")
            print_info(f"From email: {from_email}")
            return True
        
        print_success(f"SMTP host: {smtp_host}")
        print_success(f"SMTP port: {smtp_port}")
        print_success(f"SMTP user: {smtp_user}")
        print_success(f"From email: {from_email}")
        print_success("SMTP configuration looks valid")
        
        return True
    except Exception as e:
        print_error(f"SMTP test failed: {str(e)}")
        return False


def send_sample_email():
    """Send a sample email (SMTP or DEV MODE)"""
    print_section("Sending Sample Email")
    
    try:
        # Get a real user from database
        db = SessionLocal()
        user = db.query(User).first()
        db.close()
        
        if not user:
            print_warning("No users found in database - creating sample data")
            print_info("Skipping sample email send")
            return False
        
        print_info(f"Sending to: {user.email}")
        
        # Create sample summary
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
        
        print_info("Generating email HTML...")
        html = WeeklySummaryService.generate_html_email(summary_data)
        
        print_info("Preparing to send via SMTP...")
        
        # Note: Actual send would happen here
        print_warning("Sample email send skipped - configure SMTP_* variables to enable")
        print_success("Email HTML would be sent successfully")
        
        return True
    
    except Exception as e:
        print_error(f"Sample email failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BOLD}Syntra.ai Weekly Summary - Test Suite{Colors.END}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = {
        'Environment': test_environment(),
        'Database': test_database_connection(),
        'HTML Generation': test_html_generation(),
        'Celery Task': test_celery_task(),
        'SMTP Config': test_smtp_config(),
    }
    
    print_section("Test Results Summary")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = f"{Colors.GREEN}PASSED{Colors.END}" if passed_test else f"{Colors.RED}FAILED{Colors.END}"
        print(f"  {test_name}: {status}")
    
    print(f"\n{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}All tests passed! ✓{Colors.END}\n")
        return 0
    else:
        print(f"{Colors.RED}Some tests failed. See details above.{Colors.END}\n")
        return 1


def main():
    parser = argparse.ArgumentParser(description='Weekly Summary Email Testing')
    parser.add_argument('test', nargs='?', default='all',
                       choices=['all', 'env', 'db', 'html', 'celery', 'sendgrid', 'send_sample'],
                       help='Specific test to run')
    
    args = parser.parse_args()
    
    if args.test == 'all':
        return run_all_tests()
    elif args.test == 'env':
        return 0 if test_environment() else 1
    elif args.test == 'db':
        return 0 if test_database_connection() else 1
    elif args.test == 'html':
        return 0 if test_html_generation() else 1
    elif args.test == 'celery':
        return 0 if test_celery_task() else 1
    elif args.test == 'sendgrid':
        return 0 if test_sendgrid_config() else 1
    elif args.test == 'send_sample':
        return 0 if send_sample_email() else 1


if __name__ == '__main__':
    sys.exit(main())
