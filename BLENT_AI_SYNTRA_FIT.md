# 🎯 Alignement de profil : Stage Développeur Python IA chez BLENT.AI

Ce document met en évidence comment mes compétences et mon projet **Syntra.ai** (Plateforme d'Intelligence de Réunion) répondent parfaitement aux exigences techniques et aux missions du poste chez BLENT.AI.

---

## 1. Adéquation avec le Profil Recherché

| Exigences BLENT.AI | Mon Profil & Implémentation dans Syntra.ai |
| :--- | :--- |
| **Maîtrise Python & API REST** | Conception et développement complet du backend de Syntra.ai en **Python 3.11** avec **FastAPI**, incluant des routes RESTful complexes et la validation stricte des données via **Pydantic**. |
| **Connaissances ORM** | Modélisation de la base de données relationnelle (PostgreSQL) en utilisant **SQLAlchemy** (Async) et gestion des migrations de schémas avec **Alembic**. |
| **Programmation asynchrone (Bonus)** | C'est le cœur de mon architecture : utilisation intensive d'**asyncio** et de **FastAPI** pour traiter en parallèle l'extraction de données via des LLMs sans bloquer le thread principal. |
| **Outils DevOps (Bonus)** | Conteneurisation de l'ensemble des micro-services (Backend, Frontend, Redis, Celery, Postgres) via **Docker** et **Docker Compose** pour assurer la reproductibilité des environnements. |
| **Utilisation d'outils d'IA** | Utilisation quotidienne de GitHub Copilot / LLMs (Claude/GPT) pour accélérer le développement, générer des tests et optimiser mon code Python. |

---

## 2. Capacité à répondre aux Missions du Poste

### 🛠️ Mission 1 : Développement, Maintenance & Qualité
* **Code propre et structuré** : L'architecture de Syntra.ai respecte la séparation des préoccupations (Routes, Services, Agents IA, Models, Tasks).
* **Documentation** : La documentation de l'API est auto-générée via le standard OpenAPI/Swagger de FastAPI. J'attache une grande importance aux *docstrings* et au typage strict (Type Hints Python).
* **Robustesse** : Gestion rigoureuse des erreurs d'API et asynchronisme (try/except sur les tâches Celery) pour garantir la stabilité de la plateforme.

### 🤖 Mission 2 : Intégration IA & Automatisation
* **Orchestration de LLM** : J'ai conçu un pipeline IA avancé utilisant **LangChain**. Je ne me contente pas d'appels API basiques : j'ai implémenté une **architecture multi-agents** (Agents spécialisés pour les Actions, Décisions, Questions) tournant en parallèle pour synthétiser des données brutes.
* **Automatisation de processus** : Utilisation de **Celery + Redis** pour automatiser les tâches d'arrière-plan lourdes (Transcription via AssemblyAI, exécution des LLMs, envoi automatique d'emails via Brevo SMTP).

---

## 3. Pourquoi ce match est idéal ?

Mon expérience sur **Syntra.ai** prouve ma capacité à :
1. **Être autonome** sur des problématiques complexes de backend Python.
2. **Gérer l'incertitude et la latence** inhérentes aux APIs d'Intelligence Artificielle (via l'architecture Task-Driven avec Celery).
3. **Apporter une valeur technique immédiate** sur les sujets de l'automatisation IA, du NLP et de l'orchestration de modèles de langage, qui sont au cœur de la mission de conseil de BLENT.AI.

Je suis particulièrement enthousiaste à l'idée d'appliquer ces compétences à vos projets clients et d'évoluer aux côtés de votre Lead Tech.
