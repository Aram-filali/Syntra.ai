# backend/tests/test_auth_workflows_e2e.py
"""
End-to-End tests for authentication workflows:
1. Email Verification Workflow
2. Password Reset Workflow
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from httpx import AsyncClient

from app.main import app
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.services.auth_service import AuthService
from app.services.email_verification_service import EmailVerificationService
from app.services.password_reset_service import PasswordResetService
from app.schemas.user import UserCreate


class TestEmailVerificationWorkflow:
    """Test complete email verification workflow"""
    
    TEST_EMAIL = "workflow.test.email@example.com"
    TEST_USERNAME = "workflowtestuser"
    TEST_PASSWORD = "TestPassword123!"
    TEST_FULL_NAME = "Workflow Test User"
    
    @pytest.mark.asyncio
    async def test_email_verification_complete_workflow(self, db: Session, async_client: AsyncClient):
        """
        Test complete email verification workflow:
        1. User registers
        2. Email not verified yet
        3. Cannot login until verified
        4. Verify email with token
        5. Can login after verification
        """
        
        # Step 1: Register user
        print("\n=== STEP 1: User Registration ===")
        user_data = UserCreate(
            email=self.TEST_EMAIL,
            username=self.TEST_USERNAME,
            password=self.TEST_PASSWORD,
            full_name=self.TEST_FULL_NAME
        )
        
        user = AuthService.create_user(db, user_data)
        assert user is not None
        assert user.email_verified == False
        print(f"✓ User created: {user.id}")
        
        # Step 2: Verify email not verified initially
        print("\n=== STEP 2: Verify Email Not Verified ===")
        user_check = db.query(User).filter(User.id == user.id).first()
        assert user_check.email_verified == False
        print(f"✓ Email verification status: {user_check.email_verified}")
        
        # Step 3: Try to login before verification (should fail)
        print("\n=== STEP 3: Login Before Verification (Should Fail) ===")
        response = await async_client.post(
            "/api/auth/login",
            json={
                "email": self.TEST_EMAIL,
                "password": self.TEST_PASSWORD
            }
        )
        assert response.status_code == 403
        assert "email" in response.json()["detail"].lower() or "verif" in response.json()["detail"].lower()
        print(f"✓ Login blocked (403): {response.json()['detail']}")
        
        # Step 4: Generate and verify email token
        print("\n=== STEP 4: Generate Email Verification Token ===")
        token = EmailVerificationService.generate_verification_token(user.email, user.id)
        assert token is not None
        print(f"✓ Token generated: {token[:30]}...")
        
        # Step 5: Verify email using token
        print("\n=== STEP 5: Verify Email with Token ===")
        success, message = EmailVerificationService.verify_email(db, user.id, token)
        assert success == True
        print(f"✓ Email verified: {message}")
        
        # Step 6: Confirm email_verified in database
        print("\n=== STEP 6: Confirm Verification in Database ===")
        user_verified = db.query(User).filter(User.id == user.id).first()
        assert user_verified.email_verified == True
        assert user_verified.email_verified_at is not None
        print(f"✓ Email verification confirmed")
        print(f"  - email_verified: {user_verified.email_verified}")
        print(f"  - email_verified_at: {user_verified.email_verified_at}")
        
        # Step 7: Login after verification (should succeed)
        print("\n=== STEP 7: Login After Verification (Should Succeed) ===")
        response = await async_client.post(
            "/api/auth/login",
            json={
                "email": self.TEST_EMAIL,
                "password": self.TEST_PASSWORD
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        print(f"✓ Login successful")
        print(f"  - Token: {data['access_token'][:50]}...")
        print(f"  - Token Type: {data['token_type']}")
        
        # Step 8: Use token to access protected endpoint
        print("\n=== STEP 8: Access Protected Resource with Token ===")
        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {data['access_token']}"}
        )
        assert response.status_code == 200
        me_data = response.json()
        assert me_data["email"] == self.TEST_EMAIL
        assert me_data["username"] == self.TEST_USERNAME
        print(f"✓ Protected resource accessible")
        print(f"  - User: {me_data['username']}")
        print(f"  - Email: {me_data['email']}")
    
    @pytest.mark.asyncio
    async def test_resend_verification_email_after_failed_verification(self, db: Session, async_client: AsyncClient):
        """
        Test resend verification email flow
        """
        
        # Create user
        user_data = UserCreate(
            email="resend.test@example.com",
            username="resendtest",
            password="TestPassword123!",
            full_name="Resend Test"
        )
        user = AuthService.create_user(db, user_data)
        
        print("\n=== Test: Resend Verification Email ===")
        print(f"✓ User created: {user.id}")
        
        # Try to resend verification email
        success, message = EmailVerificationService.resend_verification_email(db, user.id)
        assert success == True
        print(f"✓ Verification email resent: {message}")
        
        # Verify still not verified
        user_check = db.query(User).filter(User.id == user.id).first()
        assert user_check.email_verified == False
        print(f"✓ Email still not verified: {user_check.email_verified}")


class TestPasswordResetWorkflow:
    """Test complete password reset workflow"""
    
    TEST_EMAIL = "workflow.test.reset@example.com"
    TEST_USERNAME = "workflowtestpwdreset"
    TEST_PASSWORD = "TestPassword123!"
    TEST_NEW_PASSWORD = "NewPassword456!"
    TEST_FULL_NAME = "Password Reset Test"
    
    @pytest.mark.asyncio
    async def test_password_reset_complete_workflow(self, db: Session, async_client: AsyncClient):
        """
        Test complete password reset workflow:
        1. User registers
        2. Request password reset
        3. Generate reset token
        4. Reset password with token
        5. Login with new password
        """
        
        # Step 1: Register user
        print("\n=== STEP 1: User Registration ===")
        user_data = UserCreate(
            email=self.TEST_EMAIL,
            username=self.TEST_USERNAME,
            password=self.TEST_PASSWORD,
            full_name=self.TEST_FULL_NAME
        )
        user = AuthService.create_user(db, user_data)
        assert user is not None
        print(f"✓ User created: {user.id}")
        
        # Step 2: Request password reset
        print("\n=== STEP 2: Request Password Reset ===")
        success, message = PasswordResetService.request_password_reset(db, self.TEST_EMAIL)
        assert success == True
        print(f"✓ Password reset requested: {message}")
        
        # Step 3: Generate reset token (simulate backend)
        print("\n=== STEP 3: Generate Reset Token ===")
        reset_token = PasswordResetService.generate_reset_token(self.TEST_EMAIL, user.id)
        assert reset_token is not None
        print(f"✓ Token generated: {reset_token[:30]}...")
        
        # Step 4: Verify token exists in database
        print("\n=== STEP 4: Verify Token in Database ===")
        import hashlib
        token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
        db_token = db.query(PasswordResetToken).filter(
            PasswordResetToken.token_hash == token_hash
        ).first()
        assert db_token is not None
        assert db_token.user_id == user.id
        assert db_token.is_used == False
        print(f"✓ Token found in database")
        print(f"  - User ID: {db_token.user_id}")
        print(f"  - Is Used: {db_token.is_used}")
        print(f"  - Expires At: {db_token.expires_at}")
        
        # Step 5: Verify token validity
        print("\n=== STEP 5: Verify Token Validity ===")
        is_valid, decoded_user_id, error = PasswordResetService.verify_reset_token(db, reset_token)
        assert is_valid == True
        assert decoded_user_id == user.id
        print(f"✓ Token is valid")
        print(f"  - User ID: {decoded_user_id}")
        
        # Step 6: Login with old password (should still work)
        print("\n=== STEP 6: Login with Old Password (Before Reset) ===")
        response = await async_client.post(
            "/api/auth/login",
            json={
                "email": self.TEST_EMAIL,
                "password": self.TEST_PASSWORD
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        print(f"✓ Login with old password works")
        
        # Step 7: Reset password with token
        print("\n=== STEP 7: Reset Password with Token ===")
        success, message = PasswordResetService.reset_password(
            db, 
            user.id, 
            reset_token, 
            self.TEST_NEW_PASSWORD
        )
        assert success == True
        print(f"✓ Password reset successful: {message}")
        
        # Step 8: Verify token marked as used
        print("\n=== STEP 8: Verify Token Marked as Used ===")
        db_token_used = db.query(PasswordResetToken).filter(
            PasswordResetToken.token_hash == token_hash
        ).first()
        assert db_token_used.is_used == True
        assert db_token_used.used_at is not None
        print(f"✓ Token marked as used")
        print(f"  - Is Used: {db_token_used.is_used}")
        print(f"  - Used At: {db_token_used.used_at}")
        
        # Step 9: Login with old password (should fail)
        print("\n=== STEP 9: Login with Old Password (After Reset - Should Fail) ===")
        response = await async_client.post(
            "/api/auth/login",
            json={
                "email": self.TEST_EMAIL,
                "password": self.TEST_PASSWORD
            }
        )
        assert response.status_code == 401
        print(f"✓ Login with old password fails (401)")
        
        # Step 10: Login with new password (should succeed)
        print("\n=== STEP 10: Login with New Password (After Reset) ===")
        response = await async_client.post(
            "/api/auth/login",
            json={
                "email": self.TEST_EMAIL,
                "password": self.TEST_NEW_PASSWORD
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        print(f"✓ Login with new password successful")
        print(f"  - Token: {data['access_token'][:50]}...")
        
        # Step 11: Try to reuse same token (should fail)
        print("\n=== STEP 11: Try to Reuse Token (Should Fail) ===")
        is_valid, _, error = PasswordResetService.verify_reset_token(db, reset_token)
        assert is_valid == False
        assert "used" in error.lower()
        print(f"✓ Token reuse prevented: {error}")
    
    @pytest.mark.asyncio
    async def test_reset_token_expiry(self, db: Session):
        """
        Test that expired tokens are rejected
        """
        
        print("\n=== Test: Reset Token Expiry ===")
        
        # Create user
        user_data = UserCreate(
            email="expiry.test@example.com",
            username="expirytest",
            password="TestPassword123!",
            full_name="Expiry Test"
        )
        user = AuthService.create_user(db, user_data)
        
        # Generate token
        reset_token = PasswordResetService.generate_reset_token(user.email, user.id)
        
        # Store token but mark expiry as past
        import hashlib
        token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
        
        expired_token = PasswordResetToken(
            user_id=user.id,
            token=reset_token,
            token_hash=token_hash,
            created_at=datetime.utcnow() - timedelta(hours=25),
            expires_at=datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        )
        db.add(expired_token)
        db.commit()
        
        # Try to verify expired token
        is_valid, _, error = PasswordResetService.verify_reset_token(db, reset_token)
        assert is_valid == False
        assert "expir" in error.lower()
        print(f"✓ Expired token rejected: {error}")


# Integration test combining both workflows in sequence
class TestAuthenticationWorkflowsIntegration:
    """Test multiple workflows in sequence"""
    
    @pytest.mark.asyncio
    async def test_signup_verify_then_reset_password(self, db: Session, async_client: AsyncClient):
        """
        Complete user journey:
        1. Sign up (verify email)
        2. Login
        3. Request password reset
        4. Reset password
        5. Login with new password
        """
        
        print("\n" + "="*70)
        print("COMPLETE USER JOURNEY TEST")
        print("="*70)
        
        email = "journey.test@example.com"
        username = "journeytest"
        password = "TestPassword123!"
        new_password = "NewPassword456!"
        
        # Step 1: Register
        print("\n1. REGISTRATION")
        user_data = UserCreate(
            email=email,
            username=username,
            password=password,
            full_name="Journey Test"
        )
        user = AuthService.create_user(db, user_data)
        print(f"✓ User registered: {user.id}")
        
        # Step 2: Verify email
        print("\n2. EMAIL VERIFICATION")
        token = EmailVerificationService.generate_verification_token(email, user.id)
        success, _ = EmailVerificationService.verify_email(db, user.id, token)
        assert success == True
        print(f"✓ Email verified")
        
        # Step 3: Login
        print("\n3. FIRST LOGIN")
        response = await async_client.post(
            "/api/auth/login",
            json={"email": email, "password": password}
        )
        assert response.status_code == 200
        token_response = response.json()
        print(f"✓ Login successful")
        
        # Step 4: Access protected resource
        print("\n4. ACCESS PROTECTED RESOURCE")
        response = await async_client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token_response['access_token']}"}
        )
        assert response.status_code == 200
        print(f"✓ Protected resource accessed")
        
        # Step 5: Request password reset
        print("\n5. REQUEST PASSWORD RESET")
        success, _ = PasswordResetService.request_password_reset(db, email)
        assert success == True
        print(f"✓ Password reset requested")
        
        # Step 6: Generate and use reset token
        print("\n6. RESET PASSWORD")
        reset_token = PasswordResetService.generate_reset_token(email, user.id)
        success, _ = PasswordResetService.reset_password(db, user.id, reset_token, new_password)
        assert success == True
        print(f"✓ Password reset successful")
        
        # Step 7: Login with new password
        print("\n7. LOGIN WITH NEW PASSWORD")
        response = await async_client.post(
            "/api/auth/login",
            json={"email": email, "password": new_password}
        )
        assert response.status_code == 200
        print(f"✓ Login with new password successful")
        
        print("\n" + "="*70)
        print("✅ COMPLETE USER JOURNEY SUCCESSFUL")
        print("="*70)
