# -*- coding: utf-8 -*-

'''
Database management library for the fresque application.
'''

from __future__ import absolute_import, unicode_literals, print_function

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker, scoped_session

import alembic.command
import alembic.config
from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext

from fresque.lib import models


class DatabaseNeedsUpgrade(Exception):
    """The database's schema is not up-to-date"""


def get_alembic_config(db_url):
    alembic_cfg = alembic.config.Config()
    alembic_cfg.set_main_option("script_location", "fresque.lib:alembic")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    return alembic_cfg


def create_session(db_url, debug=False, pool_recycle=3600):
    """ Create the Session object to use to query the database.

    :arg db_url: URL used to connect to the database. The URL contains
    information with regards to the database engine, the host to connect
    to, the user and password and the database name.
      ie: <engine>://<user>:<password>@<host>/<dbname>
    :kwarg debug: a boolean specifying wether we should have the verbose
        output of sqlalchemy or not.
    :return a Session that can be used to query the database.

    """
    engine = sa.create_engine(
        db_url, echo=debug,
        pool_recycle=pool_recycle,
        convert_unicode=True)
    session = scoped_session(sessionmaker(
        autocommit=False, autoflush=False, bind=engine))
    # check that the database's schema is up-to-date
    script_dir = ScriptDirectory.from_config(get_alembic_config(db_url))
    head_rev = script_dir.get_current_head()
    context = MigrationContext.configure(session.connection())
    current_rev = context.get_current_revision()
    if current_rev != head_rev:
        raise DatabaseNeedsUpgrade
    # everything looks good here
    return session


def create_tables(config, debug=False):
    """ Create the tables in the database using the information from the
    url obtained.

    :arg db_url, URL used to connect to the database. The URL contains
        information with regards to the database engine, the host to
        connect to, the user and password and the database name.
          ie: <engine>://<user>:<password>@<host>/<dbname>
    :kwarg alembic_ini, path to the alembic ini file. This is necessary
        to be able to use alembic correctly, but not for the unit-tests.
    :kwarg debug, a boolean specifying wether we should have the verbose
        output of sqlalchemy or not.
    :return a session that can be used to query the database.

    """
    db_url = config['SQLALCHEMY_DATABASE_URI']
    engine = sa.create_engine(db_url, echo=debug)
    models.Base.metadata.create_all(engine)
    # engine.execute(collection_package_create_view(driver=engine.driver))
    if db_url.startswith('sqlite:'):
        # Ignore the warning about con_record
        # pylint: disable=W0613
        def _fk_pragma_on_connect(dbapi_con, con_record):
            ''' Tries to enforce referential constraints on sqlite. '''
            dbapi_con.execute('pragma foreign_keys=ON')
        sa.event.listen(engine, 'connect', _fk_pragma_on_connect)

    # Generate the Alembic version table and "stamp" it with the latest rev
    alembic.command.stamp(get_alembic_config(db_url), "head")

    # Add missing distributions
    session = create_session(db_url, debug=debug)
    for d_id, d_name in config["DISTRIBUTIONS"].items():
        distro = session.query(models.Distribution).get(d_id)
        if distro:
            continue
        session.add(models.Distribution(id=d_id, name=d_name))
    session.commit()
