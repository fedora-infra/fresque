# -*- coding: utf-8 -*-

'''
Views for the fresque flask application
'''

from __future__ import absolute_import, unicode_literals, print_function

import flask
from flask.ext.fas import fas_login_required
from six import string_types

from fresque import APP, FAS
from fresque import forms
from fresque.utils import is_safe_url, is_authenticated
from fresque.lib.models import Package, Distribution


@APP.route("/")
def index():
    return flask.render_template("index.html")

@APP.route("/search")
def search():
    raise NotImplementedError

@APP.route("/packages")
def packages():
    return flask.render_template("simple.html", content="all packages")

@APP.route("/packages/<name>")
def package(name):
    return flask.render_template("simple.html", content="package %s" % name)

@APP.route("/pacakges/<pname>/reviews/")
def reviews(pname):
    return flask.render_template("simple.html", content="review for package %s" % pname)

@APP.route("/pacakges/<pname>/reviews/<int:rid>")
def review(pname, rid):
    return flask.render_template("simple.html", content="review %d" % rid)


@APP.route("/new", methods=["GET", "POST"])
@fas_login_required
def newpackage():
    distributions = flask.g.db.query(
        Distribution).order_by(Distribution.id).all()
    form = forms.NewPackage()
    form.distributions.choices = [ (d.id, d.name) for d in distributions ]
    form.distributions.default = [ d.id for d in distributions ]
    if form.validate_on_submit():
        pkg = Package(
            name=form.name.data,
            summary=form.summary.data,
            description=form.description.data,
            owner=flask.g.fas_user.username,
            )
        flask.g.db.add(pkg)
        pkg.distributions = flask.g.db.query(Distribution).filter(
            Distribution.id.in_(form.distributions.data)).all()
        flask.g.db.commit()
        flask.flash("Package successfully created!", "success")
        return flask.redirect(flask.url_for('package', name=pkg.name))
    return flask.render_template('new.html', form=form)


@APP.route("/my/packages")
@fas_login_required
def user_packages():
    packages = flask.g.db.query(Package).filter_by(
        owner=flask.g.fas_user.username).all()
    # TODO: filter-out included packages (state == done)
    packages.sort(key=lambda p: p.last_review_activity)
    return flask.render_template("user/packages.html", packages=packages)

@APP.route("/my/reviews")
@fas_login_required
def user_reviews():
    return flask.render_template("simple.html", content="user_reviews")


# Login / logout

@APP.route('/login', methods=['GET', 'POST'])
def auth_login():
    next_url = flask.url_for('index')
    if 'next' in flask.request.values:
        url = flask.request.values['next']
        if is_safe_url(url) and url != flask.url_for('auth_login'):
            next_url = url

    if is_authenticated():
        return flask.redirect(next_url)

    required_groups = set(APP.config['REQUIRED_GROUPS'])
    if isinstance(APP.config['ADMIN_GROUPS'], string_types):
        required_groups.add(APP.config['ADMIN_GROUPS'])
    else:
        required_groups.update(APP.config['ADMIN_GROUPS'])
    return FAS.login(return_url=next_url, groups=required_groups)


@APP.route('/logout')
def logout():
    if flask.g.fas_user:
        flask.flash("Sucessfully disconnected, goodbye!", "success")
        FAS.logout()
    return flask.redirect(flask.url_for('index'))
