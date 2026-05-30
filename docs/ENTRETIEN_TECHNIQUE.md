# Syntra.ai —

---

## 1. Présentation du projet

### Nom du projet
**Syntra.ai** — une plateforme d'intelligence de réunion.

### Contexte
J'ai développé ce projet en autonomie pour explorer plusieurs sujets qui m'intéressaient en parallèle : l'architecture multi-agents avec des LLM, le traitement asynchrone à grande échelle, et la construction d'un produit SaaS de bout en bout. J'ai choisi le domaine de la réunion parce qu'il s'agit d'un problème concret et universel : les réunions produisent une énorme quantité d'information, mais cette information reste souvent perdue ou éparpillée.

### Problème que je voulais résoudre
Après une réunion d'une heure, retrouver les décisions prises, les tâches attribuées et les questions laissées ouvertes prend facilement 15 à 20 minutes. Ce travail est fastidieux, répétitif et source d'oublis. J'ai voulu automatiser entièrement cette étape.

### Objectif principal
Transformer un enregistrement audio ou vidéo de réunion en un rapport structuré exploitable : résumé exécutif, décisions prises, actions assignées, et questions non résolues — le tout disponible en quelques minutes après la fin de la réunion.

---

## 2. Fonctionnalités principales

- **Transcription automatique avec identification des locuteurs**
  J'utilise l'API AssemblyAI avec la diarisation des locuteurs activée. Le système reconnaît qui parle à quel moment et retourne des segments horodatés avec un score de confiance.

- **Analyse IA multi-agents en parallèle**
  Quatre agents LLM spécialisés analysent la transcription simultanément : un pour les actions, un pour les décisions, un pour les questions ouvertes, et un pour le résumé global. L'exécution est parallélisée avec `asyncio.gather()`.

- **Import et intégration Zoom**
  L'utilisateur peut connecter son compte Zoom via OAuth 2.0. Le système récupère automatiquement les enregistrements, télécharge l'audio et lance le pipeline de traitement. Un webhook Zoom peut aussi déclencher le traitement dès qu'un enregistrement est disponible.

- **Upload manuel de fichiers audio/vidéo**
  En dehors de Zoom, l'utilisateur peut uploader directement un fichier (mp4, m4a, wav, etc.) depuis le dashboard.

- **Suivi des actions**
  Chaque action extraite peut être consultée, mise à jour (statut : à faire / en cours / terminé) et filtrée depuis l'interface.

- **Partage par email**
  Le rapport peut être partagé par email aux participants et aux personnes assignées à des actions, avec un template HTML professionnel.

- **Résumé hebdomadaire automatique**
  Chaque lundi à 9h UTC, un email récapitulatif des réunions de la semaine et des actions ouvertes est envoyé automatiquement aux utilisateurs, via Celery Beat.

- **Recherche full-text**
  Un endpoint de recherche globale permet de retrouver des réunions par mots-clés dans les titres et les contenus.

- **Authentification complète**
  Inscription avec vérification email, connexion JWT, réinitialisation de mot de passe par token — le tout avec des tokens à usage unique et expiration.

---

## 3. Stack technique

### Langages
- **Python** (backend)
- **JavaScript / JSX** (frontend)
- **SQL** (migrations Alembic)

### Frameworks & bibliothèques
| Couche | Technologie |
|---|---|
| API | FastAPI 0.109 + Uvicorn |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth | python-jose (JWT) + passlib Argon2 |
| LLM | LangChain 0.1 + OpenAI GPT-4o-mini |
| Transcription | AssemblyAI SDK |
| Tâches async | Celery 5.3 + Redis |
| Email | SMTP + Jinja2 (templates HTML) |
| Frontend | React 18 + React Router 6 + Tailwind CSS |
| Build | Vite |
| Tests E2E | Playwright |

### Services et outils externes
- **OpenAI** (GPT-4o-mini) — via OpenRouter pour la flexibilité de provider
- **AssemblyAI** — transcription et diarisation
- **Zoom API** — OAuth 2.0, recordings, webhooks
- **Redis** — broker Celery et backend de résultats
- **PostgreSQL** — base de données principale
- **Docker Compose** — orchestration locale de 6 services

### Pourquoi ces choix ?
- **FastAPI** : async natif, validation automatique avec Pydantic, génération OpenAPI — idéal pour une API où les performances comptent.
- **Celery + Redis** : la transcription et l'analyse LLM peuvent prendre plusieurs dizaines de secondes. Je ne pouvais pas bloquer une requête HTTP. Celery me permet de détacher ce traitement et de le suivre par polling côté frontend.
- **GPT-4o-mini** : bon compromis coût / qualité pour de la structuration de texte. Je n'avais pas besoin de GPT-4 pour extraire des actions et des décisions d'une transcription.
- **AssemblyAI** : meilleure diarisation des locuteurs que Whisper sur des enregistrements multi-personnes, avec une API simple et fiable.
- **Argon2** pour les mots de passe : algorithme recommandé actuellement, résistant aux attaques GPU.

---

## 4. Architecture du projet

### Organisation du code

```
meeting-intelligence/
├── backend/
│   ├── app/
│   │   ├── agents/        # Logique IA (orchestrator + 4 agents)
│   │   ├── api/           # Routes FastAPI (auth, meetings, zoom, webhooks)
│   │   ├── models/        # Modèles SQLAlchemy (User, Meeting, Summary, ActionItem...)
│   │   ├── schemas/       # Schémas Pydantic (validation entrée/sortie)
│   │   ├── services/      # Logique métier (auth, email, transcription, zoom)
│   │   ├── tasks/         # Workers Celery (traitement réunion, emails hebdo)
│   │   └── utils/         # Helpers (sécurité, formatage...)
│   └── alembic/           # Migrations DB
├── frontend/
│   └── src/
│       ├── pages/         # Vues (Dashboard, MeetingDetail, SignIn...)
│       ├── components/    # Composants réutilisables
│       ├── api/           # Client Axios + modules d'appels API
│       └── context/       # AuthContext (état global d'authentification)
└── docker-compose.yml     # 6 services : postgres, redis, backend, worker, beat, frontend
```

### Composants principaux
- **FastAPI** expose une API REST versionnée, avec séparation claire entre routes, services et modèles.
- **Services** : chaque responsabilité métier (auth, email, zoom, transcription) est encapsulée dans une classe de service indépendante.
- **Celery Workers** : deux rôles distincts — le worker traite les tâches à la demande, le beat déclenche les tâches planifiées.
- **React frontend** : architecture par pages, avec un `AuthContext` global qui gère le token JWT et l'état d'authentification. Un intercepteur Axios injecte automatiquement le token dans chaque requête.

### Flux de données

**Flux principal (analyse d'une réunion Zoom) :**
```
1. L'utilisateur connecte Zoom → OAuth callback → tokens stockés en base
2. Il importe un enregistrement → POST /zoom/import
3. Le backend récupère l'URL audio signé depuis l'API Zoom
4. La tâche Celery `process_zoom_meeting_recording` est mise en queue
5. AssemblyAI transcrit l'audio et retourne les segments avec locuteurs
6. La tâche `process_meeting_analysis_internal` est enchaînée
7. L'orchestrateur lance 4 agents LLM en parallèle (asyncio.gather)
8. Le résumé final est sauvegardé en base (Summary + ActionItems)
9. Le frontend poll /meetings/{id}/summary jusqu'à completion
10. Le rapport est affiché avec résumé, actions, décisions, questions
```

**Flux webhook Zoom :**
```
Zoom → POST /webhooks/zoom (signature HMAC-SHA256 vérifiée)
     → Création de la réunion en base
     → Déclenchement automatique du pipeline de traitement
```

---

## 5. Partie IA — Architecture multi-agents

### Pourquoi une architecture multi-agents ?

La première question qu'on me pose souvent : "Pourquoi ne pas envoyer la transcription à un seul LLM et lui demander de tout faire ?"

La réponse est simple : un prompt qui fait tout à la fois donne des résultats médiocres sur tout. En séparant les responsabilités, chaque agent peut avoir un prompt très ciblé, des critères d'inclusion/exclusion précis, et un schéma de sortie adapté à sa tâche. La qualité des extractions est nettement supérieure, et le système est plus facile à déboguer et à faire évoluer indépendamment.

---

### Modèle utilisé
**GPT-4o-mini** via l'API OpenAI. J'ai configuré le LLM avec `temperature=0` pour avoir des sorties déterministes — c'est important ici, je veux de la structuration, pas de la créativité. Le provider passe par OpenRouter (`openrouter.ai/api/v1`) ce qui me permet de switcher de modèle (Claude, Mistral, etc.) sans changer le code, juste une variable d'environnement.

```python
# llm_provider.py
def get_openrouter_llm():
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_base="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENAI_API_KEY")
    )
```

---

### Les 4 agents et leur rôle

| Agent | Rôle | Sortie Pydantic |
|---|---|---|
| `ActionItemsAgent` | Extrait les tâches : qui fait quoi, deadline, priorité | `List[ActionItem]` |
| `DecisionsAgent` | Identifie les décisions actées (consensus, validation, rejet) | `List[Decision]` |
| `QuestionsAgent` | Repère les questions restées sans réponse claire | `List[UnansweredQuestion]` |
| `SummaryAgent` | Synthétise les 3 extractions en un rapport Markdown complet | `MeetingSummary` |

Chaque agent est une classe Python indépendante avec :
- son propre `ChatPromptTemplate` (system prompt + user prompt)
- son propre schéma Pydantic de sortie
- des critères d'inclusion ET d'exclusion explicites dans le prompt

Par exemple, le `QuestionsAgent` exclut explicitement les questions rhétoriques et celles qui ont trouvé une réponse dans les 2 minutes. Et l'`ActionItemsAgent` capture aussi les assignations implicites ("il faut qu'on fasse X"), pas seulement les phrases directes.

---

### La structure d'un agent (exemple : ActionItemsAgent)

```python
class ActionItem(BaseModel):
    action: str
    assigned_to: str
    deadline: str
    priority: str  # Haute / Moyenne / Basse
    context: str

class ActionItems(BaseModel):
    items: List[ActionItem]

class ActionItemsAgent:
    def __init__(self, llm):
        self.parser = PydanticOutputParser(pydantic_object=ActionItems)
        self.prompt = ChatPromptTemplate.from_messages([...])

    async def extract(self, transcription: str):
        chain = self.prompt | self.llm | self.parser
        result = await chain.ainvoke({
            "transcription": transcription,
            "format_instructions": self.parser.get_format_instructions()
        })
        return result.model_dump()
```

Le `PydanticOutputParser` injecte automatiquement les instructions de format dans le prompt, et valide que la sortie du LLM correspond bien au schéma attendu. Si le LLM hallucine du JSON mal formé, ça lève une exception catchée proprement — pas de données corrompues en base.

---

### L'orchestrateur : exécution parallèle

L'`MeetingIntelligenceOrchestrator` coordonne tout. Le point clé : les 3 agents d'extraction tournent **en parallèle** avec `asyncio.gather()`, pas séquentiellement. Ça réduit le temps d'analyse d'un facteur ~3.

```python
# orchestrator.py
async def process_meeting(self, transcription: str, metadata: dict):
    # Étape 1 — 3 agents en parallèle (le gain de perf principal)
    results = await asyncio.gather(
        self.action_agent.extract(transcription),
        self.decision_agent.extract(transcription),
        self.question_agent.extract(transcription),
    )
    actions, decisions, questions = results

    # Étape 2 — synthèse finale avec tout le contexte
    summary = await self.summary_agent.generate(
        transcription=transcription,
        actions=actions,
        decisions=decisions,
        questions=questions,
        metadata=metadata
    )
    return {"actions": actions, "decisions": decisions, "questions": questions, "summary": summary}
```

Le `SummaryAgent` est délibérément séquentiel : il a besoin des outputs des 3 premiers agents pour générer un rapport cohérent. C'est un design en deux phases : extraction parallèle → synthèse.

---

### Intégration dans le pipeline Celery

Le pipeline d'analyse est déclenché depuis une tâche Celery (`process_meeting_analysis_internal`). Celery est synchrone par nature, mais mes agents utilisent `async/await`. J'ai résolu ça avec `asyncio.run()` :

```python
# meeting_tasks.py
def process_meeting_analysis_internal(meeting_id: int, db):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, ...)
    orchestrator = MeetingIntelligenceOrchestrator(llm)

    # Pont entre le monde synchrone (Celery) et async (agents LangChain)
    results = asyncio.run(orchestrator.process_meeting(
        transcription=meeting.transcription.full_text,
        metadata={"title": meeting.title, "duration": meeting.duration_minutes}
    ))

    # Persistance en base
    db.add(Summary(meeting_id=meeting_id, ...))
    for action in results["actions"]["items"]:
        db.add(ActionItem(meeting_id=meeting_id, ...))
    db.commit()
```

Le résultat final (Summary + ActionItems) est sauvegardé en base. Le frontend poll l'endpoint `/meetings/{id}/summary` jusqu'à ce que le statut passe à `completed`.

---

## 6. Défis rencontrés

### 1. Async dans Celery
Celery utilise un modèle synchrone, mais mes agents LLM utilisent `async/await`. J'ai dû encapsuler les appels avec `asyncio.run()` dans les tâches Celery pour les faire cohabiter proprement.

### 2. Gestion des tokens Zoom
L'API Zoom utilise des tokens d'accès de courte durée avec refresh. J'ai implémenté une logique d'auto-refresh : si le token expire dans moins de 5 minutes, il est rafraîchi automatiquement avant chaque appel. Ça évite les erreurs silencieuses en production.

### 3. Qualité des sorties LLM
Les premiers prompts donnaient des sorties inconsistantes. J'ai résolu ça en combinant deux approches : des prompts très explicites avec des exemples de ce qu'il faut inclure ET exclure, et l'utilisation de `PydanticOutputParser` qui force le LLM à produire du JSON valide ou échoue proprement.

### 4. Signature des webhooks Zoom
Zoom signe ses webhooks avec HMAC-SHA256. J'ai implémenté la vérification côté serveur pour rejeter tout événement non authentifié, et j'ai géré séparément le cas particulier de la validation d'URL (challenge-response) que Zoom exige lors de la configuration du webhook.

### 5. Polling côté frontend
L'analyse d'une réunion peut prendre 30 à 60 secondes. Plutôt que du WebSocket (plus complexe à déployer), j'ai opté pour du polling intelligent avec backoff côté React — un helper `createPolling()` qui interroge l'API à intervalles réguliers jusqu'à completion ou timeout.

### Ce que j'ai appris
- Comment concevoir une architecture qui découple proprement le traitement long (async workers) de l'API web.
- Que les prompts d'agents spécialisés avec des critères d'exclusion explicites donnent de bien meilleurs résultats que des prompts génériques.
- L'importance de valider les données à la frontière (webhooks, inputs utilisateur) plutôt que d'assainir en interne.

---

## 7. Améliorations possibles

- **WebSockets** à la place du polling pour une expérience plus réactive lors de l'analyse.
- **Streaming des réponses LLM** pour afficher le rapport progressivement plutôt qu'en une fois.
- **Choix du modèle LLM** dans l'UI — permettre à l'utilisateur de choisir entre GPT-4o-mini, Claude, Mistral selon son budget et ses besoins.
- **Diarisation améliorée** : associer les labels "Speaker 1", "Speaker 2" aux vrais prénoms des participants via la liste de participants Zoom.
- **Export PDF** : la base est là (ReportLab est dans les dépendances), mais l'implémentation n'est pas finalisée.
- **Tests unitaires** plus complets sur les agents — notamment des tests de regression sur des transcriptions types pour détecter les régressions de prompt.
- **Rate limiting** sur les endpoints d'auth pour se protéger contre le brute-force.
- **Support multi-langue** : AssemblyAI détecte la langue automatiquement, mais les prompts agents sont actuellement en français/anglais mélangé — il faudrait adapter les prompts à la langue détectée.

---

## 8. Démo rapide — pitch oral

> "Syntra.ai, c'est un outil qui prend un enregistrement de réunion et en extrait automatiquement ce qui compte : un résumé exécutif, les décisions prises, les actions avec qui fait quoi et pour quand, et les questions qui sont restées sans réponse. Techniquement, c'est FastAPI + Celery pour le traitement asynchrone, AssemblyAI pour la transcription avec identification des locuteurs, et quatre agents GPT-4o-mini qui travaillent en parallèle via LangChain. Le frontend est en React avec Tailwind. J'ai aussi intégré Zoom — l'utilisateur connecte son compte et le système récupère et traite automatiquement ses enregistrements, avec un webhook qui déclenche le pipeline dès qu'un enregistrement est disponible."
