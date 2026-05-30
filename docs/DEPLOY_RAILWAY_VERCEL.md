# Plan de deploiement Railway + services free (Syntra.ai)

Objectif: deployer proprement tous les services et eviter les erreurs classiques (CORS, callback Zoom, jobs Celery, secrets manquants).

Services de l'app:
- API FastAPI
- PostgreSQL
- Redis
- Celery Worker
- Celery Beat
- Frontend Vite (React)

---

## 0) Sites free recommandes par service

Note: les offres gratuites changent souvent. Verifie les limites avant de lancer en production.

### Option A (la plus simple): Railway + Vercel
- API: Railway
- Worker: Railway
- Beat: Railway
- PostgreSQL: Railway plugin
- Redis: Railway plugin
- Frontend: Vercel (free)

Avantage: infra simple et coherente.
Risque: Railway n'est pas toujours 100% free selon periode/offre.

### Option B (max free, multi-fournisseurs)
- API: Render Free Web Service ou Koyeb Free
- Worker: Render Background Worker (free selon limites)
- Beat: Render Background Worker (instance dediee) ou cron externe
- PostgreSQL: Neon Free ou Supabase Free
- Redis: Upstash Free
- Frontend: Vercel Free ou Netlify Free

Avantage: cout minimal.
Risque: veille/sleep, quotas, cold starts, plus de complexite.

Recommendation pratique:
- MVP rapide: Option A.
- Cout minimal: Option B.

---

## 1) Pre-check avant de deployer (obligatoire)

### A. Verifications techniques
- API locale demarre sans erreur.
- Endpoint health OK: `GET /health` retourne `{"status":"healthy"}`.
- Frontend build local OK (`npm run build`).
- Migrations Alembic a jour (pas de migration locale en attente).
- Flux critiques testes: signup/login, upload meeting, analyse, reset password.

### B. Secrets et variables a preparer

Backend / Worker / Beat:
- DATABASE_URL
- REDIS_URL
- JWT_SECRET_KEY (forte cle, min 32 chars)
- ACCESS_TOKEN_EXPIRE_MINUTES (ex: 60)
- OPENAI_API_KEY
- OPENAI_BASE_URL (ex: `https://openrouter.ai/api/v1`)
- ASSEMBLYAI_API_KEY
- SMTP_HOST
- SMTP_PORT
- SMTP_USER
- SMTP_PASSWORD
- FROM_EMAIL
- FROM_NAME
- FRONTEND_URL (URL publique frontend)
- CORS_ORIGINS (liste CSV avec au minimum ton domaine frontend)
- ZOOM_CLIENT_ID
- ZOOM_CLIENT_SECRET
- ZOOM_REDIRECT_URI = `https://<ton-backend>.up.railway.app/api/zoom/callback`
- ZOOM_CONNECTED_REDIRECT_PATH (optionnel, ex `/dashboard`)

Frontend:
- VITE_API_URL = `https://<ton-backend>.up.railway.app/api`
- VITE_USE_MOCK_ZOOM=false (production)

### C. Verifications produit avant go-live
- Tu as un sender email valide chez ton provider SMTP (Brevo ou autre).
- Ton app Zoom OAuth est en mode correct (dev ou prod), avec bonne redirect URI.
- Tu as decide si les services Celery sont obligatoires au lancement.

---

## 2) Plan de deploiement Railway pas a pas

## Etape 1 - Backend API
- Cree un nouveau service Railway depuis le repo.
- Root Directory: `/backend`.
- Build: Dockerfile detecte automatiquement.
- Start command: laisser vide (ou `uvicorn app.main:app --host 0.0.0.0 --port $PORT`).
- Healthcheck path: `/health`.

Ajoute les variables backend (section 1B).

Important:
- Si Railway propose des commandes Node (`npm run build/start`), supprime-les.

## Etape 2 - PostgreSQL
- Ajoute un service PostgreSQL Railway.
- Lie la variable `DATABASE_URL` au backend.

Apres premier deploy backend:
- Ouvre le shell Railway du backend.
- Lance: `alembic upgrade head`.

## Etape 3 - Redis
- Ajoute un service Redis Railway.
- Lie `REDIS_URL` au backend.

## Etape 4 - Celery Worker
- Cree un 2e service Railway depuis le meme repo.
- Root Directory: `/backend`.
- Start command:
   `celery -A app.tasks.celery_app worker --loglevel=info -Q meetings --concurrency=2`
- Copie les memes variables que backend (surtout DATABASE_URL, REDIS_URL, OPENAI_*, ASSEMBLYAI_API_KEY, SMTP_*, FRONTEND_URL).

## Etape 5 - Celery Beat
- Cree un 3e service Railway depuis le meme repo.
- Root Directory: `/backend`.
- Start command:
   `celery -A app.tasks.celery_app beat --loglevel=info --pidfile=/tmp/celerybeat.pid`
- Copie les memes variables que backend.

## Etape 6 - Frontend (Vercel)
- Import repo dans Vercel.
- Root Directory: `/frontend`.
- Framework Preset: Vite.
- Build command: `npm run build`.
- Output directory: `dist`.
- Variables: `VITE_API_URL` (URL backend + `/api`).

Le rewrite SPA est deja gere par `frontend/vercel.json`.

## Etape 7 - Zoom OAuth
- Dans Zoom Marketplace:
   - Redirect URL for OAuth:
      `https://<ton-backend>.up.railway.app/api/zoom/callback`
   - Allow list / whitelist domaine backend si demande.

---

## 3) Ce qu'il faut changer/ajouter pendant le deployment

### A. Ajouts obligatoires
- Ajouter les 3 services Railway separes: backend, worker, beat.
- Ajouter PostgreSQL + Redis.
- Ajouter toutes les variables d'env dans chaque service compute (backend/worker/beat).

### B. Changements de configuration obligatoires
- Remplacer toutes les URLs localhost par URLs publiques:
   - FRONTEND_URL
   - VITE_API_URL
   - ZOOM_REDIRECT_URI
   - CORS_ORIGINS
- Mettre `VITE_USE_MOCK_ZOOM=false` en prod.
- Verifier que `JWT_SECRET_KEY` n'est pas une valeur de test.

### C. Optionnel mais recommande
- Fixer `OPENAI_BASE_URL` explicitement.
- Baisser/augmenter `--concurrency` worker selon CPU/memoire.
- Ajouter monitoring basique (logs + alertes Railway).

---

## 4) Verification post-deploiement (checklist)

Backend:
- `GET https://<backend>/health` -> `{"status":"healthy"}`
- `GET https://<backend>/docs` accessible
- signup/login OK
- upload meeting OK

Async:
- Worker logs: reception et execution de taches `meetings`
- Beat logs: emission job hebdo

Frontend:
- Login/register OK
- Pas d'erreur CORS en console navigateur
- Reset password genere un lien vers domaine frontend public

Zoom:
- Connexion Zoom aboutit sur `/dashboard?zoom=connected`
- Import Zoom cree bien un meeting

Email:
- Envoi de mail test (verification / reset) recu

DB:
- Tables creees + migration appliquee (`alembic upgrade head`)

---

## 5) Ordre d'execution recommande (resume rapide)

1. Preparer toutes les variables/secrets.
2. Deployer backend Railway.
3. Attacher PostgreSQL, lancer migrations.
4. Attacher Redis.
5. Deployer worker puis beat.
6. Deployer frontend Vercel.
7. Configurer Zoom OAuth avec URL finale backend.
8. Executer checklist de verification complete.

Si tu veux, je peux ensuite te faire une version ultra-oprationnelle en mode runbook (copier/coller), avec une checklist cocheable pour chaque clic Railway/Vercel.

---

## 6) Checklist Railway (clic par clic)

Utilise cette section comme runbook execution.

### A. Creer le projet Railway
- [ ] Ouvrir Railway > New Project.
- [ ] Choisir Deploy from GitHub Repo.
- [ ] Selectionner le repository `meeting-intelligence`.

### B. Service API backend
- [ ] New Service > GitHub Repo (meme repo).
- [ ] Root Directory = `/backend`.
- [ ] Verifier qu'un Dockerfile est detecte.
- [ ] Start command vide (ou `uvicorn app.main:app --host 0.0.0.0 --port $PORT`).
- [ ] Healthcheck path = `/health`.
- [ ] Ajouter les variables backend (voir section 8).
- [ ] Deploy.
- [ ] Ouvrir l'URL publique et tester `/health`.

### C. Service PostgreSQL
- [ ] New Service > Database > PostgreSQL.
- [ ] Lier `DATABASE_URL` au service backend.
- [ ] Ouvrir Shell backend.
- [ ] Executer `alembic upgrade head`.
- [ ] Verifier dans les logs que les migrations sont appliquees.

### D. Service Redis
- [ ] New Service > Database > Redis.
- [ ] Lier `REDIS_URL` au backend.
- [ ] Redeployer backend si necessaire.

### E. Service Worker Celery
- [ ] New Service > GitHub Repo (meme repo).
- [ ] Root Directory = `/backend`.
- [ ] Start command = `celery -A app.tasks.celery_app worker --loglevel=info -Q meetings --concurrency=2`.
- [ ] Copier les variables backend vers worker (section 8).
- [ ] Deploy.
- [ ] Verifier logs worker (tache recue puis executee).

### F. Service Beat Celery
- [ ] New Service > GitHub Repo (meme repo).
- [ ] Root Directory = `/backend`.
- [ ] Start command = `celery -A app.tasks.celery_app beat --loglevel=info --pidfile=/tmp/celerybeat.pid`.
- [ ] Copier les variables backend vers beat (section 8).
- [ ] Deploy.
- [ ] Verifier logs beat (scheduler actif).

### G. Verification immediate Railway
- [ ] Backend: `/health` retourne `{"status":"healthy"}`.
- [ ] Backend: `/docs` s'ouvre.
- [ ] Aucun crash de demarrage dans logs backend/worker/beat.

---

## 7) Checklist Vercel (clic par clic)

### A. Import frontend
- [ ] Ouvrir Vercel > Add New Project.
- [ ] Importer le meme repository GitHub.
- [ ] Root Directory = `/frontend`.
- [ ] Framework Preset = Vite.
- [ ] Build Command = `npm run build`.
- [ ] Output Directory = `dist`.

### B. Variables frontend
- [ ] Ajouter `VITE_API_URL=https://<backend>.up.railway.app/api`.
- [ ] Ajouter `VITE_USE_MOCK_ZOOM=false`.

### C. Deploy frontend
- [ ] Lancer Deploy.
- [ ] Ouvrir l'URL Vercel generee.
- [ ] Verifier navigation SPA (refresh sur route interne sans 404).

### D. Post-config backend apres URL frontend finale
- [ ] Dans Railway backend/worker/beat, definir `FRONTEND_URL=https://<frontend>.vercel.app`.
- [ ] Definir `CORS_ORIGINS=https://<frontend>.vercel.app` (ou CSV si multi-domaines).
- [ ] Redeployer backend/worker/beat.

### E. Config Zoom OAuth finale
- [ ] Zoom Marketplace > OAuth Redirect URL = `https://<backend>.up.railway.app/api/zoom/callback`.
- [ ] Verifier que la redirection finale arrive sur frontend `/dashboard?zoom=connected`.

---

## 8) Tableau variables d'environnement (pret a copier)

Remplace uniquement les valeurs entre `<...>`.

### A. Backend / Worker / Beat (Railway)

```env
# Core infra
DATABASE_URL=<railway-postgres-url>
REDIS_URL=<railway-redis-url>

# Auth
JWT_SECRET_KEY=<very-strong-random-secret-min-32-chars>
ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS / Frontend links
FRONTEND_URL=https://<frontend>.vercel.app
CORS_ORIGINS=https://<frontend>.vercel.app

# LLM / AI
OPENAI_API_KEY=<openrouter-or-openai-key>
OPENAI_BASE_URL=https://openrouter.ai/api/v1
ASSEMBLYAI_API_KEY=<assemblyai-key>

# SMTP
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=<brevo-smtp-user>
SMTP_PASSWORD=<brevo-smtp-password>
FROM_EMAIL=<validated-sender@yourdomain.com>
FROM_NAME=Syntra.ai

# Zoom OAuth
ZOOM_CLIENT_ID=<zoom-client-id>
ZOOM_CLIENT_SECRET=<zoom-client-secret>
ZOOM_REDIRECT_URI=https://<backend>.up.railway.app/api/zoom/callback
ZOOM_CONNECTED_REDIRECT_PATH=/dashboard

# Optional
CORS_ALLOW_ORIGIN_REGEX=
```

### B. Frontend (Vercel)

```env
VITE_API_URL=https://<backend>.up.railway.app/api
VITE_USE_MOCK_ZOOM=false
```

### C. Verifications express apres ajout des variables
- [ ] Aucune variable vide critique (`DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, `OPENAI_API_KEY`).
- [ ] Aucune URL en localhost en environnement production.
- [ ] `FRONTEND_URL`, `CORS_ORIGINS` et `VITE_API_URL` pointent vers les domaines publics finaux.
- [ ] `ZOOM_REDIRECT_URI` correspond exactement a la valeur configuree sur Zoom.
