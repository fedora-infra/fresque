from __future__ import absolute_import, unicode_literals, print_function

from flask import current_app
from sqlalchemy import func

from fresque.lib import states

db = current_app.extensions["sqlalchemy"].db

#class User(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    nickname = db.Column(db.String(64), index=True, unique=True)
#    email = db.Column(db.String(120), index=True, unique=True)
#


class Package(db.Model):
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(128), nullable=False, index=True, unique=True)
    summary = db.Column(db.String(255), nullable=False)
    owner   = db.Column(db.String(255), db.ForeignKey("user.name", onupdate="cascade"))
    # The state could use an Enum type, but we don't need the space-savings and
    # strict model checks that come with the added complexity in migrations.
    state   = db.Column(db.String(64), nullable=False, default="new", index=True)

    def __repr__(self):
        return '<Package %r>' % (self.name)


class Distribution(db.Model):
    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<Distribution %r>' % (self.id)


target_distributions = db.Table('target_distributions',
    db.Column('package_id', db.Integer,
        db.ForeignKey('package.id'), primary_key=True),
    db.Column('distribution_id', db.String(32),
        db.ForeignKey('distribution.id'), primary_key=True)
)


class User(db.Model):
    # From FAS
    name     = db.Column(db.String(255), primary_key=True)
    fullname = db.Column(db.String(255))
    email    = db.Column(db.String(255))

    def __repr__(self):
        return '<User %r>' % (self.name)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey("package.id", ondelete="cascade", onupdate="cascade"))
    commit_id  = db.Column(db.String(128), index=True, nullable=False)
    date_start = db.Column(db.DateTime, index=True, nullable=False, default=db.func.now())
    date_end   = db.Column(db.DateTime, index=True)
    srpm_filename = db.Column(db.String(255))
    spec_filename = db.Column(db.String(255))
    active     = db.Column(db.Boolean, nullable=False, default=True)

    def __repr__(self):
        return '<Review %r of package %r>' % (self.id, self.package_id)


reviewers = db.Table("reviewers",
    db.Column('review_id', db.Integer, db.ForeignKey('package.id')),
    db.Column('reviewer_name', db.String(255), db.ForeignKey('user.name'))
)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_id    = db.Column(db.Integer, db.ForeignKey("review.id", ondelete="cascade", onupdate="cascade"))
    author       = db.Column(db.String(255), db.ForeignKey("user.name", onupdate="cascade"))
    date         = db.Column(db.DateTime, nullable=False, default=db.func.now())
    line_number  = db.Column(db.Integer)
    relevant     = db.Column(db.Boolean, nullable=False, default=True) # Is the comment still relevant

    def __repr__(self):
        return '<Comment %r on %r>' % (self.id, review_id)
