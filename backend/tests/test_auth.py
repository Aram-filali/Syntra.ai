# backend/tests/test_auth.py
"""
Tests pour l'authentification JWT
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.base import Base, get_db
from app.models.user import User

# Base de données de test en mémoire
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override de la dépendance de base de données pour les tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_database():
    """Créer et nettoyer la base de données pour chaque test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_register_user():
    """Test de l'inscription d'un utilisateur"""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123",
            "full_name": "Test User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["username"] == "testuser"
    assert "hashed_password" not in data["user"]  # Ne doit pas exposer le mot de passe


def test_register_duplicate_email():
    """Test de l'inscription avec un email déjà utilisé"""
    # Premier utilisateur
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser1",
            "password": "TestPass123"
        }
    )
    
    # Tentative avec le même email
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser2",
            "password": "TestPass123"
        }
    )
    
    assert response.status_code == 400
    assert "email est déjà utilisé" in response.json()["detail"]


def test_register_weak_password():
    """Test de l'inscription avec un mot de passe faible"""
    # Sans chiffre
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "WeakPassword"
        }
    )
    assert response.status_code == 422
    
    # Sans majuscule
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "weakpass123"
        }
    )
    assert response.status_code == 422


def test_login_success():
    """Test de connexion avec succès"""
    # Inscription
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123"
        }
    )
    
    # Connexion
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPass123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"


def test_login_wrong_password():
    """Test de connexion avec mauvais mot de passe"""
    # Inscription
    client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123"
        }
    )
    
    # Tentative avec mauvais mot de passe
    response = client.post(
        "/api/auth/login",
        json={
            "email": "test@example.com",
            "password": "WrongPass123"
        }
    )
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()


def test_get_current_user():
    """Test de récupération du profil utilisateur"""
    # Inscription
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123",
            "full_name": "Test User"
        }
    )
    
    token = register_response.json()["access_token"]
    
    # Récupérer le profil
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"


def test_get_current_user_invalid_token():
    """Test d'accès avec token invalide"""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    
    assert response.status_code == 401


def test_get_current_user_no_token():
    """Test d'accès sans token"""
    response = client.get("/api/auth/me")
    
    assert response.status_code == 403  # Forbidden car pas de token


def test_verify_token():
    """Test de vérification du token"""
    # Inscription
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123"
        }
    )
    
    token = register_response.json()["access_token"]
    
    # Vérifier le token
    response = client.get(
        "/api/auth/verify-token",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["email"] == "test@example.com"


def test_logout():
    """Test de déconnexion"""
    # Inscription
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPass123"
        }
    )
    
    token = register_response.json()["access_token"]
    
    # Déconnexion
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert "déconnecté" in response.json()["message"].lower()
