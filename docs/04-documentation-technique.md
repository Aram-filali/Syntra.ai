# Syntra.ai - Documentation Technique

## 📚 Table des Matières

1. [Stack Technologique](#stack-technologique)
2. [Installation et Configuration](#installation-et-configuration)
3. [Structure du Code](#structure-du-code)
4. [API Reference](#api-reference)
5. [Modèles de Données](#modèles-de-données)
6. [Agents IA - Implémentation](#agents-ia---implémentation)
7. [Tests](#tests)
8. [Déploiement](#déploiement)
9. [Dépannage](#dépannage)

---

## 🛠️ Stack Technologique

### Backend

| Composant | Technologie | Version | Rôle |
|-----------|-------------|---------|------|
| **Framework Web** | FastAPI | 0.109.0 | API REST |
| **Serveur ASGI** | Uvicorn | 0.27.0 | Serveur d'application |
| **ORM** | SQLAlchemy | 2.0.25 | Mapping objet-relationnel |
| **Base de données** | PostgreSQL | 15 | Persistance |
| **Migrations** | Alembic | 1.13.1 | Gestion versions DB |
| **Validation** | Pydantic | 2.5.3 | Validation de schémas |
| **LLM Framework** | LangChain | 0.1.4 | Orchestration IA |
| **LLM Provider** | OpenAI | 1.10.0 | Modèles IA (GPT-4o-mini) |
| **Transcription** | AssemblyAI | 0.17.0 | Speech-to-text |
| **Task Queue** | Celery | 5.3.6 | Traitement asynchrone |
| **Message Broker** | Redis | 5.0.1 | File de messages |
| **PDF Generation** | ReportLab | 4.0.9 | Génération de rapports |
| **Email** | SendGrid | 6.11.0 | Envoi d'emails |
| **Authentification** | python-jose | 3.3.0 | JWT tokens |
| **Hashing** | passlib | 1.7.4 | Hash de mots de passe |

### Frontend

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| **Framework** | React | Interface utilisateur |
| **Routing** | React Router | Navigation |
| **HTTP Client** | Axios | Appels API |
| **State Management** | React Hooks | Gestion d'état local |

### DevOps

| Outil | Rôle |
|-------|------|
| **Docker** | Conteneurisation |
| **Docker Compose** | Orchestration locale |
| **Git** | Versioning |

---

## 🚀 Installation et Configuration

### Prérequis

- **Python** : 3.10+
- **Node.js** : 16+
- **PostgreSQL** : 15+
- **Redis** : 7+
- **Docker & Docker Compose** : (optionnel mais recommandé)

### Installation Backend

#### 1. Cloner le Projet

```bash
git clone <repository-url>
cd meeting-intelligence
```

#### 2. Créer un Environnement Virtuel

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

#### 3. Installer les Dépendances

```bash
pip install -r requirements.txt
```

#### 4. Configuration des Variables d'Environnement

Créer un fichier `.env` dans le dossier `backend/` :

```bash
# Database
DATABASE_URL=postgresql://meeting_user:meeting_pass@localhost:5432/meeting_intelligence

# Redis
REDIS_URL=redis://localhost:6379/0

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# AssemblyAI
ASSEMBLYAI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Zoom
ZOOM_CLIENT_ID=xxxxxxxxxxxxxx
ZOOM_CLIENT_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
ZOOM_REDIRECT_URI=http://localhost:8000/auth/zoom/callback

# SendGrid (Email)
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=noreply@meeting-intelligence.com

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### 5. Démarrer les Services (Docker Compose)

```bash
# Depuis la racine du projet
docker-compose up -d
```

Cela démarre :
- PostgreSQL sur le port 5432
- Redis sur le port 6379

#### 6. Créer les Tables de la Base de Données

**Option 1 : Avec Alembic (recommandé)**

```bash
cd backend
alembic upgrade head
```

**Option 2 : Création automatique**

Les tables sont créées automatiquement au démarrage de l'application grâce à :
```python
# backend/app/main.py
models.Base.metadata.create_all(bind=engine)
```

#### 7. Démarrer le Serveur Backend

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

L'API est accessible sur : **http://localhost:8000**

Documentation interactive : **http://localhost:8000/docs**

#### 8. Démarrer Celery Worker (optionnel)

Dans un nouveau terminal :

```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

### Installation Frontend

```bash
cd frontend
npm install
npm run dev
```

Le frontend est accessible sur : **http://localhost:3000**

---

## 📁 Structure du Code

### Backend

```
backend/
│
├── alembic/                          # Migrations de base de données
│   ├── versions/                     # Scripts de migration
│   │   ├── 67dc4ad592e9_inital.py
│   │   └── 869e4dc6a980_create_all_tables.py
│   └── env.py                        # Configuration Alembic
│
├── app/
│   ├── __init__.py
│   ├── main.py                       # Point d'entrée FastAPI
│   │
│   ├── api/                          # Endpoints REST
│   │   ├── __init__.py
│   │   └── meetings.py               # Routes /api/meetings
│   │
│   ├── agents/                       # Agents IA
│   │   ├── __init__.py
│   │   ├── orchestrator.py           # Coordinateur principal
│   │   ├── action_agent.py           # Extraction d'actions
│   │   ├── decision_agent.py         # Extraction de décisions
│   │   ├── question_agent.py         # Extraction de questions
│   │   └── summary_agent.py          # Génération de résumé
│   │
│   ├── models/                       # Modèles SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py                   # Configuration DB
│   │   └── meeting.py                # Entités (User, Meeting, etc.)
│   │
│   ├── tasks/                        # Tâches asynchrones
│   │   ├── __init__.py
│   │   ├── celery_app.py             # Configuration Celery
│   │   └── meeting_tasks.py          # Tâches (transcription, analyse)
│   │
│   └── llm_provider.py               # Factory LLM
│
├── tests/                            # Tests unitaires et d'intégration
│   ├── __init__.py
│   ├── conftest.py                   # Fixtures pytest
│   ├── test_agent.py                 # Tests des agents
│   ├── fakes/
│   │   └── fake_llm.py               # Mock LLM pour tests
│   └── mock_data/
│       ├── llm_responses.py          # Réponses LLM mockées
│       └── transcriptions.py         # Transcriptions de test
│
├── requirements.txt                  # Dépendances Python
├── alembic.ini                       # Configuration Alembic
├── test_openai.py                    # Script de test OpenAI
└── test_full_flow.py                 # Test du workflow complet
```

### Fichiers Clés

#### `app/main.py`
Point d'entrée de l'application FastAPI. Configure :
- CORS
- Routes
- Middleware
- Création des tables

#### `app/api/meetings.py`
Définit tous les endpoints de l'API :
- Création de réunion
- Liste des réunions
- Ajout de transcription
- Analyse IA
- Récupération des résultats

#### `app/agents/orchestrator.py`
Coordinateur des agents IA. Gère :
- L'exécution parallèle des agents
- La coordination des résultats
- La gestion des erreurs

#### `app/models/meeting.py`
Définit les modèles de données :
- `User`
- `Meeting`
- `Transcription`
- `ActionItem`
- `Summary`

---

## 🌐 API Reference

### Base URL
```
http://localhost:8000/api/meetings
```

### Endpoints

#### 1. Créer une Réunion

```http
POST /api/meetings/
```

**Body** :
```json
{
  "title": "Réunion de planification Sprint 12",
  "scheduled_time": "2026-01-20T14:00:00",
  "duration_minutes": 60,
  "zoom_meeting_id": "123456789",
  "user_id": 1
}
```

**Response** (201 Created) :
```json
{
  "id": 1,
  "title": "Réunion de planification Sprint 12",
  "status": "scheduled",
  "scheduled_time": "2026-01-20T14:00:00",
  "created_at": "2026-01-15T12:30:00"
}
```

#### 2. Lister Toutes les Réunions

```http
GET /api/meetings/
```

**Response** (200 OK) :
```json
[
  {
    "id": 1,
    "title": "Réunion de planification Sprint 12",
    "status": "completed",
    "scheduled_time": "2026-01-20T14:00:00",
    "duration_minutes": 60,
    "has_transcription": true,
    "has_summary": true
  }
]
```

#### 3. Obtenir une Réunion Spécifique

```http
GET /api/meetings/{meeting_id}
```

**Response** (200 OK) :
```json
{
  "id": 1,
  "title": "Réunion de planification Sprint 12",
  "status": "completed",
  "scheduled_time": "2026-01-20T14:00:00",
  "duration_minutes": 60,
  "has_transcription": true,
  "has_summary": true,
  "actions_count": 5
}
```

#### 4. Ajouter une Transcription

```http
POST /api/meetings/{meeting_id}/transcription
```

**Body** :
```json
{
  "full_text": "Bonjour à tous, bienvenue à cette réunion...",
  "speaker_segments": {
    "speakers": [
      {"name": "Marie", "segments": [{"start": 0, "end": 15, "text": "..."}]},
      {"name": "Paul", "segments": [{"start": 15, "end": 30, "text": "..."}]}
    ]
  }
}
```

**Response** (200 OK) :
```json
{
  "id": 1,
  "meeting_id": 1,
  "text_length": 2547,
  "created_at": "2026-01-15T15:00:00"
}
```

#### 5. Analyser une Réunion avec IA

```http
POST /api/meetings/{meeting_id}/analyze
```

**Response** (200 OK) :
```json
{
  "status": "completed",
  "actions_count": 5,
  "decisions_count": 3,
  "questions_count": 2,
  "summary_preview": "Cette réunion a porté sur la planification du Sprint 12. L'équipe a convenu de..."
}
```

**Erreurs possibles** :
- `404` : Meeting not found
- `400` : No transcription available
- `400` : Meeting already analyzed
- `500` : AI analysis failed

#### 6. Récupérer le Résumé

```http
GET /api/meetings/{meeting_id}/summary
```

**Response** (200 OK) :
```json
{
  "id": 1,
  "meeting_id": 1,
  "executive_summary": "Cette réunion a couvert les objectifs du Sprint 12...",
  "decisions": {
    "items": [
      {
        "decision": "Utilisation de PostgreSQL",
        "context": "Discussion sur la base de données",
        "impact": "Architecture technique"
      }
    ]
  },
  "questions": {
    "items": [
      {
        "question": "Quel budget pour le projet ?",
        "answered": true,
        "answer": "50 000€"
      }
    ]
  },
  "full_markdown": "# Résumé de Réunion\n\n## Titre: ...",
  "created_at": "2026-01-15T15:05:00"
}
```

#### 7. Récupérer les Actions

```http
GET /api/meetings/{meeting_id}/actions
GET /api/meetings/{meeting_id}/actions?status=pending
```

**Response** (200 OK) :
```json
[
  {
    "id": 1,
    "description": "Préparer le rapport Q4",
    "assigned_to": "Marie Dupont",
    "deadline": "Vendredi 24 janvier",
    "priority": "HIGH",
    "status": "pending",
    "created_at": "2026-01-15T15:05:00"
  }
]
```

#### 8. Mettre à Jour le Statut d'une Action

```http
PATCH /api/meetings/actions/{action_id}
```

**Body** :
```json
{
  "status": "completed"
}
```

**Response** (200 OK) :
```json
{
  "id": 1,
  "status": "completed"
}
```

#### 9. Supprimer une Réunion

```http
DELETE /api/meetings/{meeting_id}
```

**Response** (200 OK) :
```json
{
  "status": "deleted",
  "meeting_id": 1
}
```

---

## 🗄️ Modèles de Données

### User

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    zoom_auth_token = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    meetings = relationship("Meeting", back_populates="user")
```

### Meeting

```python
class MeetingStatus(enum.Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    zoom_meeting_id = Column(String, unique=True)
    title = Column(String)
    scheduled_time = Column(DateTime)
    duration_minutes = Column(Integer)
    status = Column(Enum(MeetingStatus), default=MeetingStatus.SCHEDULED)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="meetings")
    transcription = relationship("Transcription", back_populates="meeting")
    action_items = relationship("ActionItem", back_populates="meeting")
    summary = relationship("Summary", back_populates="meeting")
```

### Transcription

```python
class Transcription(Base):
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), unique=True)
    full_text = Column(String)
    speaker_segments = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    meeting = relationship("Meeting", back_populates="transcription")
```

### ActionItem

```python
class ActionItem(Base):
    __tablename__ = "action_items"
    
    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    description = Column(String)
    assigned_to = Column(String)
    deadline = Column(String)
    priority = Column(String)  # HIGH, MEDIUM, LOW
    status = Column(String, default="pending")  # pending, in_progress, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    meeting = relationship("Meeting", back_populates="action_items")
```

### Summary

```python
class Summary(Base):
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), unique=True)
    executive_summary = Column(String)
    decisions = Column(JSON)
    questions = Column(JSON)
    full_markdown = Column(String)
    pdf_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    meeting = relationship("Meeting", back_populates="summary")
```

---

## 🤖 Agents IA - Implémentation

### Architecture Générale

Tous les agents suivent le même pattern :

```python
class BaseAgent:
    def __init__(self, llm: Runnable):
        self.llm = llm
        self.prompt_template = """..."""
    
    async def extract(self, transcription: str) -> dict:
        # 1. Construire le prompt
        prompt = self.prompt_template.format(transcription=transcription)
        
        # 2. Appeler le LLM
        response = await self.llm.ainvoke(prompt)
        
        # 3. Parser la réponse JSON
        result = json.loads(response.content)
        
        # 4. Valider et retourner
        return result
```

### Action Agent

**Fichier** : `backend/app/agents/action_agent.py`

```python
from langchain_core.runnables import Runnable
import json

class ActionItemsAgent:
    def __init__(self, llm: Runnable):
        self.llm = llm
    
    async def extract(self, transcription: str) -> dict:
        prompt = f"""
Tu es un expert en extraction d'actions à partir de transcriptions de réunions.

Analyse la transcription suivante et identifie TOUTES les actions mentionnées.

Pour chaque action, détermine :
- action : description précise de l'action à entreprendre
- assigned_to : la personne assignée (nom complet si mentionné, sinon "Non spécifié")
- deadline : l'échéance (date exacte si mentionnée, sinon description temporelle)
- priority : HIGH, MEDIUM ou LOW basé sur l'urgence et l'importance
- context : contexte de l'action (pourquoi elle est nécessaire)

Transcription :
{transcription}

Retourne UNIQUEMENT un JSON valide dans ce format exact :
{{
  "items": [
    {{
      "action": "...",
      "assigned_to": "...",
      "deadline": "...",
      "priority": "HIGH|MEDIUM|LOW",
      "context": "..."
    }}
  ]
}}

Ne retourne RIEN d'autre que ce JSON.
"""
        
        response = await self.llm.ainvoke(prompt)
        
        try:
            result = json.loads(response.content)
            return result
        except json.JSONDecodeError:
            # Extraction manuelle si JSON invalide
            # ou retour d'un objet vide
            return {"items": []}
```

**Exemple de sortie** :
```json
{
  "items": [
    {
      "action": "Préparer le rapport financier Q4",
      "assigned_to": "Marie Dupont",
      "deadline": "Vendredi 24 janvier 2026",
      "priority": "HIGH",
      "context": "Pour la présentation au board"
    },
    {
      "action": "Contacter le client pour validation",
      "assigned_to": "Paul Martin",
      "deadline": "Cette semaine",
      "priority": "MEDIUM",
      "context": "Avant de commencer le développement"
    }
  ]
}
```

### Decision Agent

**Fichier** : `backend/app/agents/decision_agent.py`

```python
class DecisionsAgent:
    def __init__(self, llm: Runnable):
        self.llm = llm
    
    async def extract(self, transcription: str) -> dict:
        prompt = f"""
Tu es un expert en identification de décisions lors de réunions.

Analyse la transcription et identifie TOUTES les décisions prises.

Une décision est :
- Un choix explicite entre plusieurs options
- Un consensus atteint par l'équipe
- Une validation formelle d'une proposition

Pour chaque décision, détermine :
- decision : la décision prise (claire et concise)
- context : le contexte de la discussion
- participants : les personnes impliquées dans la décision
- impact : l'impact estimé de cette décision

Transcription :
{transcription}

Retourne UNIQUEMENT un JSON valide :
{{
  "items": [
    {{
      "decision": "...",
      "context": "...",
      "participants": ["...", "..."],
      "impact": "..."
    }}
  ]
}}
"""
        
        response = await self.llm.ainvoke(prompt)
        result = json.loads(response.content)
        return result
```

### Question Agent

**Fichier** : `backend/app/agents/question_agent.py`

```python
class QuestionsAgent:
    def __init__(self, llm: Runnable):
        self.llm = llm
    
    async def extract(self, transcription: str) -> dict:
        prompt = f"""
Tu es un expert en analyse de questions lors de réunions.

Analyse la transcription et identifie TOUTES les questions posées.

Pour chaque question, détermine :
- question : la question exacte posée
- asked_by : qui a posé la question
- answered : true si une réponse a été donnée, false sinon
- answer : la réponse si elle existe, null sinon
- timestamp : moment approximatif dans la réunion

Transcription :
{transcription}

Retourne UNIQUEMENT un JSON valide :
{{
  "items": [
    {{
      "question": "...",
      "asked_by": "...",
      "answered": true/false,
      "answer": "..." ou null,
      "timestamp": "..."
    }}
  ]
}}
"""
        
        response = await self.llm.ainvoke(prompt)
        result = json.loads(response.content)
        return result
```

### Summary Agent

**Fichier** : `backend/app/agents/summary_agent.py`

```python
class SummaryAgent:
    def __init__(self, llm: Runnable):
        self.llm = llm
    
    async def generate(
        self, 
        transcription: str, 
        actions: dict,
        decisions: dict,
        questions: dict,
        metadata: dict
    ) -> dict:
        prompt = f"""
Tu es un expert en création de résumés de réunions professionnelles.

Crée un résumé complet et structuré de cette réunion.

**MÉTADONNÉES :**
Titre : {metadata.get('title', 'N/A')}
Durée : {metadata.get('duration', 'N/A')} minutes

**TRANSCRIPTION :**
{transcription[:2000]}...

**ACTIONS IDENTIFIÉES :**
{json.dumps(actions, indent=2)}

**DÉCISIONS PRISES :**
{json.dumps(decisions, indent=2)}

**QUESTIONS SOULEVÉES :**
{json.dumps(questions, indent=2)}

Génère :
1. **executive_summary** : Un résumé exécutif de 2-3 paragraphes
2. **key_points** : Liste des 5 points clés
3. **full_markdown** : Un rapport complet en Markdown incluant :
   - Titre et métadonnées
   - Résumé exécutif
   - Décisions prises
   - Actions à entreprendre (tableau)
   - Questions soulevées
   - Prochaines étapes

Retourne UNIQUEMENT un JSON valide :
{{
  "executive_summary": "...",
  "key_points": ["...", "..."],
  "full_markdown": "# Titre\\n\\n## Section..."
}}
"""
        
        response = await self.llm.ainvoke(prompt)
        result = json.loads(response.content)
        return result
```

### Orchestrator

**Fichier** : `backend/app/agents/orchestrator.py`

```python
import asyncio
from .action_agent import ActionItemsAgent
from .decision_agent import DecisionsAgent
from .question_agent import QuestionsAgent
from .summary_agent import SummaryAgent

class MeetingIntelligenceOrchestrator:
    def __init__(self, llm):
        self.llm = llm
        self.action_agent = ActionItemsAgent(llm)
        self.decision_agent = DecisionsAgent(llm)
        self.question_agent = QuestionsAgent(llm)
        self.summary_agent = SummaryAgent(llm)
    
    async def process_meeting(self, transcription: str, metadata: dict):
        """
        Orchestration principale - exécution parallèle des agents
        """
        # Étape 1 : Exécution PARALLÈLE des 3 agents indépendants
        results = await asyncio.gather(
            self.action_agent.extract(transcription),
            self.decision_agent.extract(transcription),
            self.question_agent.extract(transcription),
        )
        
        actions, decisions, questions = results
        
        # Étape 2 : Synthèse avec tous les résultats
        summary = await self.summary_agent.generate(
            transcription=transcription,
            actions=actions,
            decisions=decisions,
            questions=questions,
            metadata=metadata
        )
        
        return {
            "actions": actions,
            "decisions": decisions,
            "questions": questions,
            "summary": summary
        }
```

**Avantages de cette architecture** :
1. **Performance** : Exécution parallèle réduit le temps total
2. **Modularité** : Chaque agent peut être testé/modifié indépendamment
3. **Scalabilité** : Facile d'ajouter de nouveaux agents
4. **Maintenabilité** : Code clair et organisé

---

## 🧪 Tests

### Structure des Tests

```
tests/
├── __init__.py
├── conftest.py                 # Fixtures pytest globales
├── test_agent.py               # Tests des agents IA
├── fakes/
│   └── fake_llm.py             # Mock LLM pour tests sans API
└── mock_data/
    ├── llm_responses.py        # Réponses LLM mockées
    └── transcriptions.py       # Transcriptions de test
```

### Fixtures Principales

**Fichier** : `tests/conftest.py`

```python
import pytest
from app.models.base import Base, engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="function")
def db_session():
    """Crée une session DB pour les tests"""
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)
    session = TestingSessionLocal()
    
    yield session
    
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_transcription():
    """Transcription de test"""
    return """
Marie: Bonjour à tous. Aujourd'hui nous allons planifier le Sprint 12.
Paul: Excellent. Qui va s'occuper du module d'authentification ?
Marie: Je propose que Sophie prenne cette tâche. Il faut la terminer pour vendredi.
Sophie: D'accord, je m'en occupe.
Jean: Avons-nous décidé quelle base de données utiliser ?
Marie: Oui, nous avons convenu d'utiliser PostgreSQL.
"""
```

### Tests des Agents

**Fichier** : `tests/test_agent.py`

```python
import pytest
from app.agents.action_agent import ActionItemsAgent
from tests.fakes.fake_llm import FakeLLM
from tests.mock_data.llm_responses import MOCK_ACTIONS_RESPONSE

@pytest.mark.asyncio
async def test_action_agent_extraction():
    """Test de l'extraction d'actions"""
    # Arrange
    fake_llm = FakeLLM(response=MOCK_ACTIONS_RESPONSE)
    agent = ActionItemsAgent(fake_llm)
    transcription = "Sophie doit préparer le rapport pour vendredi."
    
    # Act
    result = await agent.extract(transcription)
    
    # Assert
    assert "items" in result
    assert len(result["items"]) > 0
    assert result["items"][0]["assigned_to"] == "Sophie"
    assert "rapport" in result["items"][0]["action"]

@pytest.mark.asyncio
async def test_orchestrator_full_flow(sample_transcription):
    """Test du workflow complet"""
    from app.agents.orchestrator import MeetingIntelligenceOrchestrator
    from tests.fakes.fake_llm import FakeLLM
    
    # Arrange
    llm = FakeLLM()
    orchestrator = MeetingIntelligenceOrchestrator(llm)
    
    # Act
    result = await orchestrator.process_meeting(
        transcription=sample_transcription,
        metadata={"title": "Test Meeting", "duration": 30}
    )
    
    # Assert
    assert "actions" in result
    assert "decisions" in result
    assert "questions" in result
    assert "summary" in result
```

### Fake LLM pour Tests

**Fichier** : `tests/fakes/fake_llm.py`

```python
class FakeLLM:
    """Mock LLM pour tests sans appeler OpenAI"""
    
    def __init__(self, response=None):
        self.response = response or '{"items": []}'
    
    async def ainvoke(self, prompt):
        """Simule un appel LLM"""
        class FakeResponse:
            def __init__(self, content):
                self.content = content
        
        return FakeResponse(self.response)
```

### Exécution des Tests

```bash
# Tous les tests
pytest

# Tests avec coverage
pytest --cov=app tests/

# Tests d'un fichier spécifique
pytest tests/test_agent.py

# Tests verbeux
pytest -v
```

---

## 🚀 Déploiement

### Déploiement Local (Development)

1. **Démarrer les services** :
```bash
docker-compose up -d
```

2. **Démarrer le backend** :
```bash
cd backend
uvicorn app.main:app --reload
```

3. **Démarrer Celery** (optionnel) :
```bash
celery -A app.tasks.celery_app worker --loglevel=info
```

### Déploiement Production

#### Option 1 : Docker Compose

**Fichier** : `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"

  celery_worker:
    build: ./backend
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: meeting_intelligence
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

**Déploiement** :
```bash
docker-compose -f docker-compose.prod.yml up -d
```

#### Option 2 : Cloud (AWS, GCP, Azure)

**Recommandations** :
- **Backend** : AWS ECS / Google Cloud Run / Azure App Service
- **Base de données** : AWS RDS / Google Cloud SQL / Azure Database for PostgreSQL
- **Redis** : AWS ElastiCache / Google Memorystore
- **Celery Workers** : AWS ECS Tasks / Google Cloud Run Jobs

### Checklist de Déploiement

- [ ] Variables d'environnement configurées
- [ ] Base de données migrée (`alembic upgrade head`)
- [ ] SSL/TLS configuré (HTTPS)
- [ ] Monitoring activé (logs, métriques)
- [ ] Backups configurés (base de données)
- [ ] Rate limiting activé
- [ ] CORS configuré correctement
- [ ] Secrets sécurisés (pas de hardcoding)

---

## 🛠️ Dépannage

### Problème : L'API ne démarre pas

**Symptômes** :
```
ERROR: Could not connect to database
```

**Solutions** :
1. Vérifier que PostgreSQL est démarré :
   ```bash
   docker-compose ps
   ```

2. Vérifier la variable `DATABASE_URL` :
   ```bash
   echo $DATABASE_URL
   ```

3. Tester la connexion manuellement :
   ```bash
   psql postgresql://meeting_user:meeting_pass@localhost:5432/meeting_intelligence
   ```

### Problème : Erreur lors de l'analyse IA

**Symptômes** :
```
500 Internal Server Error: AI analysis failed
```

**Solutions** :
1. Vérifier la clé API OpenAI :
   ```bash
   echo $OPENAI_API_KEY
   ```

2. Tester OpenAI manuellement :
   ```bash
   python backend/test_openai.py
   ```

3. Vérifier les logs :
   ```bash
   tail -f backend/logs/app.log
   ```

### Problème : Celery worker ne traite pas les tâches

**Symptômes** :
Les tâches restent dans la queue Redis sans être traitées.

**Solutions** :
1. Vérifier que le worker est actif :
   ```bash
   celery -A app.tasks.celery_app inspect active
   ```

2. Vérifier la connexion Redis :
   ```bash
   redis-cli ping
   # Réponse attendue : PONG
   ```

3. Redémarrer le worker :
   ```bash
   celery -A app.tasks.celery_app worker --loglevel=debug
   ```

### Logs et Debugging

**Activer le mode debug** :
```python
# backend/app/main.py
import logging

logging.basicConfig(level=logging.DEBUG)
app = FastAPI(debug=True)
```

**Consulter les logs Celery** :
```bash
celery -A app.tasks.celery_app events
```

---

## 📖 Documentation Complémentaire

### Ressources Officielles

- **FastAPI** : https://fastapi.tiangolo.com/
- **SQLAlchemy** : https://docs.sqlalchemy.org/
- **LangChain** : https://python.langchain.com/
- **OpenAI** : https://platform.openai.com/docs
- **Celery** : https://docs.celeryq.dev/
- **Alembic** : https://alembic.sqlalchemy.org/

### Tutoriels Recommandés

1. **FastAPI + SQLAlchemy** : https://fastapi.tiangolo.com/tutorial/sql-databases/
2. **LangChain Multi-Agent** : https://python.langchain.com/docs/use_cases/
3. **Celery avec FastAPI** : https://testdriven.io/blog/fastapi-and-celery/

---

**Date de dernière mise à jour** : Janvier 2026  
**Version** : 1.0.0  
**Mainteneur** : Équipe Meeting Intelligence
