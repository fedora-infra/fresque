# -*- coding: utf-8 -*-
# pylint: disable=bad-whitespace,no-init,too-few-public-methods,bad-continuation,invalid-name

from __future__ import absolute_import, unicode_literals, print_function

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Package(Base):
    __tablename__ = 'packages'

    id       = sa.Column(sa.Integer, primary_key=True)
    name     = sa.Column(sa.String(128),
                         nullable=False, index=True, unique=True)
    summary  = sa.Column(sa.String(255), nullable=False)
    owner    = sa.Column(sa.String(255))
    # The state could use an Enum type, but we don't need the space-savings and
    # strict model checks that come with the added complexity in migrations.
    state    = sa.Column(sa.String(64),
                         nullable=False, default="new", index=True)
    requires = sa.Column(sa.Integer,
                         sa.ForeignKey("packages.id", onupdate="cascade"))

    def __repr__(self):
        return '<Package %r>' % (self.name)


class Distribution(Base):
    __tablename__ = 'distributions'

    id   = sa.Column(sa.String(32), primary_key=True)
    name = sa.Column(sa.String(64), unique=True)

    def __repr__(self):
        return '<Distribution %r>' % (self.id)


class TargetDistribution(Base):
    __tablename__ = 'target_distributions'

    package_id      = sa.Column(
        sa.Integer, sa.ForeignKey('packages.id'), primary_key=True)
    distribution_id = sa.Column(
        sa.String(32), sa.ForeignKey('distributions.id'), primary_key=True)


class Review(Base):
    __tablename__ = 'reviews'

    id         = sa.Column(sa.Integer, primary_key=True)
    package_id = sa.Column(sa.Integer,
                           sa.ForeignKey("packages.id",
                           ondelete="cascade", onupdate="cascade"))
    commit_id  = sa.Column(sa.String(128), index=True, nullable=False)
    date_start = sa.Column(sa.DateTime,
                           index=True, nullable=False, default=sa.func.now())
    date_end   = sa.Column(sa.DateTime, index=True)
    srpm_filename = sa.Column(sa.String(255))
    spec_filename = sa.Column(sa.String(255))
    active     = sa.Column(sa.Boolean, nullable=False, default=True)

    def __repr__(self):
        return '<Review %r of package %r>' % (self.id, self.package_id)


class Reviewer(Base):
    __tablename__ = 'reviewers'

    review_id     = sa.Column(sa.Integer,
                              sa.ForeignKey('reviews.id'), primary_key=True)
    reviewer_name = sa.Column(sa.String(255), primary_key=True)


class Watcher(Base):
    __tablename__ = 'watchers'

    package_id   = sa.Column(sa.Integer,
                             sa.ForeignKey('packages.id'), primary_key=True)
    watcher_name = sa.Column(sa.String(255), primary_key=True)


class Comment(Base):
    __tablename__ = 'comments'

    id          = sa.Column(sa.Integer, primary_key=True)
    review_id   = sa.Column(sa.Integer,
                            sa.ForeignKey("reviews.id",
                                ondelete="cascade", onupdate="cascade"))
    author      = sa.Column(sa.String(255))
    date        = sa.Column(sa.DateTime, nullable=False, default=sa.func.now())
    line_number = sa.Column(sa.Integer)
    # relevant: has the comment been replied to?
    relevant    = sa.Column(sa.Boolean, nullable=False, default=True)

    def __repr__(self):
        return '<Comment %r on %r>' % (self.id, self.review_id)
