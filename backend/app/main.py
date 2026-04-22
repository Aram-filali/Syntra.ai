# backend/app/main.py
#
# FastAPI application entrypoint.
# Registers all routers and configures CORS middleware.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import meetings, auth, zoom, webhooks
from .models.base import engine, Base

# All models must be imported before create_all() so SQLAlchemy can discover them
from .models import meeting, user

# Create tables on startup if they don't exist yet.
# In production, prefer running Alembic migrations explicitly instead.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Syntra.ai API",
    description="API pour analyser des réunions avec IA et authentification JWT",
    version="1.0.0"
)

# Allow requests from the frontend dev server and any custom frontend port
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:5173",
    ],
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