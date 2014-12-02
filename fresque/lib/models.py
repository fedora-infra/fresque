# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, print_function

import sqlalchemy as sa
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import relation
from sqlalchemy.orm import backref


BASE = declarative_base()


def create_tables(db_url, alembic_ini=None, debug=False):
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
    engine = sa.create_engine(db_url, echo=debug)
    BASE.metadata.create_all(engine)
    #engine.execute(collection_package_create_view(driver=engine.driver))
    if db_url.startswith('sqlite:'):
        ## Ignore the warning about con_record
        # pylint: disable=W0613
        def _fk_pragma_on_connect(dbapi_con, con_record):
            ''' Tries to enforce referential constraints on sqlite. '''
            dbapi_con.execute('pragma foreign_keys=ON')
        sa.event.listen(engine, 'connect', _fk_pragma_on_connect)

    if alembic_ini is not None:  # pragma: no cover
        # then, load the Alembic configuration and generate the
        # version table, "stamping" it with the most recent rev:

        ## Ignore the warning missing alembic
        # pylint: disable=F0401
        from alembic.config import Config
        from alembic import command
        alembic_cfg = Config(alembic_ini)
        command.stamp(alembic_cfg, "head")

    scopedsession = scoped_session(sessionmaker(bind=engine))
    return scopedsession


#class User(sa.Model):
#    id = sa.Column(sa.Integer, primary_key=True)
#    nickname = sa.Column(sa.String(64), index=True, unique=True)
#    email = sa.Column(sa.String(120), index=True, unique=True)
#


class Package(BASE):
    __tablename__ = 'packages'

    id = sa.Column(
        sa.Integer,
        primary_key=True)
    name = sa.Column(
        sa.String(128),
        nullable=False,
        index=True,
        unique=True)
    summary = sa.Column(
        sa.String(255),
        nullable=False)
    owner = sa.Column(
        sa.String(255),
        sa.ForeignKey(
            "users.name",
            onupdate="cascade")
        )
    # The state could use an Enum type, but we don't need the space-savings and
    # strict model checks that come with the added complexity in migrations.
    state = sa.Column(
        sa.String(64),
        nullable=False,
        default="new",
        index=True)

    def __repr__(self):
        return '<Package %r>' % (self.name)


class Distribution(BASE):
    __tablename__ = 'distributions'

    id = sa.Column(
        sa.String(32),
        primary_key=True)
    name = sa.Column(
        sa.String(64),
        unique=True)

    def __repr__(self):
        return '<Distribution %r>' % (self.id)


class TargetDistribution(BASE):
    __tablename__ = 'target_distributions'

    package_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('packages.id'),
        primary_key=True),
    distribution_id = sa.Column(
        sa.String(32),
        sa.ForeignKey('distributions.id'),
        primary_key=True)


class User(BASE):
    __tablename__ = 'users'
    # From FAS
    name = sa.Column(
        sa.String(255),
        primary_key=True)
    fullname = sa.Column(
        sa.String(255))
    email = sa.Column(
        sa.String(255))

    def __repr__(self):
        return '<User %r>' % (self.name)


class Review(BASE):
    __tablename__ = 'reviews'

    id = sa.Column(
        sa.Integer,
        primary_key=True)
    package_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            "packages.id",
            ondelete="cascade",
            onupdate="cascade")
        )
    commit_id  = sa.Column(
        sa.String(128),
        index=True,
        nullable=False)
    date_start = sa.Column(
        sa.DateTime,
        index=True,
        nullable=False,
        default=sa.func.now())
    date_end = sa.Column(
        sa.DateTime,
        index=True)
    srpm_filename = sa.Column(
        sa.String(255))
    spec_filename = sa.Column(
        sa.String(255))
    active = sa.Column(
        sa.Boolean,
        nullable=False,
        default=True)

    def __repr__(self):
        return '<Review %r of package %r>' % (self.id, self.package_id)


class Reviewer(BASE):
    __tablename__ = 'reviewers'

    review_id = sa.Column(
        sa.Integer,
        sa.ForeignKey('packages.id'),
        primary_key=True)
    reviewer_name = sa.Column(
        sa.String(255),
        sa.ForeignKey('users.name'),
        primary_key=True)


class Comment(BASE):
    __tablename__ = 'comments'

    id = sa.Column(
        sa.Integer,
        primary_key=True)
    review_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            "reviews.id",
            ondelete="cascade",
            onupdate="cascade")
        )
    author = sa.Column(
        sa.String(255),
        sa.ForeignKey(
            "users.name",
            onupdate="cascade")
        )
    date = sa.Column(
        sa.DateTime,
        nullable=False,
        default=sa.func.now())
    line_number = sa.Column(
        sa.Integer)
    relevant = sa.Column(
        sa.Boolean,
        nullable=False,
        default=True) # Is the comment still relevant

    def __repr__(self):
        return '<Comment %r on %r>' % (self.id, review_id)
