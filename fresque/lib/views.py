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

from sqlalchemy.exc import SQLAlchemyError

from fresque import forms
from fresque.lib.models import Package, Distribution
from fresque.lib.utils import Result


def newpackage(db, method, data, username):
    distributions = db.query(
        Distribution).order_by(Distribution.id).all()
    form = forms.NewPackage(data)
    form.distributions.choices = [ (d.id, d.name) for d in distributions ]
    form.distributions.default = [ d.id for d in distributions ]
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
    return result


def user_packages(db, username):
    all_packages = db.query(Package).filter_by(owner=username).all()
    # TODO: filter-out included packages (state == done)
    all_packages.sort(key=lambda p: p.last_review_activity)
    packages = []
    old_packages = []
    for package in all_packages:
        if package.state in ["done", "rejected"]:
            # I'm pretty sure we'll end up needing a workflow engine, if we
            # want to make the app easily configurable. Then we can extract the
            # exit states here instead of hardcoding.
            # TODO: use a workflow engine.
            old_packages.append(package)
        else:
            packages.append(package)
    return Result({"packages": packages, "old_packages": old_packages})
