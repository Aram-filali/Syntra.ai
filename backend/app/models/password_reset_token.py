# backend/app/models/password_reset_token.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class PasswordResetToken(Base):
    """
    Modèle pour stocker les tokens de réinitialisation de mot de passe
    """
    __tablename__ = "password_reset_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(255), nullable=False)  # Token brut (ne pas exposer en logs)
    token_hash = Column(String(255), nullable=False, unique=True, index=True)  # Hash du token pour stockage sécurisé
    
    # Status
    is_used = Column(Boolean, default=False, index=True)
    used_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)  # Expire après 24h
    
    # Relations
    user = relationship("User", backref="reset_tokens")
    
    def is_valid(self) -> bool:
        """Vérifie si le token est encore valide"""
        if self.is_used:
            return False
        if datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def mark_as_used(self):
        """Marque le token comme utilisé"""
        self.is_used = True
        self.used_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<PasswordResetToken user_id={self.user_id} is_used={self.is_used}>"
