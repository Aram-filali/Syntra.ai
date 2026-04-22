# Syntra.ai - Documentation Architecturale

## 📚 Table des Matières

1. [Vue d'Ensemble de l'Architecture](#vue-densemble-de-larchitecture)
2. [Architecture en Couches](#architecture-en-couches)
3. [Composants Principaux](#composants-principaux)
4. [Architecture des Données](#architecture-des-données)
5. [Architecture d'Intégration](#architecture-dintégration)
6. [Architecture de Déploiement](#architecture-de-déploiement)
7. [Diagrammes d'Architecture](#diagrammes-darchitecture)

---

## 🏛️ Vue d'Ensemble de l'Architecture

### Style Architectural
**Meeting Intelligence** suit une architecture **microservices légère** avec les caractéristiques suivantes :

- **API-First** : Communication via API REST
- **Event-Driven** : Déclenchement par événements (fin de réunion, nouvelle transcription)
- **Asynchrone** : Traitement en arrière-plan pour les opérations longues
- **Découplage** : Séparation claire entre couches et composants

### Principes Architecturaux

#### 1. Separation of Concerns (SoC)
Chaque composant a une responsabilité unique et bien définie.

#### 2. Single Responsibility Principle (SRP)
Chaque module, classe et fonction fait une seule chose.

#### 3. Dependency Inversion
Les couches de haut niveau ne dépendent pas des couches de bas niveau.

#### 4. Scalability by Design
Architecture permettant la montée en charge horizontale.

---

## 📐 Architecture en Couches

```
┌─────────────────────────────────────────────────────────┐
│                   PRESENTATION LAYER                    │
│                                                         │
│  ┌──────────────┐         ┌──────────────┐            │
│  │   Frontend   │         │  REST API    │            │
│  │   (React)    │◄────────┤  (FastAPI)   │            │
│  └──────────────┘         └──────────────┘            │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   APPLICATION LAYER                     │
│                                                         │
│  ┌────────────────┐    ┌──────────────────┐           │
│  │  Orchestrator  │    │  Business Logic  │           │
│  │  (Coordination)│    │  (Use Cases)     │           │
│  └────────────────┘    └──────────────────┘           │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                   DOMAIN LAYER                          │
│                                                         │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐    │
│  │Agent1│  │Agent2│  │Agent3│  │Agent4│  │Models│    │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘    │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────┐
│                  INFRASTRUCTURE LAYER                   │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │PostgreSQL│  │  Redis   │  │  Celery  │  │External││
│  │   (DB)   │  │ (Cache)  │  │ (Tasks)  │  │  APIs  ││
│  └──────────┘  └──────────┘  └──────────┘  └────────┘│
└─────────────────────────────────────────────────────────┘
```

### Détails des Couches

#### Couche Présentation
- **Responsabilité** : Interface utilisateur et exposition de l'API
- **Technologies** : React (Frontend), FastAPI (Backend API)
- **Contient** : 
  - Contrôleurs API
  - Validation des requêtes
  - Serialization/Deserialization

#### Couche Application
- **Responsabilité** : Logique métier et orchestration
- **Technologies** : Python (logique métier)
- **Contient** :
  - Use cases
  - Orchestrateurs
  - Services applicatifs

#### Couche Domaine
- **Responsabilité** : Logique métier pure, règles business
- **Technologies** : Python
- **Contient** :
  - Modèles de domaine
  - Agents IA
  - Règles métier

#### Couche Infrastructure
- **Responsabilité** : Persistance et services externes
- **Technologies** : PostgreSQL, Redis, Celery
- **Contient** :
  - Repositories
  - Adaptateurs externes
  - Configuration

---

## 🔧 Composants Principaux

### 1. Backend API (FastAPI)

```
backend/
│
├── app/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée FastAPI
│   │
│   ├── api/                    # Couche Présentation
│   │   └── meetings.py         # Endpoints REST
│   │
│   ├── agents/                 # Couche Domaine
│   │   ├── orchestrator.py     # Coordinateur multi-agents
│   │   ├── action_agent.py     # Agent extraction actions
│   │   ├── decision_agent.py   # Agent extraction décisions
│   │   ├── question_agent.py   # Agent extraction questions
│   │   └── summary_agent.py    # Agent synthèse
│   │
│   ├── models/                 # Couche Domaine
│   │   ├── base.py             # Configuration SQLAlchemy
│   │   └── meeting.py          # Modèles de données
│   │
│   ├── tasks/                  # Couche Infrastructure
│   │   ├── celery_app.py       # Configuration Celery
│   │   └── meeting_tasks.py    # Tâches asynchrones
│   │
│   └── llm_provider.py         # Service LLM
│
└── tests/                      # Tests
    ├── test_agent.py
    └── conftest.py
```

**Responsabilités** :
- Exposer l'API REST
- Orchestrer les agents IA
- Gérer la persistance
- Coordonner les tâches asynchrones

### 2. Frontend Application (React)

```
frontend/
│
├── src/
│   ├── pages/                  # Pages de l'application
│   │   ├── Dashboard.jsx
│   │   ├── MeetingList.jsx
│   │   └── MeetingDetail.jsx
│   │
│   ├── components/             # Composants réutilisables
│   │   ├── MeetingCard.jsx
│   │   ├── ActionItem.jsx
│   │   └── Summary.jsx
│   │
│   └── api/                    # Client API
│       └── client.js
│
└── public/
```

**Responsabilités** :
- Interface utilisateur
- Appels API vers le backend
- Affichage des résultats

### 3. Base de Données (PostgreSQL)

**Schéma relationnel** :

```
┌─────────────┐
│    users    │
├─────────────┤
│ id (PK)     │
│ email       │
│ name        │
│ zoom_token  │
└─────┬───────┘
      │
      │ 1:N
      ▼
┌─────────────────┐
│    meetings     │
├─────────────────┤
│ id (PK)         │
│ user_id (FK)    │
│ title           │
│ scheduled_time  │
│ duration        │
│ status          │
│ zoom_meeting_id │
└─────┬───────────┘
      │
      │ 1:1
      ▼
┌──────────────────┐         ┌──────────────────┐
│ transcriptions   │         │    summaries     │
├──────────────────┤         ├──────────────────┤
│ id (PK)          │         │ id (PK)          │
│ meeting_id (FK)  │◄────┐   │ meeting_id (FK)  │
│ full_text        │     │   │ exec_summary     │
│ speaker_segments │     │   │ decisions (JSON) │
└──────────────────┘     │   │ questions (JSON) │
                         │   │ full_markdown    │
                         │   └──────────────────┘
                         │
                         │ 1:N
                         │
                   ┌─────┴──────────┐
                   │  action_items  │
                   ├────────────────┤
                   │ id (PK)        │
                   │ meeting_id (FK)│
                   │ description    │
                   │ assigned_to    │
                   │ deadline       │
                   │ priority       │
                   │ status         │
                   └────────────────┘
```

### 4. Task Queue (Celery + Redis)

**Architecture des tâches asynchrones** :

```
┌─────────────┐
│   FastAPI   │
│   Request   │
└──────┬──────┘
       │
       │ Enqueue task
       ▼
┌─────────────────┐
│  Redis Queue    │
│  (Message Broker)│
└──────┬──────────┘
       │
       │ Dequeue
       ▼
┌─────────────────┐
│ Celery Worker   │
│                 │
│ • Transcription │
│ • Analysis      │
│ • PDF Gen       │
│ • Email Send    │
└──────┬──────────┘
       │
       │ Update status
       ▼
┌─────────────────┐
│   PostgreSQL    │
└─────────────────┘
```

**Tâches définies** :
1. `transcribe_meeting` : Envoi audio à AssemblyAI
2. `analyze_meeting` : Exécution des agents IA
3. `generate_pdf` : Création du rapport PDF
4. `send_email_notifications` : Envoi des emails

### 5. Agents IA

**Architecture d'orchestration** :

```python
class MeetingIntelligenceOrchestrator:
    """
    Coordinateur central des agents IA
    """
    
    def __init__(self, llm):
        self.action_agent = ActionItemsAgent(llm)
        self.decision_agent = DecisionsAgent(llm)
        self.question_agent = QuestionsAgent(llm)
        self.summary_agent = SummaryAgent(llm)
    
    async def process_meeting(self, transcription, metadata):
        # Étape 1 : Exécution parallèle des agents indépendants
        results = await asyncio.gather(
            self.action_agent.extract(transcription),
            self.decision_agent.extract(transcription),
            self.question_agent.extract(transcription)
        )
        
        # Étape 2 : Synthèse avec tous les résultats
        summary = await self.summary_agent.generate(
            transcription, 
            results, 
            metadata
        )
        
        return {
            "actions": results[0],
            "decisions": results[1],
            "questions": results[2],
            "summary": summary
        }
```

**Pattern utilisé** : Orchestration avec exécution parallèle

---

## 💾 Architecture des Données

### Flux de Données

```
┌──────────┐
│   Zoom   │ Audio Recording
└────┬─────┘
     │
     ▼
┌──────────────┐
│ AssemblyAI   │ Transcription
└────┬─────────┘
     │
     ▼
┌──────────────┐
│ PostgreSQL   │ Storage (text)
│ transcription│
└────┬─────────┘
     │
     ▼
┌──────────────────┐
│   LLM Agents     │ Analysis
│ (OpenAI GPT-4)   │
└────┬─────────────┘
     │
     ▼
┌──────────────────┐
│   PostgreSQL     │ Storage (structured)
│ actions/decisions│
└────┬─────────────┘
     │
     ▼
┌──────────────┐
│   Frontend   │ Display
└──────────────┘
```

### Stratégie de Cache

**Redis est utilisé pour** :
1. **Broker Celery** : File de messages pour tâches asynchrones
2. **Session Storage** : Sessions utilisateurs
3. **API Response Cache** : Cache des réponses GET fréquentes (liste meetings)

**TTL (Time To Live)** :
- Liste meetings : 5 minutes
- Détails meeting : 1 heure
- Résultats d'analyse : permanent (invalidation manuelle)

---

## 🔗 Architecture d'Intégration

### Intégrations Externes

#### 1. Zoom API
```
Meeting Intelligence ──HTTP──> Zoom API
                     <────────
                     
Endpoints utilisés :
• GET /meetings         (liste des réunions)
• GET /meetings/{id}    (détails)
• GET /recordings       (récupération enregistrement)
```

**Authentification** : OAuth 2.0

#### 2. AssemblyAI API
```
Meeting Intelligence ──HTTP──> AssemblyAI
                     <────────
                     
Workflow :
1. POST /upload        (upload fichier audio)
2. POST /transcript    (démarrage transcription)
3. GET /transcript/{id} (polling du résultat)
```

**Authentification** : API Key

#### 3. OpenAI API
```
Meeting Intelligence ──HTTP──> OpenAI API
                     <────────

Endpoints utilisés :
• POST /chat/completions  (appels LLM)

Modèle : gpt-4o-mini
```

**Authentification** : API Key (Bearer token)

### Architecture de Communication

```
┌────────────┐
│  Frontend  │
└─────┬──────┘
      │ HTTP/HTTPS
      │ REST API
      ▼
┌────────────────┐
│  FastAPI       │
│  (Backend)     │
└─────┬──────────┘
      │
      ├──────► PostgreSQL (SQL)
      │
      ├──────► Redis (TCP)
      │
      ├──────► Celery Workers (AMQP)
      │
      └──────► External APIs (HTTPS)
               • Zoom
               • AssemblyAI
               • OpenAI
```

---

## 🚀 Architecture de Déploiement

### Environnement de Développement

```
┌─────────────────────────────────────────┐
│         Developer Machine               │
│                                         │
│  ┌──────────────┐   ┌───────────────┐  │
│  │   Backend    │   │   Frontend    │  │
│  │   uvicorn    │   │   npm dev     │  │
│  │ localhost:8000   │ localhost:3000│  │
│  └──────────────┘   └───────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │     Docker Compose               │  │
│  │  ┌──────────┐    ┌──────────┐   │  │
│  │  │PostgreSQL│    │  Redis   │   │  │
│  │  │  :5432   │    │  :6379   │   │  │
│  │  └──────────┘    └──────────┘   │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

**Commandes** :
```bash
# Base de données
docker-compose up -d

# Backend
cd backend
uvicorn app.main:app --reload

# Frontend
cd frontend
npm run dev
```

### Environnement de Production (Proposition)

```
                   ┌─────────────────┐
                   │   Load Balancer │
                   │     (Nginx)     │
                   └────────┬────────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
      ┌───────────────┐          ┌───────────────┐
      │  FastAPI      │          │  FastAPI      │
      │  Instance 1   │          │  Instance 2   │
      └───────┬───────┘          └───────┬───────┘
              │                           │
              └────────────┬──────────────┘
                           │
              ┌────────────┴─────────────┐
              │                          │
              ▼                          ▼
      ┌──────────────┐          ┌──────────────┐
      │  PostgreSQL  │          │    Redis     │
      │   (Primary)  │          │   Cluster    │
      └──────┬───────┘          └──────────────┘
             │
             ▼
      ┌──────────────┐
      │  PostgreSQL  │
      │  (Replica)   │
      └──────────────┘

      ┌──────────────────────────────────┐
      │     Celery Workers               │
      │  ┌────────┐  ┌────────┐ ┌──────┐│
      │  │Worker 1│  │Worker 2│ │Worker│││
      │  └────────┘  └────────┘ └──────┘│
      └──────────────────────────────────┘
```

**Infrastructure as Code (Docker Compose Production)** :

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://...
    deploy:
      replicas: 3  # 3 instances
    depends_on:
      - postgres
      - redis

  celery_worker:
    build: ./backend
    command: celery -A app.tasks.celery_app worker
    deploy:
      replicas: 2
    depends_on:
      - redis
      - postgres

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
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Scalabilité

**Composants scalables horizontalement** :
1. ✅ Backend API (FastAPI) : Stateless, facile à répliquer
2. ✅ Celery Workers : Ajout de workers selon la charge
3. ✅ Frontend : CDN + serveurs multiples

**Composants nécessitant scaling vertical** :
1. ⚠️ PostgreSQL : Primary/Replica, partitionnement
2. ⚠️ Redis : Clustering Redis pour haute disponibilité

---

## 📊 Diagrammes d'Architecture

### Diagramme de Séquence : Analyse de Réunion

```
User    Frontend    Backend     Database    Celery     OpenAI
 │         │          │            │          │          │
 │─────────┤          │            │          │          │
 │ Clique "Analyser" │            │          │          │
 │         │──────────►           │          │          │
 │         │ POST /analyze        │          │          │
 │         │          │────────────►         │          │
 │         │          │  Vérifie meeting     │          │
 │         │          │◄────────────         │          │
 │         │          │            │          │          │
 │         │          │─────────────────────►│          │
 │         │          │  Enqueue task        │          │
 │         │          │◄─────────────────────│          │
 │         │◄──────────                      │          │
 │         │ 202 Accepted                    │          │
 │◄─────────                                 │          │
 │                                            │          │
 │                                       Traitement      │
 │                                       asynchone       │
 │                                            │          │
 │                                            │──────────►
 │                                            │ Extract  │
 │                                            │ Actions  │
 │                                            │◄─────────│
 │                                            │          │
 │                                            │──────────►
 │                                            │ Extract  │
 │                                            │ Decisions│
 │                                            │◄─────────│
 │                                            │          │
 │                                            │──────────►
 │                                            │ Extract  │
 │                                            │ Questions│
 │                                            │◄─────────│
 │                                            │          │
 │                                            │──────────►
 │                                            │ Generate │
 │                                            │ Summary  │
 │                                            │◄─────────│
 │                                            │          │
 │                                            │────────────►
 │                                            │  Save results
 │                                            │◄────────────
 │                                            │
 │─────────►                                  │
 │ Refresh page                               │
 │◄─────────                                  │
 │ Résultats affichés                         │
```

### Diagramme de Composants

```
┌───────────────────────────────────────────────────────┐
│                    FRONTEND (React)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐ │
│  │  Dashboard  │  │ Meeting List│  │   Detail     │ │
│  └─────────────┘  └─────────────┘  └──────────────┘ │
└────────────────────────┬──────────────────────────────┘
                         │ REST API
                         ▼
┌───────────────────────────────────────────────────────┐
│                  BACKEND API (FastAPI)                │
│  ┌──────────────────────────────────────────────┐    │
│  │          API Endpoints (meetings.py)         │    │
│  └─────────────────────┬────────────────────────┘    │
│                        │                              │
│  ┌─────────────────────▼───────────────────────┐     │
│  │       Meeting Intelligence Orchestrator       │    │
│  └─────────────────────┬────────────────────────┘    │
│                        │                              │
│       ┌────────────────┼────────────────┐            │
│       ▼                ▼                ▼            │
│  ┌─────────┐    ┌──────────┐    ┌─────────┐        │
│  │ Action  │    │ Decision │    │ Question│        │
│  │ Agent   │    │  Agent   │    │  Agent  │        │
│  └─────────┘    └──────────┘    └─────────┘        │
│                        │                              │
│                        ▼                              │
│              ┌──────────────────┐                    │
│              │  Summary Agent   │                    │
│              └──────────────────┘                    │
└───────────────────────┬──────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
┌──────────────┐ ┌──────────┐  ┌─────────────┐
│  PostgreSQL  │ │  Celery  │  │  OpenAI API │
└──────────────┘ └──────────┘  └─────────────┘
```

---

## 🔒 Considérations de Sécurité

### 1. Authentification et Autorisation
- **JWT Tokens** pour l'authentification
- **RBAC** (Role-Based Access Control)
- Chaque utilisateur ne voit que ses réunions

### 2. Protection des Données
- **Chiffrement en transit** : HTTPS/TLS
- **Chiffrement au repos** : PostgreSQL encryption
- **Secrets management** : Variables d'environnement, pas de hardcoding

### 3. Validation des Entrées
- **Pydantic schemas** pour validation automatique
- **SQL Injection protection** : ORM (SQLAlchemy)
- **XSS protection** : Sanitization des outputs

### 4. Rate Limiting
- Limitation des appels API (100 req/min par utilisateur)
- Protection contre les abus

---

## 📈 Monitoring et Observabilité

### Logs
- **Structured logging** : Format JSON
- **Niveaux** : DEBUG, INFO, WARNING, ERROR
- **Centralisation** : ELK Stack ou CloudWatch

### Métriques
- **Performance** : Temps de réponse API
- **Usage** : Nombre de réunions analysées/jour
- **Coûts** : Appels OpenAI, coûts cloud

### Alertes
- **Erreurs LLM** : Si taux d'échec > 5%
- **Base de données** : Si latence > 200ms
- **Celery** : Si queue > 100 tâches

---

**Date de dernière mise à jour** : Janvier 2026  
**Version** : 1.0.0
