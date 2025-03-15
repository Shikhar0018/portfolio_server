# alembic/env.py
from logging.config import fileConfig
import sys
import os

# Add the app directory to Python path (critical for Docker)
sys.path.insert(0, "/app")  # This matches the Docker WORKDIR

from sqlalchemy import engine_from_config, pool
from alembic import context

# Import your Base and settings from the core module
from app.core.database import Base
from app.core.config import settings

config = context.config
fileConfig(config.config_file_name)

# Set target metadata from your Base class
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        url=settings.DATABASE_URL  # Use settings from your config
    )

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