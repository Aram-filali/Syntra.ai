# backend/app/services/password_reset_service.py
"""
Service pour la réinitialisation de mot de passe
"""

import secrets
import hashlib
import os
from datetime import datetime, timedelta
from typing import Tuple
from sqlalchemy.orm import Session
from ..models.user import User
from .email_service import EmailService


class PasswordResetService:
    """Service de gestion des réinitialisations de mot de passe"""
    
    # Paramètres de token
    TOKEN_LENGTH = 32
    TOKEN_EXPIRY_HOURS = 24  # Les tokens expirent après 24 heures

    @staticmethod
    def _get_frontend_url() -> str:
        return os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
    
    @staticmethod
    def generate_reset_token(email: str, user_id: int) -> str:
        """
        Génère un token unique de réinitialisation
        
        Format: {random}:{hashed_email_id}
        """
        random_part = secrets.token_urlsafe(PasswordResetService.TOKEN_LENGTH)
        hash_part = hashlib.sha256(f"{email}:{user_id}:{datetime.utcnow().isoformat()}".encode()).hexdigest()[:16]
        return f"{random_part}:{hash_part}"
    
    @staticmethod
    def generate_reset_link(token: str, frontend_url: str | None = None) -> str:
        """
        Génère le lien de réinitialisation complet
        
        Retourne: {frontend_url}/reset-password?token=XXX
        """
        if not frontend_url:
            frontend_url = PasswordResetService._get_frontend_url()
        return f"{frontend_url}/reset-password?token={token}"
    
    @staticmethod
    def send_reset_email(user: User, token: str, frontend_url: str | None = None) -> bool:
        """
        Envoie l'email de réinitialisation via SMTP
        """
        reset_link = PasswordResetService.generate_reset_link(token, frontend_url)
        
        email_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; font-weight: bold; }}
                .token {{ background: #f5f5f5; padding: 15px; border-radius: 6px; font-family: monospace; word-break: break-all; margin: 20px 0; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px; }}
                .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; border-top: 1px solid #e0e0e0; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 28px;">🔐 Réinitialisation de Mot de Passe</h1>
                </div>
                
                <div class="content">
                    <p>Bonjour <strong>{user.username}</strong>,</p>
                    
                    <p>Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte Meeting Intelligence.</p>
                    
                    <p><strong>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</strong></p>
                    
                    <p>Pour réinitialiser votre mot de passe, cliquez sur le bouton ci-dessous:</p>
                    
                    <center>
                        <a href="{reset_link}" class="button">Réinitialiser Mon Mot de Passe</a>
                    </center>
                    
                    <p>Ou copiez le lien suivant dans votre navigateur:</p>
                    <p style="word-break: break-all; color: #667eea;">{reset_link}</p>
                    
                    <div class="warning">
                        <strong>⏰ Attention:</strong> Ce lien ne reste valide que <strong>24 heures</strong>.
                    </div>
                    
                    <div class="token">
                        {token}
                    </div>
                    
                    <p style="color: #999; font-size: 14px;">
                        Si vous avez des questions, contactez notre support à support@meetingintelligence.com
                    </p>
                </div>
                
                <div class="footer">
                    <p>© 2026 Meeting Intelligence. Tous droits réservés.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return EmailService.send_email(
            recipient_email=user.email,
            subject="🔐 Réinitialisation de votre mot de passe - Meeting Intelligence",
            html_content=email_template
        )
    
    @staticmethod
    def verify_reset_token(db: Session, token: str) -> Tuple[bool, int, str]:
        """
        Vérifie si un token de réinitialisation est valide
        
        Retourne: (is_valid, user_id, message)
        """
        try:
            from ..models.password_reset_token import PasswordResetToken
            
            # Hasher le token pour chercher en base
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Chercher le token
            reset_token = db.query(PasswordResetToken).filter(
                PasswordResetToken.token_hash == token_hash
            ).first()
            
            if not reset_token:
                return (False, 0, "Token de réinitialisation invalide")
            
            # Vérifier que le token n'est pas expiré
            if datetime.utcnow() > reset_token.expires_at:
                return (False, 0, "Ce lien de réinitialisation a expiré")
            
            # Vérifier que le token n'a pas déjà été utilisé
            if reset_token.is_used:
                return (False, 0, "Ce lien de réinitialisation a déjà été utilisé")
            
            return (True, reset_token.user_id, "Token valide")
        
        except Exception as e:
            return (False, 0, f"Erreur lors de la vérification du token: {str(e)}")
    
    @staticmethod
    def reset_password(db: Session, user_id: int, token: str, new_password: str) -> Tuple[bool, str]:
        """
        Réinitialise le mot de passe d'un utilisateur avec un token valide
        
        Retourne: (success, message)
        """
        try:
            from ..models.password_reset_token import PasswordResetToken
            
            # Vérifier que le token est valide
            is_valid, token_user_id, error_msg = PasswordResetService.verify_reset_token(db, token)
            if not is_valid:
                return (False, error_msg)
            
            # Vérifier que le token appartient à l'utilisateur
            if token_user_id != user_id:
                return (False, "Le token n'appartient pas à cet utilisateur")
            
            # Trouver l'utilisateur
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return (False, "Utilisateur non trouvé")
            
            # Mettre à jour le mot de passe
            from ..services.auth_service import AuthService
            user.hashed_password = AuthService.hash_password(new_password)
            user.updated_at = datetime.utcnow()
            
            # Marquer le token comme utilisé
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            reset_token = db.query(PasswordResetToken).filter(
                PasswordResetToken.token_hash == token_hash
            ).first()
            
            if reset_token:
                reset_token.mark_as_used()
            
            db.commit()
            
            return (True, "Mot de passe réinitialisé avec succès")
        
        except Exception as e:
            db.rollback()
            return (False, f"Erreur lors de la réinitialisation: {str(e)}")
    
    @staticmethod
    def request_password_reset(db: Session, email: str, frontend_url: str | None = None) -> Tuple[bool, str]:
        """
        Gère la demande de réinitialisation de mot de passe
        
        Retourne: (success, message)
        """
        try:
            if not frontend_url:
                frontend_url = PasswordResetService._get_frontend_url()

            from ..models.password_reset_token import PasswordResetToken
            from ..services.auth_service import AuthService
            
            # Chercher l'utilisateur par email
            user = AuthService.get_user_by_email(db, email)
            
            if not user:
                # Ne pas révéler si l'email existe ou non (sécurité)
                return (True, "Si cet email est associé à un compte, vous allez recevoir un lien de réinitialisation")
            
            # Générer le token
            token = PasswordResetService.generate_reset_token(email, user.id)
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            # Stocker le token en base de données avec expiry (24 heures)
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token,
                token_hash=token_hash,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(hours=PasswordResetService.TOKEN_EXPIRY_HOURS)
            )
            
            db.add(reset_token)
            db.commit()
            
            # Envoyer l'email
            EmailService.send_email(
                to_email=user.email,
                subject="🔐 Réinitialisation de votre mot de passe - Meeting Intelligence",
                html_content=PasswordResetService._generate_reset_email_html(user, token, frontend_url)
            )
            
            return (True, "Email de réinitialisation envoyé avec succès")
        
        except Exception as e:
            db.rollback()
            return (False, f"Erreur: {str(e)}")
    
    @staticmethod
    def _generate_reset_email_html(user: User, token: str, frontend_url: str) -> str:
        """Génère le HTML de l'email de réinitialisation"""
        reset_link = PasswordResetService.generate_reset_link(token, frontend_url)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background: white; padding: 30px; border: 1px solid #e0e0e0; border-radius: 0 0 8px 8px; }}
                .button {{ display: inline-block; padding: 12px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; font-weight: bold; }}
                .token {{ background: #f5f5f5; padding: 15px; border-radius: 6px; font-family: monospace; word-break: break-all; margin: 20px 0; font-size: 12px; }}
                .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px; }}
                .footer {{ text-align: center; padding: 20px; color: #999; font-size: 12px; border-top: 1px solid #e0e0e0; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1 style="margin: 0; font-size: 28px;">🔐 Réinitialisation de Mot de Passe</h1>
                </div>
                
                <div class="content">
                    <p>Bonjour <strong>{user.username}</strong>,</p>
                    
                    <p>Nous avons reçu une demande de réinitialisation de mot de passe pour votre compte Meeting Intelligence.</p>
                    
                    <p><strong>Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.</strong></p>
                    
                    <p>Pour réinitialiser votre mot de passe, cliquez sur le bouton ci-dessous:</p>
                    
                    <center>
                        <a href="{reset_link}" class="button">Réinitialiser Mon Mot de Passe</a>
                    </center>
                    
                    <p>Ou copiez le lien suivant dans votre navigateur:</p>
                    <p style="word-break: break-all; color: #667eea; font-size: 12px;">{reset_link}</p>
                    
                    <div class="warning">
                        <strong>⏰ Attention:</strong> Ce lien ne reste valide que <strong>24 heures</strong>.
                    </div>
                    
                    <div class="token">
                        Token: {token}
                    </div>
                    
                    <p style="color: #999; font-size: 14px; margin-top: 30px;">
                        Si vous avez des questions, contactez notre support à support@meetingintelligence.com
                    </p>
                </div>
                
                <div class="footer">
                    <p>© 2026 Meeting Intelligence. Tous droits réservés.</p>
                </div>
            </div>
        </body>
        </html>
        """
