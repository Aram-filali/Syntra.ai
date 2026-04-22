"""
Backend tests for authentication service
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.models.user import User


class TestAuthService:
    """Test suite for authentication service"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password_123"
        hashed = AuthService.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert AuthService.verify_password(password, hashed)

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = AuthService.hash_password(password)
        
        assert not AuthService.verify_password(wrong_password, hashed)

    def test_create_user_success(self, test_db: Session):
        """Test successful user creation"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepass123",
            "full_name": "New User"
        }
        
        user = AuthService.create_user(test_db, **user_data)
        
        assert user.id is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
        assert user.full_name == "New User"
        assert user.is_active
        assert not user.is_verified
        assert AuthService.verify_password("securepass123", user.hashed_password)

    def test_create_user_duplicate_email(self, test_db: Session, test_user: User):
        """Test creating user with duplicate email"""
        user_data = {
            "username": "anotheruser",
            "email": test_user.email,  # Same email
            "password": "securepass123"
        }
        
        with pytest.raises(ValueError, match="Email already registered"):
            AuthService.create_user(test_db, **user_data)

    def test_get_user_by_email(self, test_db: Session, test_user: User):
        """Test retrieving user by email"""
        user = AuthService.get_user_by_email(test_db, test_user.email)
        
        assert user is not None
        assert user.email == test_user.email
        assert user.id == test_user.id

    def test_get_user_by_email_not_found(self, test_db: Session):
        """Test retrieving non-existent user by email"""
        user = AuthService.get_user_by_email(test_db, "nonexistent@example.com")
        
        assert user is None

    def test_authenticate_user_success(self, test_db: Session, test_user: User):
        """Test successful user authentication"""
        user = AuthService.authenticate_user(test_db, test_user.email, "testpass123")
        
        assert user is not None
        assert user.email == test_user.email

    def test_authenticate_user_wrong_password(self, test_db: Session, test_user: User):
        """Test authentication with wrong password"""
        user = AuthService.authenticate_user(test_db, test_user.email, "wrongpassword")
        
        assert user is None

    def test_authenticate_user_not_found(self, test_db: Session):
        """Test authentication with non-existent email"""
        user = AuthService.authenticate_user(test_db, "nonexistent@example.com", "anypass")
        
        assert user is None

    def test_authenticate_user_inactive(self, test_db: Session, test_user: User):
        """Test authentication with inactive user"""
        test_user.is_active = False
        test_db.commit()
        
        user = AuthService.authenticate_user(test_db, test_user.email, "testpass123")
        
        assert user is None
