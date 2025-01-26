# db/env.py
import os
import sys
from logging.config import fileConfig

# Para poder importar auth_service/config.py
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from alembic import context
from sqlalchemy import engine_from_config, pool

from upload_service.config import config as app_config

# Carrega config do Alembic e logging
config_alembic = context.config
fileConfig(config_alembic.config_file_name)

# Aqui definimos a URL a partir de app_config
config_alembic.set_main_option("sqlalchemy.url", app_config.database_url)

# Metadados para 'autogenerate' se necessário (none se não usar)
target_metadata = None


def run_migrations_offline():
    """Executa migrações em modo offline."""
    url = config_alembic.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Executa migrações em modo online."""
    connectable = engine_from_config(
        config_alembic.get_section(config_alembic.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


def run_migrations():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()


run_migrations()
