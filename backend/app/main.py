# backend/app/main.py
#
# FastAPI application entrypoint.
# Registers all routers and configures CORS middleware.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from .api import meetings, auth, zoom, webhooks
from .models.base import engine, Base

# All models must be imported before create_all() so SQLAlchemy can discover them
from .models import meeting, user

# Do not create tables by default at startup in production.
# This can block boot/healthchecks if DB is temporarily unavailable.
if os.getenv("AUTO_CREATE_TABLES", "false").lower() == "true":
    Base.metadata.create_all(bind=engine)


def _build_cors_origins() -> list[str]:
    default_origins = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
        "https://syntra-ai-three.vercel.app",
    ]
    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    extra_origins = [
        origin.strip() for origin in os.getenv("CORS_ORIGINS", "").split(",") if origin.strip()
    ]

    origins = default_origins + extra_origins
    if frontend_url:
        origins.append(frontend_url)

    unique_origins = []
    seen = set()
    for origin in origins:
        normalized = origin.rstrip("/")
        if normalized and normalized not in seen:
            seen.add(normalized)
            unique_origins.append(normalized)

    return unique_origins

app = FastAPI(
    title="Syntra.ai API",
    description="API pour analyser des réunions avec IA et authentification JWT",
    version="1.0.0"
)

# Allow requests from the frontend dev server and any custom frontend port
app.add_middleware(
    CORSMiddleware,
    allow_origins=_build_cors_origins(),
    allow_origin_regex=os.getenv("CORS_ALLOW_ORIGIN_REGEX") or r"^https://[a-zA-Z0-9-]+\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all route groups with their URL prefixes
app.include_router(auth.router, prefix="/api/auth", tags=["🔐 Authentication"])
app.include_router(meetings.router, prefix="/api/meetings", tags=["📅 Meetings"])
app.include_router(zoom.router, prefix="/api/zoom", tags=["📹 Zoom Integration"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["⚓ Webhooks"])


@app.get("/")
def root():
    return {
        "status": "Syntra.ai API running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    """Health check endpoint — used by Docker and load balancers."""
    return {"status": "healthy"}