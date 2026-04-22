# Syntra.ai - Documentation Conceptuelle

## 📚 Table des Matières

1. [Concepts Fondamentaux](#concepts-fondamentaux)
2. [Modèle de Domaine](#modèle-de-domaine)
3. [Workflows Métier](#workflows-métier)
4. [Agents Intelligents](#agents-intelligents)
5. [Cycle de Vie des Données](#cycle-de-vie-des-données)
6. [Concepts d'Intelligence Artificielle](#concepts-dintelligence-artificielle)

---

## 🎓 Concepts Fondamentaux

### Syntra.ai
**Définition** : Système d'analyse automatisée de réunions utilisant l'intelligence artificielle pour extraire de l'information structurée et actionnable à partir de transcriptions audio.

### Principes de Base

#### 1. Séparation des Préoccupations
Chaque agent IA est spécialisé dans une tâche unique :
- **Action Agent** : Extraction des tâches et actions
- **Decision Agent** : Identification des décisions prises
- **Question Agent** : Détection des questions et leur statut
- **Summary Agent** : Synthèse globale

#### 2. Traitement Asynchrone
Les analyses longues sont traitées en arrière-plan pour ne pas bloquer l'utilisateur.

#### 3. Architecture Événementielle
Le système réagit aux événements (fin de réunion, nouvelle transcription, etc.)

---

## 🏗️ Modèle de Domaine

### Entités Principales

#### 1. **User (Utilisateur)**
Représente un utilisateur du système.

**Attributs** :
- Identité : email, nom
- Authentification : token Zoom
- Relations : possède plusieurs réunions

**Responsabilités** :
- Organiser des réunions
- Accéder à l'historique de ses réunions
- Gérer ses actions assignées

#### 2. **Meeting (Réunion)**
Entité centrale du système représentant une réunion.

**Attributs** :
- Informations de base : titre, date, durée
- État : scheduled, in_progress, completed
- Identifiant Zoom
- Relations : appartient à un utilisateur

**Cycle de vie** :
```
SCHEDULED → IN_PROGRESS → COMPLETED
```

**Responsabilités** :
- Contenir la transcription
- Agréger les analyses (actions, décisions, questions)
- Fournir un résumé

#### 3. **Transcription**
Représente le texte extrait de l'audio de la réunion.

**Attributs** :
- Texte complet
- Segments par locuteur (speaker diarization)
- Timestamps

**Caractéristiques** :
- Relation 1:1 avec Meeting
- Créée après la fin de la réunion
- Immutable une fois créée

#### 4. **Action Item (Élément d'Action)**
Représente une tâche ou action à entreprendre identifiée pendant la réunion.

**Attributs** :
- Description de l'action
- Personne assignée
- Deadline (échéance)
- Priorité (haute, moyenne, basse)
- Statut (pending, in_progress, completed)

**Énumérations** :
```
Priority: HIGH | MEDIUM | LOW
Status: PENDING | IN_PROGRESS | COMPLETED | CANCELLED
```

#### 5. **Decision (Décision)**
Représente une décision prise pendant la réunion.

**Attributs** :
- Description de la décision
- Contexte
- Participants ayant validé
- Impact estimé

#### 6. **Question**
Représente une question soulevée pendant la réunion.

**Attributs** :
- Question formulée
- Personne qui l'a posée
- Réponse (si disponible)
- Statut : answered / unanswered

#### 7. **Summary (Résumé)**
Synthèse complète de la réunion.

**Attributs** :
- Résumé exécutif (2-3 paragraphes)
- Liste des décisions
- Liste des questions
- Rapport complet en Markdown
- URL du PDF généré

---

## 🔄 Workflows Métier

### Workflow 1 : Création et Planification de Réunion

```
┌─────────────┐
│   Début     │
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  Utilisateur crée   │
│  une réunion        │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Synchronisation    │
│  avec Zoom API      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Meeting créé avec  │
│  statut SCHEDULED   │
└──────┬──────────────┘
       │
       ▼
┌─────────────┐
│     Fin     │
└─────────────┘
```

### Workflow 2 : Traitement Post-Réunion (Principal)

```
┌──────────────────┐
│  Réunion se      │
│  termine         │
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│  Enregistrement      │
│  disponible sur Zoom │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Téléchargement      │
│  fichier audio       │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Envoi à             │
│  AssemblyAI pour     │
│  transcription       │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Réception de la     │
│  transcription       │
│  complète            │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Sauvegarde dans     │
│  base de données     │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Déclenchement       │
│  analyse IA          │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────────────┐
│  ORCHESTRATEUR               │
│  ┌────────────────────────┐  │
│  │ Exécution parallèle    │  │
│  │ des 3 agents :         │  │
│  │                        │  │
│  │ • Action Agent    ──┐  │  │
│  │ • Decision Agent  ──┤  │  │
│  │ • Question Agent  ──┤  │  │
│  │                     │  │  │
│  │ Attente résultats ◄─┘  │  │
│  └────────────────────────┘  │
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────┐
│  Summary Agent       │
│  (utilise les 3      │
│  résultats précéd.)  │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Sauvegarde des      │
│  résultats :         │
│  • Actions           │
│  • Décisions         │
│  • Questions         │
│  • Résumé            │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Génération PDF      │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Envoi emails aux    │
│  participants        │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Meeting marqué      │
│  comme COMPLETED     │
└────────┬─────────────┘
         │
         ▼
┌─────────────┐
│     Fin     │
└─────────────┘
```

### Workflow 3 : Gestion des Actions

```
┌──────────────────┐
│  Action créée    │
│  (statut PENDING)│
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Notification    │
│  à l'assigné     │
└────────┬─────────┘
         │
         ▼
┌──────────────────────────┐
│  Assigné consulte        │
│  ses actions             │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Changement statut       │
│  → IN_PROGRESS           │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Travail sur l'action    │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Changement statut       │
│  → COMPLETED             │
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Notification au         │
│  responsable réunion     │
└────────┬─────────────────┘
         │
         ▼
┌─────────────┐
│     Fin     │
└─────────────┘
```

---

## 🤖 Agents Intelligents

### Concept d'Agent
Un **Agent** est une entité autonome spécialisée dans une tâche d'analyse spécifique. Chaque agent :
- Reçoit une transcription en entrée
- Utilise un LLM (Large Language Model) avec un prompt optimisé
- Produit une sortie structurée et prévisible

### Architecture Multi-Agents

```
                    ┌─────────────────────┐
                    │   ORCHESTRATEUR     │
                    │  (Coordinateur)     │
                    └──────────┬──────────┘
                               │
                               │ Distribue la transcription
                               │
         ┌─────────────────────┼─────────────────────┐
         │                     │                     │
         ▼                     ▼                     ▼
┌────────────────┐   ┌────────────────┐   ┌────────────────┐
│ ACTION AGENT   │   │ DECISION AGENT │   │ QUESTION AGENT │
│                │   │                │   │                │
│ Extrait les    │   │ Identifie les  │   │ Détecte les    │
│ tâches à faire │   │ décisions      │   │ questions      │
│                │   │ prises         │   │ posées         │
└────────┬───────┘   └────────┬───────┘   └────────┬───────┘
         │                    │                     │
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   SUMMARY AGENT     │
                    │                     │
                    │ Agrège et synthétise│
                    │ tous les résultats  │
                    └─────────────────────┘
```

### 1. Action Agent

**Objectif** : Identifier toutes les actions concrètes mentionnées dans la réunion.

**Critères d'extraction** :
- Verbes d'action (préparer, envoyer, appeler, vérifier...)
- Mention d'une personne responsable
- Contexte temporel (deadline)

**Format de sortie** :
```json
{
  "items": [
    {
      "action": "Préparer le rapport Q4",
      "assigned_to": "Marie Dupont",
      "deadline": "Vendredi prochain",
      "priority": "HIGH",
      "context": "Pour la réunion du board"
    }
  ]
}
```

**Prompt structuré** :
```
Tu es un expert en extraction d'actions à partir de transcriptions de réunions.

Analyse la transcription suivante et identifie TOUTES les actions mentionnées.

Pour chaque action, détermine :
- La description précise de l'action
- La personne assignée (si mentionnée)
- La deadline (si mentionnée)
- La priorité (HIGH/MEDIUM/LOW)

Transcription :
{transcription}

Retourne un JSON structuré.
```

### 2. Decision Agent

**Objectif** : Capturer toutes les décisions prises pendant la réunion.

**Critères d'identification** :
- Expressions de consensus ("nous avons décidé", "il est convenu")
- Choix entre plusieurs options
- Validation explicite

**Format de sortie** :
```json
{
  "items": [
    {
      "decision": "Utilisation de PostgreSQL pour la base de données",
      "context": "Discussion sur l'architecture technique",
      "participants": ["Alice", "Bob"],
      "impact": "Décision technique majeure"
    }
  ]
}
```

### 3. Question Agent

**Objectif** : Lister toutes les questions soulevées et identifier si elles ont été répondues.

**Critères** :
- Formulation interrogative
- Vérification de réponse dans la suite de la transcription
- Classification du statut

**Format de sortie** :
```json
{
  "items": [
    {
      "question": "Quel est le budget alloué au projet ?",
      "asked_by": "Jean Martin",
      "answered": true,
      "answer": "50 000 euros sur 6 mois",
      "timestamp": "10:23"
    },
    {
      "question": "Qui sera le point de contact côté client ?",
      "asked_by": "Sophie Bernard",
      "answered": false,
      "answer": null,
      "timestamp": "15:42"
    }
  ]
}
```

### 4. Summary Agent

**Objectif** : Créer une synthèse cohérente de toute la réunion en agrégeant les résultats des autres agents.

**Entrées** :
- Transcription complète
- Actions extraites
- Décisions identifiées
- Questions listées
- Métadonnées (titre, durée, participants)

**Format de sortie** :
```json
{
  "executive_summary": "Réunion de planification du projet X. L'équipe a validé l'architecture technique et réparti les premières tâches...",
  "key_points": [
    "Validation de l'architecture PostgreSQL + FastAPI",
    "Planning établi pour les 2 prochaines semaines",
    "3 questions restent en suspens"
  ],
  "full_markdown": "# Résumé de Réunion\n\n## Résumé Exécutif\n..."
}
```

---

## 🔄 Cycle de Vie des Données

### Phase 1 : Capture
```
Audio (Zoom) → Fichier MP4/WAV
```

### Phase 2 : Transcription
```
Audio → AssemblyAI API → Texte structuré avec speakers
```

### Phase 3 : Analyse
```
Transcription → Agents IA → Données structurées
                  ↓
        ┌─────────┼─────────┐
        ▼         ▼         ▼
    Actions  Décisions  Questions
```

### Phase 4 : Synthèse
```
Données structurées → Summary Agent → Résumé complet
```

### Phase 5 : Stockage
```
Résultats → Base de données PostgreSQL
         → Indexation pour recherche
```

### Phase 6 : Restitution
```
Base de données → API REST → Frontend
                → PDF
                → Email
```

---

## 🧠 Concepts d'Intelligence Artificielle

### LLM (Large Language Model)
**Définition** : Modèle de langage pré-entraîné capable de comprendre et générer du texte.

**Utilisation dans le projet** :
- OpenAI GPT-4o-mini pour l'analyse
- Choix basé sur : coût, vitesse, qualité

### Prompt Engineering
**Définition** : Art de formuler des instructions optimales pour obtenir les meilleurs résultats d'un LLM.

**Techniques utilisées** :
1. **Few-Shot Learning** : Fournir des exemples dans le prompt
2. **Chain of Thought** : Demander au modèle de raisonner étape par étape
3. **Structured Output** : Spécifier un format JSON attendu
4. **Role Playing** : Assigner un rôle ("Tu es un expert en...")

### Structured Output Generation
Contrairement à la génération de texte libre, nous forçons le LLM à produire du JSON structuré pour :
- Faciliter le parsing
- Garantir la cohérence
- Permettre la validation
- Faciliter l'intégration

### Orchestration
Coordination intelligente de plusieurs LLM calls :
- **Parallélisation** : Exécution simultanée des agents indépendants
- **Séquencement** : Summary Agent attend les résultats des autres
- **Gestion d'erreurs** : Retry logic et fallbacks

---

## 🔐 Concepts de Sécurité et Confidentialité

### Données Sensibles
Les transcriptions de réunions peuvent contenir :
- Informations stratégiques
- Données personnelles
- Secrets commerciaux

### Mesures de Protection
1. **Chiffrement** : Données chiffrées au repos et en transit
2. **Accès contrôlé** : Seul le propriétaire accède à ses réunions
3. **Rétention** : Politique de suppression après X jours (configurable)
4. **Anonymisation** : Option d'anonymiser les noms dans les exports

---

## 📊 Concepts de Performance

### Traitement Asynchrone avec Celery
- Les analyses IA sont longues (30s à 2min)
- Utilisation de files de tâches (task queues)
- L'utilisateur ne bloque pas, il est notifié à la fin

### Caching
- Résultats d'analyse mis en cache
- Évite les retraitements coûteux

### Optimisation LLM
- Utilisation du modèle le plus économique suffisant
- Limitation de la taille des prompts
- Batch processing quand possible

---

**Date de dernière mise à jour** : Janvier 2026  
**Version** : 1.0.0
