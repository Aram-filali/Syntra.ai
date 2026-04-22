"""
Backend integration tests for API endpoints and complete flows
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app


class TestAuthEndpoints:
    """Test suite for authentication endpoints"""

    def test_register_success(self, test_client: TestClient, test_db: Session):
        """Test successful user registration"""
        response = test_client.post(
            "/api/auth/register",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepass123",
                "full_name": "New User"
            }
        )
        
        assert response.status_code in [200, 201]
        data = response.json()
        assert "access_token" in data
        assert data.get("username") == "newuser"

    def test_register_duplicate_email(self, test_client: TestClient, test_user, test_db: Session):
        """Test registration with duplicate email"""
        response = test_client.post(
            "/api/auth/register",
            json={
                "username": "anotheruser",
                "email": test_user.email,
                "password": "securepass123"
            }
        )
        
        assert response.status_code in [400, 409]

    def test_login_success(self, test_client: TestClient, test_user, test_db: Session):
        """Test successful login"""
        response = test_client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_wrong_password(self, test_client: TestClient, test_user, test_db: Session):
        """Test login with wrong password"""
        response = test_client.post(
            "/api/auth/login",
            data={
                "username": test_user.email,
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401

    def test_login_user_not_found(self, test_client: TestClient):
        """Test login with non-existent user"""
        response = test_client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "anypass"
            }
        )
        
        assert response.status_code == 401


class TestMeetingEndpoints:
    """Test suite for meeting endpoints"""

    def test_create_meeting_success(self, test_client: TestClient, auth_headers: dict, test_db: Session):
        """Test successful meeting creation"""
        response = test_client.post(
            "/api/meetings",
            headers=auth_headers,
            json={
                "title": "New Meeting",
                "scheduled_time": datetime.utcnow().isoformat(),
                "duration_minutes": 45
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data.get("title") == "New Meeting"

    def test_get_meetings_list(self, test_client: TestClient, auth_headers: dict, test_meeting, test_db: Session):
        """Test retrieving meetings list"""
        response = test_client.get(
            "/api/meetings",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_meeting_detail(self, test_client: TestClient, auth_headers: dict, test_meeting, test_db: Session):
        """Test retrieving meeting details"""
        response = test_client.get(
            f"/api/meetings/{test_meeting.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_meeting.id
        assert data["title"] == test_meeting.title

    def test_get_meeting_unauthorized(self, test_client: TestClient, test_meeting, test_db: Session):
        """Test accessing meeting without authentication"""
        response = test_client.get(f"/api/meetings/{test_meeting.id}")
        
        assert response.status_code == 401

    def test_get_transcription(self, test_client: TestClient, auth_headers: dict, test_meeting_with_transcription, test_db: Session):
        """Test retrieving transcription"""
        meeting, transcription = test_meeting_with_transcription
        response = test_client.get(
            f"/api/meetings/{meeting.id}/transcription",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "full_text" in data

    def test_get_actions(self, test_client: TestClient, auth_headers: dict, test_meeting_with_actions, test_db: Session):
        """Test retrieving meeting actions"""
        meeting, actions = test_meeting_with_actions
        response = test_client.get(
            f"/api/meetings/{meeting.id}/actions",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_update_action_item(self, test_client: TestClient, auth_headers: dict, test_meeting_with_actions, test_db: Session):
        """Test updating an action item"""
        meeting, actions = test_meeting_with_actions
        action = actions[0]
        
        response = test_client.patch(
            f"/api/meetings/actions/{action.id}",
            headers=auth_headers,
            json={
                "status": "completed",
                "priority": "high"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_search_meetings(self, test_client: TestClient, auth_headers: dict, test_meeting, test_db: Session):
        """Test global search functionality"""
        response = test_client.get(
            "/api/meetings/search/global",
            headers=auth_headers,
            params={"q": "Test"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestCompleteFlows:
    """Test complete user workflows"""

    def test_signup_and_login_flow(self, test_client: TestClient, test_db: Session):
        """Test complete signup and login flow"""
        # Register
        register_response = test_client.post(
            "/api/auth/register",
            json={
                "username": "flowuser",
                "email": "flow@example.com",
                "password": "flowpass123",
                "full_name": "Flow User"
            }
        )
        
        assert register_response.status_code in [200, 201]
        
        # Login
        login_response = test_client.post(
            "/api/auth/login",
            data={
                "username": "flow@example.com",
                "password": "flowpass123"
            }
        )
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        assert token is not None

    def test_create_meeting_and_fetch_flow(self, test_client: TestClient, auth_headers: dict, test_db: Session):
        """Test creating meeting and retrieving it"""
        # Create meeting
        create_response = test_client.post(
            "/api/meetings",
            headers=auth_headers,
            json={
                "title": "Flow Test Meeting",
                "scheduled_time": datetime.utcnow().isoformat(),
                "duration_minutes": 30
            }
        )
        
        assert create_response.status_code == 201
        meeting_id = create_response.json()["id"]
        
        # Fetch meeting
        fetch_response = test_client.get(
            f"/api/meetings/{meeting_id}",
            headers=auth_headers
        )
        
        assert fetch_response.status_code == 200
        assert fetch_response.json()["title"] == "Flow Test Meeting"
