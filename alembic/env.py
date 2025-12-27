import os
from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig

# Alembic Config object
config = context.config

# Interpret the config file for logging
fileConfig(config.config_file_name)

# Read async URL from env
async_url = os.getenv("POSTGRES_URL")

# Replace asyncpg with psycopg2 for migrations
sync_url = async_url.replace("asyncpg", "psycopg2")

# Override sqlalchemy.url in Alembic config
config.set_main_option("sqlalchemy.url", sync_url)

# Import your models Base
from src.shared.app.db import Base
target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
