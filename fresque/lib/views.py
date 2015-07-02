# -*- coding: utf-8 -*-

'''
Views independant from the web framework.

Exceptions:

- We use the Form subclass coming from Flask-WTF, which transparently uses
  Flask's request and session proxies. However, we don't use the special API
  methods here (like validate_on_submit() or hidden_tag()), so it should be
  easy to switch to a vanilla WTForm, we'd only have to re-implement the
  session-based CSRF token generation and validation.
'''

from __future__ import absolute_import, unicode_literals, print_function

import os
import pygit2
import json
import fresque
from time import time

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound
from pygit2 import GitError
from fresque import forms
from fresque.lib.models import Package, Distribution, Review, Reviewer, Comment
from fresque.lib.utils import Result


def index(db):
    recent_pkgs = db.query(Package).filter(Package.active
        ).order_by(Package.submitted.desc()).limit(10).all()
    updated_revs = db.query(Review).join(Comment
        ).order_by(Comment.date.desc()).limit(10).all()
    pkgs_without_rev = db.query(Package).filter(
        Package.active, ~Package.reviews.any()
        ).order_by(Package.submitted.desc()).limit(10).all()
    return Result({"recent_pkgs": recent_pkgs,
                   "updated_revs": updated_revs,
                   "pkgs_without_rev": pkgs_without_rev,
                   })


def packages(db):
    packages = db.query(Package).filter(Package.active).all()
    packages.sort(key=lambda p: p.last_review_activity)
    return Result({"packages": packages})


def package(db, name):
    try:
        package = db.query(Package).filter_by(name=name).one()
    except NoResultFound:
        return Result({"message": "Unknown package: {}".format(name)},
                      code=404)
    else:
        return Result({"package": package})


def newpackage(db, method, data, username, gitfolder):
    distributions = db.query(
        Distribution).order_by(Distribution.id).all()
    form = forms.NewPackage(data)
    form.distributions.choices = [(d.id, d.name) for d in distributions]
    form.distributions.default = [d.id for d in distributions]
    result = Result({"form": form})
    if method == "POST" and form.validate():
        pkg = Package(
            name=form.name.data,
            summary=form.summary.data,
            description=form.description.data,
            owner=username,
            )
        db.add(pkg)
        pkg.distributions = db.query(Distribution).filter(
            Distribution.id.in_(form.distributions.data)).all()
        try:
            db.commit()
        except SQLAlchemyError:
            result.flash.append(("An error occurred while adding your "
                "package, please contact an administrator.", "danger"))
        else:
            result.flash.append(("Package successfully created!", "success"))
            result.redirect = ('package', {"name": pkg.name})

            # Add git repo creation message
            try:
                status_message = create_git_repo(pkg.name, gitfolder)
                result.flash.append((
                    status_message, "success"))
            except fresque.exceptions.FresqueException:
                result.flash.append(("An error occurred while creating git \
                    repository, please contact an administrator.", "danger"))

    return result


def user_packages(db, username):
    all_packages = db.query(Package).filter_by(owner=username).all()
    all_packages.sort(key=lambda p: p.last_review_activity)
    packages = []
    old_packages = []
    for package in all_packages:
        if package.active:
            packages.append(package)
        else:
            old_packages.append(package)
    return Result({"packages": packages, "old_packages": old_packages})


def user_reviews(db, username):
    reviews = db.query(Review).join(Reviewer).filter(
            Reviewer.reviewer_name == username
        ).order_by(Review.date_start).all()
    return Result({"reviews": reviews})


def create_git_repo(name, gitfolder):
    # Create a git project based on the package information.
    # get the path of the git repo
    gitrepo = os.path.join(gitfolder, '%s.git' % name)

    if os.path.exists(gitrepo):
        raise fresque.exceptions.RepoExistsException(
            'The project named "%s" already have '
            'a git repository' % name
        )
    # create a bare git repository
    pygit2.init_repository(gitrepo, bare=True)
    return 'Successfully created Project {0} git respository'.format(name)
