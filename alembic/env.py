# alembic/env.py

from logging.config import fileConfig
import sys
import os

# Alembic imports
from alembic import context
from sqlalchemy import engine_from_config, pool

# Make sure Python can find your 'app' package.
# If your Dockerfile WORKDIR is /app, this is often enough:
sys.path.insert(0, "/app")

# Project imports
from app.core.database import Base  # Base from your core module
from app.core.config import settings

# Import ALL model modules so Alembic can see them
# (Even if you don't explicitly use them here, the import
#  ensures their tables are attached to Base.metadata)
from app.models import data, design, experiences, projects, profile

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# Set the metadata for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline():
    """
    Run migrations in 'offline' mode.
    Alembic configures the context with just a URL
    and not an Engine, though an Engine is acceptable.
    """
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """
    Run migrations in 'online' mode.
    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=settings.DATABASE_URL  # We override the URL from alembic.ini
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

# Determine offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
