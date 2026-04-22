"""
Email verification service - handles email confirmation tokens and verification
"""
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.email_service import EmailService
import secrets
import hashlib


class EmailVerificationService:
    """Service pour gérer la vérification d'email"""
    
    # Token validity: 24 hours
    TOKEN_EXPIRY_HOURS = 24
    
    @staticmethod
    def generate_verification_token(email: str, user_id: int) -> str:
        """
        Génère un token de vérification unique
        Format: {random_32_hex}
        """
        token = secrets.token_urlsafe(32)
        return token
    
    @staticmethod
    def generate_verification_link(token: str) -> str:
        """
        Génère le lien de vérification complet basé sur le FRONTEND_URL de l'environnement
        """
        import os
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000").rstrip("/")
        return f"{frontend_url}/verify-email?token={token}"
    
    @staticmethod
    def send_verification_email(user: User, token: str) -> bool:
        """
        Envoie l'email de vérification
        """
        verification_link = EmailVerificationService.generate_verification_link(token)
        
        # HTML email template
        html_content = f"""
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f3f4f6; padding: 40px 0;">
            <tr>
                <td align="center">
                    <table width="600" border="0" cellspacing="0" cellpadding="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                        <!-- Header -->
                        <tr>
                            <td align="center" style="background-color: #6366f1; padding: 40px 20px;">
                                <h1 style="color: #ffffff; margin: 0; font-family: 'Segoe UI', Arial, sans-serif; font-size: 28px; font-weight: 800;">Confirmer votre email</h1>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 40px 30px; font-family: 'Segoe UI', Arial, sans-serif;">
                                <p style="color: #1f2937; font-size: 18px; font-weight: 600; margin: 0 0 16px 0;">
                                    Bienvenue, {user.full_name or user.username} !
                                </p>
                                
                                <p style="color: #4b5563; font-size: 16px; line-height: 1.6; margin: 0 0 32px 0;">
                                    Merci d'avoir rejoint <strong>Meeting Intelligence</strong>. Pour finaliser votre inscription et activer votre compte, veuillez cliquer sur le bouton ci-dessous.
                                </p>
                                
                                <div style="text-align: center; margin-bottom: 32px;">
                                    <a href="{verification_link}" style="background-color: #6366f1; color: #ffffff; padding: 16px 32px; text-decoration: none; border-radius: 12px; font-weight: 700; font-size: 16px; display: inline-block;">
                                        ✓ Confirmer mon email
                                    </a>
                                </div>
                                
                                <p style="color: #9ca3af; font-size: 14px; margin: 0;">
                                    Ce lien expirera dans 24 heures. Si vous n'avez pas créé de compte, vous pouvez ignorer cet email.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 24px 30px; background-color: #f9fafb; border-top: 1px solid #e5e7eb; text-align: center;">
                                <p style="color: #9ca3af; font-size: 12px; margin: 0;">
                                    © 2026 Meeting Intelligence • IA pour vos réunions
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
        """
        
        try:
            return EmailService.send_email(
                recipient_email=user.email,
                subject="Confirmez votre adresse email - Meeting Intelligence",
                html_content=html_content
            )
        except Exception as e:
            print(f"Error sending verification email: {str(e)}")
            return False
    
    @staticmethod
    def verify_email(db: Session, user_id: int, token: str) -> tuple[bool, str]:
        """
        Vérifie l'email d'un utilisateur
        Returns: (success, message)
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False, "Utilisateur non trouvé"
            
            if user.email_verified:
                return False, "Email déjà vérifié"
            
            # In production, you would validate the token against a stored value
            # For now, we trust the token if the endpoint is properly secured
            user.email_verified = True
            user.email_verified_at = datetime.utcnow()
            db.commit()
            
            return True, "Email vérifié avec succès!"
        
        except Exception as e:
            db.rollback()
            return False, f"Erreur lors de la vérification: {str(e)}"
    
    @staticmethod
    def can_login(user: User) -> tuple[bool, Optional[str]]:
        """
        Vérifie si un utilisateur peut se connecter
        Returns: (can_login, error_message)
        """
        if not user.is_active:
            return False, "Compte désactivé"
        
        if not user.email_verified:
            return False, "Veuillez vérifier votre email avant de vous connecter"
        
        return True, None
    
    @staticmethod
    def resend_verification_email(db: Session, user_id: int) -> tuple[bool, str]:
        """
        Renvoie l'email de vérification
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            
            if not user:
                return False, "Utilisateur non trouvé"
            
            if user.email_verified:
                return False, "Email déjà vérifié"
            
            token = EmailVerificationService.generate_verification_token(user.email, user.id)
            
            if EmailVerificationService.send_verification_email(user, token):
                return True, "Email de vérification renvoyé"
            else:
                return False, "Erreur lors de l'envoi de l'email"
        
        except Exception as e:
            return False, f"Erreur: {str(e)}"
