from __future__ import with_statement, unicode_literals, absolute_import, print_function
from alembic import context
from sqlalchemy import create_engine, pool


if context.config.config_file_name is not None:
    # Invoked by the "alembic" command, we can setup logging
    from logging.config import fileConfig
    fileConfig(context.config.config_file_name)

from fresque import APP
db_url = APP.config.get('SQLALCHEMY_DATABASE_URI')
from fresque.lib.models import Base
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(url=db_url, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = create_engine(db_url, poolclass=pool.NullPool)

    connection = engine.connect()
    context.configure(
        connection=connection,
        target_metadata=target_metadata
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
