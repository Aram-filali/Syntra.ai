# Syntra.ai — Meeting Intelligence Platform

> An AI-powered platform that transcribes meetings and automatically extracts summaries, action items, decisions, and open questions.

![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18-blue?logo=react)
![Python](https://img.shields.io/badge/Python-3.11-yellow?logo=python)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

---

## 🚀 Features

- **AI-Powered Analysis** — Automatically extracts action items, key decisions, and open questions from meeting transcriptions using LLM agents (via OpenRouter / OpenAI).
- **Transcription** — Converts meeting audio/video files (MP3, MP4, M4A) to text with speaker diarization using AssemblyAI.
- **Meeting Reports** — Generates structured Markdown reports with executive summary, timeline, and next steps.
- **Email Sharing** — Send meeting reports to participants directly via email (Brevo SMTP).
- **Zoom Integration** — OAuth connection to import recordings directly from Zoom Cloud.
- **Authentication** — JWT-based auth with email verification flow.

---

## 🧱 Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI (Python 3.11), SQLAlchemy, Alembic |
| **Frontend** | React 18, React Router, TailwindCSS |
| **AI / LLM** | LangChain + OpenRouter (OpenAI-compatible) |
| **Transcription** | AssemblyAI (speaker diarization) |
| **Database** | PostgreSQL |
| **Queue** | Celery + Redis |
| **Email** | Brevo (SMTP) |
| **Infrastructure** | Docker + Docker Compose |

---

## 📁 Project Structure

```
meeting-intelligence/
├── backend/
│   ├── app/
│   │   ├── agents/          # LLM agents (summary, actions, decisions, questions)
│   │   ├── api/             # FastAPI route handlers (auth, meetings, zoom, webhooks)
│   │   ├── models/          # SQLAlchemy database models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── services/        # Business logic (auth, email, transcription, zoom)
│   │   ├── tasks/           # Celery async tasks
│   │   └── main.py          # FastAPI app entrypoint
│   ├── alembic/             # Database migrations
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios API client
│   │   ├── components/      # Reusable UI components
│   │   ├── context/         # React context (Auth)
│   │   └── pages/           # Application pages
│   └── Dockerfile
├── docker-compose.yml
└── .env.example             # Environment variable template
```

---

## ⚙️ Installation & Setup

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- A Brevo account for email (free tier works).
- An AssemblyAI API key (free tier available).
- An OpenRouter API key (for LLM access).

### 1. Clone the repository

```bash
git clone https://github.com/your-username/meeting-intelligence.git
cd meeting-intelligence
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Open `.env` and fill in your keys:

```env
# Required
ASSEMBLYAI_API_KEY=your_assemblyai_key
OPENAI_API_KEY=your_openrouter_key
OPENAI_BASE_URL=https://openrouter.ai/api/v1

# Email (Brevo SMTP)
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=your_brevo_login@smtp-brevo.com
SMTP_PASSWORD=your_brevo_smtp_key
FROM_EMAIL=your_validated_sender@email.com

# JWT (change this to a strong secret)
JWT_SECRET_KEY=your-super-secret-key-minimum-32-chars
```

### 3. Start the application

```bash
docker-compose up --build
```

This starts:
- **Backend API** on `http://localhost:8000`
- **Frontend** on `http://localhost:3000`
- **PostgreSQL** database
- **Redis** broker
- **Celery** worker and beat scheduler

---

## 🖥️ Usage

1. **Sign up** at `http://localhost:3000/signup`
2. **Verify your email** by clicking the link sent to your inbox.
3. **Sign in** and navigate to your Dashboard.
4. **Create a meeting** by uploading an audio/video file (MP3, MP4, M4A).
5. Wait for the AI to process — it will:
   - Transcribe the audio with speaker labels.
   - Extract action items, decisions, and open questions.
   - Generate a full Markdown meeting report.
6. **Share** the report with participants via email from the meeting detail page.

**API Documentation** is available at `http://localhost:8000/docs` (Swagger UI).

---

## 🏗️ AI Architecture

The meeting analysis pipeline uses **4 specialized LLM agents** running in parallel:

```
                  ┌──────────────────────┐
                  │  Meeting Transcription│
                  └──────────┬───────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       Action Agent   Decision Agent  Question Agent
              └──────────────┬──────────────┘
                             │
                             ▼
                       Summary Agent
                    (uses all 3 results)
                             │
                             ▼
                    Full Meeting Report
```

The orchestrator runs the 3 extraction agents in **parallel** with `asyncio.gather()`, then feeds all results into the summary agent for a coherent final report.

---

## 🔑 Environment Variables Reference

| Variable | Description |
|---|---|
| `ASSEMBLYAI_API_KEY` | AssemblyAI key for transcription |
| `OPENAI_API_KEY` | LLM key (OpenRouter or OpenAI) |
| `OPENAI_BASE_URL` | LLM base URL (default: OpenRouter) |
| `SMTP_HOST` / `SMTP_PORT` | SMTP server for emails |
| `SMTP_USER` / `SMTP_PASSWORD` | SMTP credentials |
| `FROM_EMAIL` | Validated sender address |
| `JWT_SECRET_KEY` | Secret for signing JWT tokens |
| `FRONTEND_URL` | Frontend URL for email links (default: `http://localhost:3000`) |

---

## 🛡️ Security Notes

- Never commit your `.env` file — it is included in `.gitignore`.
- Change `JWT_SECRET_KEY` to a strong, random value before deploying.
- Restrict `ALLOWED_ORIGINS` to your domain in production.


---

*Built using FastAPI, React, LangChain, and AssemblyAI.*
