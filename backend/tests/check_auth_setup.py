# backend/check_auth_setup.py
"""
Script de vérification de l'installation de l'authentification JWT
"""
import os
from pathlib import Path

def check_file(path):
    """Vérifie si un fichier existe"""
    exists = Path(path).exists()
    status = "[OK]" if exists else "[X]"
    print(f"{status} {path}")
    return exists

def check_env_var(var_name):
    """Vérifie si une variable d'environnement est définie"""
    exists = os.getenv(var_name) is not None
    status = "[OK]" if exists else "[!]"
    print(f"{status} Variable d'environnement: {var_name}")
    return exists

def main():
    print("=== Verification de l'installation de l'authentification JWT ===\n")
    
    print("Fichiers du systeme:")
    files = [
        "app/models/user.py",
        "app/schemas/user.py",
        "app/schemas/__init__.py",
        "app/services/auth_service.py",
        "app/services/__init__.py",
        "app/utils/dependencies.py",
        "app/utils/__init__.py",
        "app/api/auth.py",
        "alembic/versions/001_create_users_table.py",
        "docs/AUTHENTICATION.md",
        "docs/AUTH_README.md",
        "tests/test_auth.py",
        ".env.example"
    ]
    
    all_files_exist = all(check_file(f) for f in files)
    
    print("\nConfiguration:")
    # Charger .env si existe
    from dotenv import load_dotenv
    load_dotenv()
    
    jwt_key = check_env_var("JWT_SECRET_KEY")
    db_url = check_env_var("DATABASE_URL")
    
    print("\nDependances Python:")
    try:
        import jose
        print("[OK] python-jose installe")
    except ImportError:
        print("[X] python-jose manquant")
    
    try:
        import passlib
        print("[OK] passlib installe")
    except ImportError:
        print("[X] passlib manquant")
    
    try:
        from sqlalchemy.orm import Session
        print("[OK] SQLAlchemy installe")
    except ImportError:
        print("[X] SQLAlchemy manquant")
    
    print("\n" + "="*60)
    
    if all_files_exist and jwt_key and db_url:
        print("[OK] Installation complete! Pret a utiliser.")
        print("\nProchaines etapes:")
        print("   1. alembic upgrade head")
        print("   2. uvicorn app.main:app --reload")
        print("   3. Ouvrez http://localhost:8000/docs")
    else:
        print("[WARNING] Installation incomplete.")
        if not jwt_key:
            print("   -> Ajoutez JWT_SECRET_KEY dans .env")
        if not db_url:
            print("   -> Ajoutez DATABASE_URL dans .env")
    
    print("="*60)

if __name__ == "__main__":
    main()
