import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy import create_engine
from alembic import context
from dotenv import load_dotenv

# Charge le .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

# URL PostgreSQL depuis le .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Alembic Config
config = context.config
fileConfig(config.config_file_name)

# Importer tes modèles et Base
from app.models.base import Base 
from app.models.meeting import User
from app.models.meeting import Meeting
from app.models.meeting import Transcription
from app.models.meeting import ActionItem
from app.models.meeting import Summary

# Metadata pour Alembic
target_metadata = Base.metadata 

# Migration offline
def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Migration online
def run_migrations_online() -> None:
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
