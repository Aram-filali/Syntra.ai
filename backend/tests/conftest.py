import sys
import os
import pytest
from datetime import datetime, timedelta
from typing import Generator

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app.main import app
from app.models.base import Base, get_db
from app.models.user import User
from app.models.meeting import Meeting, MeetingStatus, Transcription, ActionItem, Summary
from app.utils.dependencies import get_current_user, create_access_token

# Configure password hashing for tests
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Use in-memory SQLite for tests
@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """Create a test database and return a session."""
    # Create in-memory SQLite database
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    # Override get_db dependency
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield session
    
    session.close()
    engine.dispose()

@pytest.fixture(scope="function")
def test_client(test_db: Session) -> TestClient:
    """Create a test client with database override."""
    return TestClient(app)

@pytest.fixture(scope="function")
def test_user(test_db: Session) -> User:
    """Create a test user in the database."""
    user = User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password=pwd_context.hash("testpass123"),
        full_name="Test User",
        is_active=True,
        is_verified=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_user_with_zoom(test_db: Session) -> User:
    """Create a test user with Zoom tokens."""
    user = User(
        id=2,
        username="zoomuser",
        email="zoom@example.com",
        hashed_password=pwd_context.hash("testpass123"),
        full_name="Zoom User",
        is_active=True,
        is_verified=True,
        zoom_access_token="test_access_token",
        zoom_refresh_token="test_refresh_token",
        zoom_token_expires_at=datetime.utcnow() + timedelta(hours=1),
        zoom_account_type="pro"
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture(scope="function")
def auth_headers(test_user: User) -> dict:
    """Create authorization headers for a test user."""
    token = create_access_token(data={"sub": str(test_user.id)}, expires_delta=timedelta(hours=1))
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def test_meeting(test_db: Session, test_user: User) -> Meeting:
    """Create a test meeting."""
    meeting = Meeting(
        id=1,
        user_id=test_user.id,
        title="Test Meeting",
        status=MeetingStatus.SCHEDULED,
        scheduled_time=datetime.utcnow(),
        duration_minutes=60,
        participants=[]
    )
    test_db.add(meeting)
    test_db.commit()
    test_db.refresh(meeting)
    return meeting

@pytest.fixture(scope="function")
def test_meeting_with_transcription(test_db: Session, test_meeting: Meeting) -> tuple[Meeting, Transcription]:
    """Create a test meeting with transcription."""
    transcription = Transcription(
        id=1,
        meeting_id=test_meeting.id,
        full_text="This is a test meeting transcription.",
        speaker_segments=[
            {"speaker": "Speaker A", "text": "This is a test meeting", "start": 0, "end": 2500},
            {"speaker": "Speaker B", "text": "transcription.", "start": 2500, "end": 3000}
        ]
    )
    test_db.add(transcription)
    test_db.commit()
    test_db.refresh(transcription)
    return test_meeting, transcription

@pytest.fixture(scope="function")
def test_meeting_with_actions(test_db: Session, test_meeting: Meeting) -> tuple[Meeting, list]:
    """Create a test meeting with action items."""
    actions = [
        ActionItem(
            id=1,
            meeting_id=test_meeting.id,
            description="Follow up with John",
            assigned_to="John",
            due_date=datetime.utcnow() + timedelta(days=3),
            priority="high",
            status="todo"
        ),
        ActionItem(
            id=2,
            meeting_id=test_meeting.id,
            description="Send proposal",
            assigned_to="Jane",
            due_date=datetime.utcnow() + timedelta(days=5),
            priority="medium",
            status="in_progress"
        )
    ]
    for action in actions:
        test_db.add(action)
    test_db.commit()
    for action in actions:
        test_db.refresh(action)
    return test_meeting, actions

@pytest.fixture(scope="function")
def test_meeting_with_summary(test_db: Session, test_meeting: Meeting) -> tuple[Meeting, Summary]:
    """Create a test meeting with summary."""
    summary = Summary(
        id=1,
        meeting_id=test_meeting.id,
        executive_summary="Key points from the meeting:",
        decisions=[
            {"description": "Go-live decision approved"}
        ],
        questions=[
            {"question": "When is the launch date?"}
        ],
        full_markdown="# Test Meeting Summary\n\nThis is a test summary with markdown."
    )
    test_db.add(summary)
    test_db.commit()
    test_db.refresh(summary)
    return test_meeting, summary
