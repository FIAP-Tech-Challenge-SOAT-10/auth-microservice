import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from src.infrastructure.database.models.refresh_token import RefreshToken  # noqa: F401

# Import your models for autogenerate support
from src.infrastructure.database.models.user import User  # noqa: F401
from src.infrastructure.database.session import Base

# Constants
ASYNCPG_DRIVER = "postgresql+asyncpg"
PSYCOPG2_DRIVER = "postgresql+psycopg2"

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    # Get URL from environment variable or config
    url = os.getenv("DATABASE_URL") or config.get_main_option("sqlalchemy.url")

    # Convert asyncpg to psycopg2 for migrations if needed
    if url and ASYNCPG_DRIVER in url:
        url = url.replace(ASYNCPG_DRIVER, PSYCOPG2_DRIVER)

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Load environment variables
    from dotenv import load_dotenv

    load_dotenv()

    # Get URL from environment variable
    database_url = os.getenv("DATABASE_URL")

    # Convert asyncpg to psycopg2 for migrations if needed
    if database_url and ASYNCPG_DRIVER in database_url:
        database_url = database_url.replace(ASYNCPG_DRIVER, PSYCOPG2_DRIVER)

    # Update config with environment URL if available
    if database_url:
        config.set_main_option("sqlalchemy.url", database_url)

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
