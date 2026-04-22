import sys
import os

# Set up the path to import from app if run from backend folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import bcrypt
# Patch for bcrypt > 4.0.0 compatibility with passlib
# passlib tries to access bcrypt.__about__.__version__ which was removed
if not hasattr(bcrypt, "__about__"):
    try:
        bcrypt.__about__ = type("about", (object,), {"__version__": bcrypt.__version__})
    except Exception:
        pass

from app.models.base import SessionLocal
from app.models.user import User
from app.models.meeting import Meeting  # Add this import
from app.services.auth_service import AuthService

def list_users(db):
    try:
        users = db.query(User).all()
        print("Listing all users:")
        for u in users:
            print(f" - ID: {u.id}, Email: {u.email}, Username: {u.username}")
    except Exception as e:
        print(f"Error listing users: {e}")

def update_password(email, new_password):
    print(f"Attempting to update password for {email} to (len={len(new_password)})")
    db = SessionLocal()
    try:
        list_users(db)
        
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"\nUser with email '{email}' not found.")
            # Try to handle potential typo in email provided by user
            if "gamil.com" in email:
                 corrected_email = email.replace("gamil.com", "gmail.com")
                 print(f"Checking for '{corrected_email}' instead...")
                 user = db.query(User).filter(User.email == corrected_email).first()
        
        if user:
            # Use bcrypt directly to avoid passlib compatibility issues
            hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            user.hashed_password = hashed.decode('utf-8')
            db.commit()
            print(f"\nSUCCESS: Password for '{user.email}' has been updated to '{new_password}'.")
        else:
            print("\nFAILURE: User not found even after typo check.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    target_email = "aramfilali25@gamil.com"
    new_pass = "aram1234"
    update_password(target_email, new_pass)
