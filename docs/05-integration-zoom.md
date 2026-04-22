# Syntra.ai - Intégration Zoom

Ce document détaille l'architecture technique, le flux de données et la démarche d'implémentation de l'intégration Zoom dans l'application Meeting Intelligence.

## 1. Architecture & Flux OAuth 2.0

L'intégration repose sur le protocole standard **OAuth 2.0 Server-to-Server** (ou User-Managed App) pour sécuriser l'accès aux données sans jamais stocker les mots de passe Zoom des utilisateurs.

### Diagramme de Séquence Simplifié

1.  **Initiation (Frontend)** : L'utilisateur clique sur "Sync Zoom". Le client demande l'URL de connexion au Backend.
2.  **Redirection (Zoom)** : L'utilisateur est redirigé vers `zoom.us/oauth/authorize`. Il valide les permissions.
3.  **Callback (Backend)** : Zoom renvoie un `code` temporaire à notre API (`/api/zoom/callback`).
4.  **Échange de Jetons** : Le Backend échange ce `code` contre deux jetons auprès des serveurs Zoom :
    *   `access_token` : Permet de lire les réunions (valide 1h).
    *   `refresh_token` : Permet de générer de nouveaux access tokens (valide 90 jours).
5.  **Persistance** : Les jetons sont chiffrés et stockés dans la table `users` de la base de données PostgreSQL.

---

## 2. Composants Techniques

### A. Backend (FastAPI)

Le code est modulaire et se divise en trois parties :

1.  **Modèle de Données (`models/user.py`)**
    Modifications de la table User pour stocker les crédits :
    ```python
    zoom_access_token = Column(String, nullable=True)
    zoom_refresh_token = Column(String, nullable=True)
    zoom_token_expires_at = Column(DateTime, nullable=True)
    ```

2.  **Service dédié (`services/zoom_service.py`)**
    Contient toute la logique métier :
    *   `get_auth_url()` : Génère l'URL avec le `client_id` et le `redirect_uri`.
    *   `exchange_code_for_token()` : Gère l'échange initial.
    *   `get_valid_access_token()` : **Fonction critique** qui vérifie si le token est expiré. S'il l'est, elle utilise automatiquement le `refresh_token` pour en obtenir un nouveau sans déconnecter l'utilisateur.
    *   `get_user_recordings()` : Appelle l'API Zoom `/users/me/recordings`.

3.  **API Endpoints (`api/zoom.py`)**
    *   `GET /login` : Fournit l'URL de redirection.
    *   `GET /callback` : Reçoit la réponse de Zoom et sauvegarde les tokens.
    *   `GET /me/recordings` : Proxy sécurisé qui récupère les vidéos.

### B. Frontend (React)

1.  **Client API (`api/client.js`)** : Centralise les appels vers le backend (`zoomAPI`).
2.  **Dashboard (`Dashboard.jsx`)** :
    *   Bouton "Sync Zoom" qui déclenche le flux.
    *   Modal d'importation affichant la liste des enregistrements.
    *   Logique de pré-remplissage du formulaire de création de meeting.

---

## 3. La Démarche d'Implémentation

Voici les étapes que nous avons suivies pour réaliser cette fonctionnalité :

### Étape 1 : Configuration Zoom Marketplace
*   Création d'une application de type **OAuth** sur [marketplace.zoom.us](https://marketplace.zoom.us).
*   Récupération des `Client ID` et `Client Secret`.
*   Configuration de la **Whitelist URL** et **Redirect URL** :
    *   Dev : `http://localhost:8000/api/zoom/callback`

### Étape 2 : Sécurisation des Scopes (Permissions)
Nous avons défini les droits minimums nécessaires pour l'application :
*   `user:read` : Pour identifier l'utilisateur.
*   `recording:read` : Pour lister et télécharger les enregistrements Cloud.

### Étape 3 : Développement du Socle Backend
1.  Mise à jour du schéma de base de données (Migration Alembic).
2.  Création du `ZoomService` pour isoler la complexité des appels HTTP.
3.  Implémentation de la route de callback pour capturer le retour de Zoom.

### Étape 4 : Développement de l'Interface (UX)
1.  Ajout d'indicateurs visuels (Loader, Notifications).
2.  Création d'un flux fluide : Dashboard -> Connexion Zoom -> Retour Dashboard -> Import.

### Étape 5 : Gestion des Erreurs et Logs
*   Traitement des erreurs communes (Token invalide, Scope manquant).
*   Ajout de logs détaillés pour faciliter le débogage (ex: erreur 400).

---

## 4. Configuration Environnement (.env)

Pour que la synchronisation fonctionne, les variables suivantes sont requises dans le `.env` du backend :

```bash
# Identifiants de l'application Zoom (Marketplace)
ZOOM_CLIENT_ID=votre_client_id
ZOOM_CLIENT_SECRET=votre_client_secret

# URL de redirection (Doit correspondre exactement à celle déclarée sur Zoom)
ZOOM_REDIRECT_URI=http://localhost:8000/api/zoom/callback

# Secret pour valider les Webhooks (Notifications automatiques)
ZOOM_WEBHOOK_SECRET=votre_webhook_secret
```

## 5. Perspectives d'Évolution

*   **Transcription Automatique** : Utiliser le lien de téléchargement fourni par l'API Zoom pour envoyer directement le fichier audio à AssemblyAI, sans action manuelle.
*   **Webhooks** : Activer le webhook `recording.completed` pour que l'analyse se lance toute seule dès que la réunion Zoom est finie.
