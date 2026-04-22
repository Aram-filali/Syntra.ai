# backend/app/services/auth_service.py
import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from ..models.user import User
from ..schemas.user import UserCreate, TokenData

# Charger les variables d'environnement
load_dotenv()

# Configuration du hachage de mot de passe
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

# Configuration JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


class AuthService:
    """Service d'authentification avec JWT"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Vérifie si le mot de passe correspond au hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash le mot de passe"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Crée un token JWT
        
        Args:
            data: Données à encoder dans le token
            expires_delta: Durée de validité du token
            
        Returns:
            Token JWT encodé
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[TokenData]:
        """
        Décode et valide un token JWT
        
        Args:
            token: Token JWT à décoder
            
        Returns:
            TokenData si valide, None sinon
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("user_id")
            email: str = payload.get("email")
            
            if user_id is None or email is None:
                return None
            
            return TokenData(user_id=user_id, email=email)
        except JWTError:
            return None
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Récupère un utilisateur par email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        """Récupère un utilisateur par username"""
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Récupère un utilisateur par ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authentifie un utilisateur
        
        Args:
            db: Session de base de données
            email: Email de l'utilisateur
            password: Mot de passe en clair
            
        Returns:
            User si authentifié, None sinon
        """
        user = AuthService.get_user_by_email(db, email)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> User:
        """
        Crée un nouvel utilisateur
        
        Args:
            db: Session de base de données
            user_create: Données de création de l'utilisateur
            
        Returns:
            Utilisateur créé
        """
        hashed_password = AuthService.get_password_hash(user_create.password)
        
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            is_active=True,
            is_verified=False,  # À vérifier par email plus tard
            is_superuser=False
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def update_last_login(db: Session, user: User) -> User:
        """Met à jour la date de dernière connexion"""
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
