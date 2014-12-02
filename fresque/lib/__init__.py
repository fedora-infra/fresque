# -*- coding: utf-8 -*-

'''
Internal library for the fresque application.

This module and all its files contains all the operations independant of the
framework and should be completely covered in unit-tests.
'''

from __future__ import absolute_import, unicode_literals, print_function

import sqlalchemy as sa
from fresque.lib import models as model

from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import SQLAlchemyError


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
        db_url,
        echo=debug,
        pool_recycle=pool_recycle)
    scopedsession = scoped_session(sessionmaker(bind=engine))
    return scopedsession

