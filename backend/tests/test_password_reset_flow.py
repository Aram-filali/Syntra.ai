#!/usr/bin/env python3
"""
Test script for password reset workflow
Tests the complete flow: forgot-password → reset-password
"""

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api"
TEST_EMAIL = "test.reset@example.com"
TEST_USERNAME = "testreset"
TEST_PASSWORD = "TestPassword123!"
TEST_NEW_PASSWORD = "NewPassword456!"
TEST_FULL_NAME = "Test Reset User"

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

class PasswordResetTester:
    def __init__(self):
        self.session = requests.Session()
        self.reset_token = None
        self.user_id = None
        self.user_email = None
        
    def log_success(self, message):
        print(f"{GREEN}✓ {message}{RESET}")
    
    def log_error(self, message):
        print(f"{RED}✗ {message}{RESET}")
    
    def log_info(self, message):
        print(f"{YELLOW}→ {message}{RESET}")
    
    def test_registration(self):
        """Test: User registration"""
        print("\n" + "="*60)
        print("TEST 1: User Registration")
        print("="*60)
        
        self.log_info("Registering new user for password reset test...")
        
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
    
    def test_forgot_password_request(self):
        """Test: Request password reset"""
        print("\n" + "="*60)
        print("TEST 2: Request Password Reset (Forgot Password)")
        print("="*60)
        
        self.log_info("Requesting password reset...")
        
        payload = {
            "email": TEST_EMAIL
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/auth/forgot-password", json=payload)
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_success("Password reset email sent successfully")
                    self.log_info("Check email inbox for reset link")
                    return True
                else:
                    self.log_error(f"Unexpected response: {data}")
                    return False
            else:
                self.log_error(f"Request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Request error: {str(e)}")
            return False
    
    def test_invalid_password_reset(self):
        """Test: Attempt reset with invalid token"""
        print("\n" + "="*60)
        print("TEST 3: Invalid Password Reset (Bad Token)")
        print("="*60)
        
        self.log_info("Attempting password reset with invalid token...")
        
        payload = {
            "token": "invalid-token-12345",
            "user_id": self.user_id,
            "new_password": TEST_NEW_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/auth/reset-password", json=payload)
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 400:
                self.log_success("Invalid token correctly rejected with 400")
                return True
            else:
                self.log_error(f"Expected 400 but got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Error: {str(e)}")
            return False
    
    def test_weak_password_reset(self):
        """Test: Attempt reset with weak password"""
        print("\n" + "="*60)
        print("TEST 4: Weak Password Validation")
        print("="*60)
        
        self.log_info("Testing weak password rejection...")
        
        weak_passwords = [
            ("short", "Too short"),
            ("nouppercase123", "No uppercase"),
            ("NOLOWERCASE123", "No lowercase"),
            ("NoDigits", "No digits"),
        ]
        
        for weak_pwd, reason in weak_passwords:
            payload = {
                "token": "any-token",
                "user_id": self.user_id,
                "new_password": weak_pwd
            }
            
            try:
                response = self.session.post(f"{API_BASE_URL}/auth/reset-password", json=payload)
                if response.status_code == 400:
                    self.log_success(f"Correctly rejected: {reason}")
                else:
                    self.log_error(f"Failed to reject weak password: {reason}")
            except:
                pass
    
    def test_manual_reset(self):
        """Test: Manual token reset (requires token from DB)"""
        print("\n" + "="*60)
        print("TEST 5: Password Reset with Valid Token (Manual)")
        print("="*60)
        
        print("\n" + "="*70)
        print("MANUAL TOKEN VERIFICATION REQUIRED")
        print("="*70)
        print("1. Check the password_reset_tokens table in the database:")
        print(f"   SELECT * FROM password_reset_tokens WHERE user_id = {self.user_id};")
        print("\n2. Extract the 'token' column value")
        print("\n3. Run: python test_password_reset_flow.py --reset <token>")
        print("\n4. This will reset the password and test the full flow")
        
        return True
    
    def reset_with_token(self, token):
        """Reset password using provided token"""
        print("\n" + "="*60)
        print("Resetting Password with Valid Token")
        print("="*60)
        
        self.log_info(f"Resetting password for user_id: {self.user_id}")
        
        payload = {
            "token": token,
            "user_id": self.user_id,
            "new_password": TEST_NEW_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/auth/reset-password", json=payload)
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_success("Password reset successfully!")
                    return True
                else:
                    self.log_error(f"Unexpected response: {data}")
                    return False
            else:
                self.log_error(f"Reset failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Error: {str(e)}")
            return False
    
    def test_login_with_new_password(self):
        """Test: Login with new password"""
        print("\n" + "="*60)
        print("TEST 6: Login with New Password")
        print("="*60)
        
        self.log_info("Attempting login with new password...")
        
        payload = {
            "email": TEST_EMAIL,
            "password": TEST_NEW_PASSWORD
        }
        
        try:
            response = self.session.post(f"{API_BASE_URL}/auth/login", json=payload)
            print(f"Response Status: {response.status_code}")
            print(f"Response Body: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("access_token"):
                    self.log_success("Login successful with new password!")
                    self.log_success(f"Token: {data['access_token'][:50]}...")
                    return True
                else:
                    self.log_error(f"No token in response: {data}")
                    return False
            else:
                self.log_error(f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_error(f"Error: {str(e)}")
            return False
    
    def run_full_test(self):
        """Run complete password reset workflow test"""
        print("\n" + "="*70)
        print("PASSWORD RESET WORKFLOW TEST")
        print("="*70)
        
        results = {
            "registration": self.test_registration(),
            "forgot_password": self.test_forgot_password_request(),
            "invalid_token": self.test_invalid_password_reset(),
            "weak_password": self.test_weak_password_reset(),
            "manual_reset": self.test_manual_reset(),
        }
        
        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"User Registration: {('✓ PASS' if results['registration'] else '✗ FAIL')}")
        print(f"Forgot Password Request: {('✓ PASS' if results['forgot_password'] else '✗ FAIL')}")
        print(f"Invalid Token Rejection: {('✓ PASS' if results['invalid_token'] else '✗ FAIL')}")
        print(f"Weak Password Validation: {('✓ PASS' if results['weak_password'] else '✗ FAIL')}")
        print(f"Manual Token Verification: See instructions above")
        
        return results


if __name__ == "__main__":
    import sys
    
    tester = PasswordResetTester()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        # Manual reset mode: python script.py --reset <token>
        if len(sys.argv) < 3:
            print("Usage: python script.py --reset <token>")
            sys.exit(1)
        
        token = sys.argv[2]
        tester.user_id = 1  # Should match the user in database
        tester.user_email = "test.reset@example.com"
        
        if tester.reset_with_token(token):
            print("\nNow testing login with new password...")
            tester.test_login_with_new_password()
        else:
            print("Password reset failed")
    else:
        # Run full workflow test
        tester.run_full_test()
