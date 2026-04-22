import os
import requests
import base64
import urllib.parse
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from ..models.user import User

load_dotenv()

class ZoomService:
    CLIENT_ID = os.getenv("ZOOM_CLIENT_ID")
    CLIENT_SECRET = os.getenv("ZOOM_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("ZOOM_REDIRECT_URI", "http://localhost:8000/api/zoom/callback")
    
    ZOOM_AUTH_URL = "https://zoom.us/oauth/authorize"
    ZOOM_TOKEN_URL = "https://zoom.us/oauth/token"
    ZOOM_API_BASE_URL = "https://api.zoom.us/v2"

    @classmethod
    def get_auth_url(cls, state: Optional[str] = None) -> str:
        """Génère l'URL d'autorisation Zoom"""
        encoded_redirect = urllib.parse.quote(cls.REDIRECT_URI, safe='')
        url = f"{cls.ZOOM_AUTH_URL}?response_type=code&client_id={cls.CLIENT_ID}&redirect_uri={encoded_redirect}"
        if state:
            url += f"&state={state}"
        return url

    @classmethod
    def exchange_code_for_token(cls, code: str) -> Dict[str, Any]:
        """Échange le code d'autorisation contre un access token et refresh token"""
        auth_header = base64.b64encode(f"{cls.CLIENT_ID}:{cls.CLIENT_SECRET}".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": cls.REDIRECT_URI
        }
        
        response = requests.post(cls.ZOOM_TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    @classmethod
    def refresh_token(cls, refresh_token: str) -> Dict[str, Any]:
        """Rafraîchit l'access token à l'aide du refresh token"""
        auth_header = base64.b64encode(f"{cls.CLIENT_ID}:{cls.CLIENT_SECRET}".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        response = requests.post(cls.ZOOM_TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    @classmethod
    def get_valid_access_token(cls, db: Session, user: User) -> str:
        """
        Récupère un access token valide pour l'utilisateur.
        Le rafraîchit si nécessaire.
        """
        if not user.zoom_access_token or not user.zoom_token_expires_at:
            raise Exception("Zoom not connected for this user")

        # Vérifier si le token expire dans moins de 5 minutes
        if user.zoom_token_expires_at < (datetime.utcnow() + timedelta(minutes=5)):
            try:
                # Refresh
                new_tokens = cls.refresh_token(user.zoom_refresh_token)
                
                user.zoom_access_token = new_tokens["access_token"]
                user.zoom_refresh_token = new_tokens["refresh_token"]
                user.zoom_token_expires_at = datetime.utcnow() + timedelta(seconds=new_tokens["expires_in"])
                
                db.commit()
                db.refresh(user)
            except Exception:
                raise Exception("Votre session Zoom a expiré. Veuillez vous reconnecter à Zoom.")

        return user.zoom_access_token

    @classmethod
    def get_user_account_type(cls, db: Session, user: User) -> str:
        """
        Récupère le type de compte Zoom de l'utilisateur.
        Retourne: 'basic', 'pro', 'business', ou 'unknown'
        """
        try:
            token = cls.get_valid_access_token(db, user)
            headers = {"Authorization": f"Bearer {token}"}
            
            response = requests.get(f"{cls.ZOOM_API_BASE_URL}/users/me", headers=headers)
            response.raise_for_status()
            
            user_data = response.json()
            account_type = user_data.get("plan", {}).get("type", "basic").lower()
            
            # Normaliser les types de compte
            if account_type in ["pro", "1"]:
                return "pro"
            elif account_type in ["business", "2"]:
                return "business"
            else:
                return "basic"
                
        except Exception as e:
            print(f"Error fetching Zoom account type: {str(e)}")
            return "unknown"

    @classmethod
    def get_meetings_large_history(cls, db: Session, user: User) -> List[Dict[str, Any]]:
        """Récupère l'historique Ultra-Large (Instantané, Prévu, Enregistré)"""
        token = cls.get_valid_access_token(db, user)
        headers = {"Authorization": f"Bearer {token}"}
        
        all_sessions = []
        
        # 1. Chercher dans les enregistrements (C'est là qu'on trouve les "Instant Meetings" enregistrées)
        try:
            # On cherche sur les 30 derniers jours pour être large
            from_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")
            res = requests.get(f"{cls.ZOOM_API_BASE_URL}/users/me/recordings?from={from_date}", headers=headers)
            if res.ok:
                recs = res.json().get("meetings", [])
                for r in recs:
                    r["source"] = "recording_record"
                    all_sessions.append(r)
        except: pass

        # 2. Chercher dans les différentes catégories de meetings
        for m_type in ["past", "pastOne", "upcoming", "scheduled"]:
            try:
                response = requests.get(
                    f"{cls.ZOOM_API_BASE_URL}/users/me/meetings?type={m_type}&page_size=50", 
                    headers=headers
                )
                if response.ok:
                    found = response.json().get("meetings", [])
                    for m in found:
                        m["source"] = f"meeting_{m_type}"
                        all_sessions.append(m)
            except: pass

        # 3. Filtrage et Uniformisation
        seen_keys = set()
        unique_sessions = []
        for s in all_sessions:
            # Clé unique : ID de réunion + Heure de début
            m_id = str(s.get("id") or s.get("uuid"))
            start_time = s.get("start_time", "unknown")
            key = f"{m_id}_{start_time}"
            
            if key not in seen_keys:
                session_data = {
                    "uuid": s.get("uuid") or m_id,
                    "id": m_id,
                    "topic": s.get("topic") or s.get("title") or "Réunion instantanée",
                    "start_time": start_time,
                    "duration": s.get("duration") or 0,
                }
                unique_sessions.append(session_data)
                seen_keys.add(key)
        
        # Trier : plus récent d'abord
        unique_sessions.sort(key=lambda x: x['start_time'], reverse=True)
        print(f"ULTRA SCAN : {len(unique_sessions)} sessions trouvées.")
        
        return {"meetings": unique_sessions}

    @classmethod
    def get_recording_files(cls, db: Session, user: User, meeting_id: str) -> Dict[str, Any]:
        """Récupère les fichiers d'un enregistrement spécifique"""
        token = cls.get_valid_access_token(db, user)
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(f"{cls.ZOOM_API_BASE_URL}/meetings/{meeting_id}/recordings", headers=headers)
        
        if not response.ok:
            print(f"Zoom API Error: {response.status_code} - {response.text}")
            
        response.raise_for_status()
        return response.json()

    @classmethod
    def get_audio_download_url(cls, db: Session, user: User, meeting_id: str) -> Optional[str]:
        """
        Récupère l'URL de téléchargement du fichier audio d'un meeting Zoom.
        Retourne l'URL avec le token d'accès pour AssemblyAI.
        """
        data = cls.get_recording_files(db, user, meeting_id)
        recording_files = data.get("recording_files", [])
        
        # Chercher le fichier audio (m4a ou mp4 audio only)
        # On préfère 'audio_only' ou 'audio_transcript'
        audio_file = None
        for file in recording_files:
            if file.get("file_type") == "M4A" or file.get("file_extension") == "m4a":
                audio_file = file
                break
            if "audio" in file.get("recording_type", "").lower():
                audio_file = file
                break
        
        if not audio_file:
            # Fallback sur le premier fichier si pas d'audio explicite
            if recording_files:
                audio_file = recording_files[0]
            else:
                return None
                
        download_url = audio_file.get("download_url")
        if not download_url:
            return None
            
        # Ajouter le token d'accès Zoom à l'URL car les fichiers sont protégés
        token = cls.get_valid_access_token(db, user)
        return f"{download_url}?access_token={token}"

    @classmethod
    def get_meeting_participants(cls, db: Session, user: User, meeting_id: str) -> List[Dict[str, Any]]:
        """
        Récupère la liste des participants d'un meeting passé.
        """
        token = cls.get_valid_access_token(db, user)
        headers = {"Authorization": f"Bearer {token}"}
        
        # On utilise l'endpoint des participants de réunion passée
        response = requests.get(
            f"{cls.ZOOM_API_BASE_URL}/past_meetings/{meeting_id}/participants", 
            headers=headers
        )
        
        if response.ok:
            return response.json().get("participants", [])
        return []
