# Fiche projet - Syntra.ai

## 1. Présentation
Syntra.ai est une plateforme d'intelligence de réunion. Elle permet d'envoyer ou d'importer un enregistrement, de le transcrire, puis d'en extraire automatiquement un résumé, des décisions, des actions et des questions ouvertes.

## 2. Objectif
Le projet vise à réduire le temps de reprise après réunion en transformant une conversation longue en informations exploitables, structurées et partageables.

## 3. Vue technique
- Frontend: React
- Backend: FastAPI
- Base de données: PostgreSQL
- Tâches asynchrones: Celery + Redis
- IA: agents LLM spécialisés pour l'analyse et la synthèse
- Transcription: AssemblyAI
- Authentification: JWT avec vérification email

## 4. Architecture
Le système suit une organisation en couches:
- présentation: interface web et API
- application: orchestration des traitements
- domaine: agents IA et règles métier
- infrastructure: base de données, files de tâches et services externes

Cette séparation facilite la maintenance, les tests et l'évolution du projet.

## 5. Fonctionnement global
1. L'utilisateur se connecte et crée une réunion.
2. Un fichier audio ou vidéo est envoyé ou récupéré depuis Zoom.
3. Le backend lance la transcription.
4. Des agents IA analysent le contenu en parallèle.
5. Le système produit un rapport final avec résumé, décisions, actions et questions.
6. Le rapport peut être consulté ou partagé par email.

## 6. Lecture théorique
Le projet repose sur trois idées simples:
- automatiser le traitement d'information non structurée
- découper le raisonnement en étapes spécialisées
- séparer l'interface, la logique métier et les services techniques

## 7. Résultat attendu
Le résultat est un outil qui aide les équipes à capitaliser rapidement sur leurs réunions, avec une sortie claire, exploitable et centralisée.
