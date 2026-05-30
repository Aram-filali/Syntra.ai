# backend/app/api/auth.py
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
import os

from ..models.base import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserLogin, UserResponse, Token
from ..services.auth_service import AuthService
from ..services.email_service import EmailService
from ..services.email_verification_service import EmailVerificationService
from ..services.password_reset_service import PasswordResetService
from ..utils.dependencies import get_current_user, get_current_active_user

router = APIRouter()


# Pydantic models
class VerifyEmailRequest(BaseModel):
    token: str
    user_id: int


class ResendVerificationEmailRequest(BaseModel):
    email: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    user_id: int
    new_password: str


class GoogleOAuthCallbackRequest(BaseModel):
    code: str
    redirect_uri: str


class AppleOAuthCallbackRequest(BaseModel):
    code: str
    id_token: str
    redirect_uri: str


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    📝 Inscription d'un nouvel utilisateur
    
    - **email**: Email unique de l'utilisateur
    - **username**: Nom d'utilisateur unique (3-50 caractères)
    - **password**: Mot de passe (min 8 caractères, 1 majuscule, 1 minuscule, 1 chiffre)
    - **full_name**: Nom complet (optionnel)
    
    Envoie un email de confirmation. L'utilisateur peut se connecter après vérification.
    """
    # Vérifier si l'email existe déjà
    existing_user = AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )
    
    # Vérifier si le username existe déjà
    existing_username = AuthService.get_user_by_username(db, user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris"
        )

    if not EmailService.can_deliver_email():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le service email n'est pas configuré. Réessayez plus tard."
        )
    
    try:
        # Créer l'utilisateur (email_verified = False par défaut)
        user = AuthService.create_user(db, user_data)
        
        # Envoyer l'email de vérification de manière synchrone.
        # Si l'envoi échoue, on supprime l'utilisateur pour éviter un compte
        # non vérifiable enregistré en base.
        token = EmailVerificationService.generate_verification_token(user.email, user.id)
        email_sent = EmailVerificationService.send_verification_email(user, token)
        if not email_sent:
            db.delete(user)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Impossible d'envoyer l'email de vérification. Compte non créé."
            )
        
        return {
            "status": "success",
            "message": "Inscripción réussie! Vérifiez votre email pour confirmer votre compte",
            "user_id": user.id,
            "email": user.email,
            "username": user.username
        }
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erreur lors de la création du compte"
        )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    🔐 Connexion d'un utilisateur
    
    - **email**: Email de l'utilisateur
    - **password**: Mot de passe
    
    Retourne un token JWT pour l'authentification
    """
    # Authentifier l'utilisateur
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Vérifier que l'email est confirmé
    can_login, error_message = EmailVerificationService.can_login(user)
    if not can_login:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=error_message
        )
    
    # Générer un token JWT
    access_token = AuthService.create_access_token(
        data={"user_id": user.id, "email": user.email}
    )
    
    # Mettre à jour la date de connexion
    AuthService.update_last_login(db, user)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    👤 Récupère les informations de l'utilisateur connecté
    
    Nécessite un token JWT valide dans le header Authorization
    """
    return UserResponse.from_orm(current_user)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    🚪 Déconnexion (côté client, le token doit être supprimé)
    
    Note: Avec JWT, la déconnexion est gérée côté client en supprimant le token.
    Cette route confirme simplement la déconnexion.
    """
    return {
        "message": f"Utilisateur {current_user.username} déconnecté avec succès",
        "detail": "Supprimez le token côté client"
    }


@router.get("/verify-token")
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    """
    ✅ Vérifie si le token JWT est valide
    
    Utile pour vérifier l'authentification côté frontend
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "email": current_user.email,
        "username": current_user.username
    }


@router.post("/verify-email")
async def verify_email(
    request: VerifyEmailRequest,
    db: Session = Depends(get_db)
):
    """
    ✅ Confirme l'adresse email d'un utilisateur
    
    - **user_id**: ID de l'utilisateur
    - **token**: Token de vérification envoyé par email
    
    Permet à l'utilisateur de se connecter après confirmation
    """
    success, message = EmailVerificationService.verify_email(db, request.user_id, request.token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "status": "success",
        "message": message
    }


@router.post("/resend-verification-email")
async def resend_verification_email(
    request: ResendVerificationEmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    📧 Renvoie l'email de vérification
    
    - **email**: Adresse email de l'utilisateur
    
    Utile si l'utilisateur n'a pas reçu l'email initial
    """
    user = AuthService.get_user_by_email(db, request.email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    if not EmailService.can_deliver_email():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le service email n'est pas configuré. Réessayez plus tard."
        )
    
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà vérifié"
        )

    if not EmailService.can_deliver_email():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Le service email n'est pas configuré. Réessayez plus tard."
        )

    token = EmailVerificationService.generate_verification_token(user.email, user.id)
    background_tasks.add_task(
        EmailVerificationService.send_verification_email,
        user,
        token,
    )
    
    return {
        "status": "success",
        "message": "Email de vérification en cours d'envoi"
    }


@router.post("/send-verification-email/{user_id}")
async def send_verification_email(
    user_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    📧 Envoie un email de vérification (après inscription)
    
    Généralement appelé automatiquement après `/register`
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email déjà vérifié"
        )
    
    token = EmailVerificationService.generate_verification_token(user.email, user.id)
    background_tasks.add_task(
        EmailVerificationService.send_verification_email,
        user,
        token,
    )
    
    return {
        "status": "success",
        "message": "Email de vérification en cours d'envoi"
    }


@router.post("/forgot-password")
async def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    🔐 Demande la réinitialisation du mot de passe
    
    - **email**: Adresse email de l'utilisateur
    
    Envoie un email avec un lien de réinitialisation (valide 24h)
    """
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    success, message = PasswordResetService.request_password_reset(db, request.email, frontend_url)
    
    return {
        "status": "success" if success else "error",
        "message": message
    }


@router.post("/reset-password")
async def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    🔐 Réinitialise le mot de passe avec un token valide
    
    - **token**: Token reçu par email
    - **user_id**: ID de l'utilisateur
    - **new_password**: Nouveau mot de passe
    
    Nécessite un token valide émis dans les 24 dernières heures
    """
    # Valider le nouveau mot de passe
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe doit contenir au moins 8 caractères"
        )
    
    if not any(c.isupper() for c in request.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe doit contenir au moins une majuscule"
        )
    
    if not any(c.islower() for c in request.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe doit contenir au moins une minuscule"
        )
    
    if not any(c.isdigit() for c in request.new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe doit contenir au moins un chiffre"
        )
    
    # Réinitialiser le mot de passe
    success, message = PasswordResetService.reset_password(
        db, 
        request.user_id, 
        request.token, 
        request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "status": "success",
        "message": message
    }

