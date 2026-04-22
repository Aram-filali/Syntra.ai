# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class User(Base):
    """
    Modèle utilisateur pour l'authentification
    """
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    
    # Champs pour compatibilité avec Meeting
    name = Column(String, nullable=True)  # Alias pour full_name
    # Champs pour intégration Zoom
    zoom_access_token = Column(String, nullable=True)
    zoom_refresh_token = Column(String, nullable=True)
    zoom_token_expires_at = Column(DateTime, nullable=True)
    zoom_account_type = Column(String, nullable=True, default='basic')  # 'basic', 'pro', 'business'
    
    # Gestion de compte
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    email_verified = Column(Boolean, default=False)  # Email confirmation status
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    email_verified_at = Column(DateTime, nullable=True)  # When email was verified
    
    # Relations
    meetings = relationship("Meeting", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.username} ({self.email})>"
