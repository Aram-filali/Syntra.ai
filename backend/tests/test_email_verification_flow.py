#!/usr/bin/env python3
"""
Test script for email verification workflow
Tests the complete flow: register → verify email → login
"""

import requests
import json
import time
import re
from urllib.parse import urlparse, parse_qs

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test.verification@example.com"
TEST_USERNAME = "testverification"
TEST_PASSWORD = "TestPassword123!"
TEST_FULL_NAME = "Test User"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

class EmailVerificationTester:
    def __init__(self):
        self.session = requests.Session()
        self.verification_token = None
        self.user_id = None
        self.user_email = None
        
    def log_success(self, message):
        print(f"{GREEN}✓ {message}{RESET}")
    
    def log_error(self, message):
        print(f"{RED}✗ {message}{RESET}")
    
    def log_info(self, message):
        print(f"{YELLOW}→ {message}{RESET}")
    
    def test_registration(self):
        """Test 1: User registration (should send verification email)"""
        print("\n" + "="*60)
        print("TEST 1: User Registration")
        print("="*60)
        
        self.log_info("Registering new user...")
        
        payload = {
            "email": TEST_EMAIL,
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD,
            "full_name": TEST_FULL_NAME
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/auth/register", json=payload)
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 201:
                data = response.json()
                if data.get("status") == "success":
                    self.user_id = data.get("user_id")
                    self.user_email = data.get("email")
                    self.log_success(f"User registered successfully! User ID: {self.user_id}")
                    return True
                else:
                    self.log_error(f"Registration returned unexpected response: {data}")
                    return False
            else:
                self.log_error(f"Registration failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            self.log_error(f"Registration error: {str(e)}")
            return False
    
    def test_login_before_verification(self):
        """Test 2: Login should fail (email not verified)"""
        print("\n" + "="*60)
        print("TEST 2: Login Before Email Verification (Should Fail)")
        print("="*60)
        
        self.log_info("Attempting to login with unverified email...")
        
        payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/auth/login", json=payload)
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 403:
                data = response.json()
                detail = data.get("detail", "")
                if "email" in detail.lower() and "verif" in detail.lower():
                    self.log_success(f"Login correctly rejected: {detail}")
                    return True
                else:
                    self.log_error(f"Wrong error message: {detail}")
                    return False
            else:
                self.log_error(f"Expected 403 but got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Login test error: {str(e)}")
            return False
    
    def test_resend_verification_email(self):
        """Test 3: Resend verification email"""
        print("\n" + "="*60)
        print("TEST 3: Resend Verification Email")
        print("="*60)
        
        self.log_info("Requesting verification email resend...")
        
        payload = {
            "email": TEST_EMAIL
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/auth/resend-verification-email", json=payload)
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_success("Verification email resent successfully")
                    return True
                else:
                    self.log_error(f"Unexpected response: {data}")
                    return False
            else:
                self.log_error(f"Resend failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Resend error: {str(e)}")
            return False
    
    def generate_test_token(self):
        """
        Generate a test verification token manually
        In a real scenario, you would extract this from the email or database
        """
        print("\n" + "="*60)
        print("TEST 4: Generate and Verify Email Token")
        print("="*60)
        
        self.log_info("Generating test verification token...")
        
        # For testing, we need to manually create a token using the service
        # In production, this comes from the email link
        # For now, we'll use a mock token generation
        
        try:
            # The token format is: {email}:{user_id}:{timestamp}:signature
            # For testing, we can extract it from the database
            self.log_info("(In real scenario, token is sent via email)")
            self.log_info("For testing, we would extract the token from the database")
            
            # Return a placeholder - in actual test, fetch from DB
            return True
            
        except Exception as e:
            self.log_error(f"Token generation error: {str(e)}")
            return False
    
    def test_email_verification(self):
        """Test 5: Verify email with token (requires manual token extraction)"""
        print("\n" + "="*60)
        print("TEST 5: Email Verification (Manual Token Required)")
        print("="*60)
        
        self.log_info("Email verification endpoint ready at:")
        self.log_info(f"POST /auth/verify-email")
        self.log_info("Required payload:")
        self.log_info("{ \"user_id\": <user_id>, \"token\": <token_from_email> }")
        
        print("\n" + "="*60)
        print("MANUAL VERIFICATION STEP REQUIRED")
        print("="*60)
        print("1. Check your email inbox for verification link from Meeting Intelligence")
        print("2. Extract the token and user_id from the verification link URL")
        print("3. Run: python test_email_verification_flow.py --verify <user_id> <token>")
        
        return None  # Requires manual intervention
    
    def verify_email_with_token(self, token):
        """Verify email using the token from email link"""
        print("\n" + "="*60)
        print("Verifying Email with Token")
        print("="*60)
        
        self.log_info(f"Verifying email for user_id: {self.user_id} with token: {token[:20]}...")
        
        payload = {
            "user_id": self.user_id,
            "token": token
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/auth/verify-email", json=payload)
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_success("Email verified successfully!")
                    return True
                else:
                    self.log_error(f"Verification failed: {data}")
                    return False
            else:
                self.log_error(f"Verification failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Verification error: {str(e)}")
            return False
    
    def test_login_after_verification(self):
        """Test 6: Login should succeed after email verification"""
        print("\n" + "="*60)
        print("TEST 6: Login After Email Verification")
        print("="*60)
        
        self.log_info("Attempting to login with verified email...")
        
        payload = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/auth/login", json=payload)
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("access_token"):
                    self.log_success("Login successful after email verification!")
                    self.log_success(f"Access Token: {data['access_token'][:50]}...")
                    return True
                else:
                    self.log_error(f"No token in response: {data}")
                    return False
            else:
                self.log_error(f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Login error: {str(e)}")
            return False
    
    def run_full_test(self):
        """Run complete email verification workflow test"""
        print("\n" + "="*70)
        print("EMAIL VERIFICATION WORKFLOW TEST")
        print("="*70)
        
        results = {
            "registration": self.test_registration(),
            "login_before_verification": self.test_login_before_verification(),
            "resend_verification": self.test_resend_verification_email(),
        }
        
        # Manual verification step
        self.test_email_verification()
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Registration: {('✓ PASS' if results['registration'] else '✗ FAIL')}")
        print(f"Login Before Verification: {('✓ PASS' if results['login_before_verification'] else '✗ FAIL')}")
        print(f"Resend Verification: {('✓ PASS' if results['resend_verification'] else '✗ FAIL')}")
        print("\nNote: Email verification step requires manual token extraction from email")
        
        return results


if __name__ == "__main__":
    import sys
    
    tester = EmailVerificationTester()
    
    if len(sys.argv) > 2 and sys.argv[1] == "--verify":
        # Manual verification mode: python script.py --verify <user_id> <token>
        user_id = sys.argv[2]
        token = sys.argv[3]
        tester.user_id = int(user_id)
        tester.verify_email_with_token(token)
        print("\nNow try logging in with: ", f"Email: {TEST_EMAIL}, Password: {TEST_PASSWORD}")
        tester.test_login_after_verification()
    else:
        # Run full workflow test
        tester.run_full_test()
