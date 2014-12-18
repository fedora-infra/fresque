# -*- coding: utf-8 -*-

'''
Views for the fresque flask application
'''

from __future__ import absolute_import, unicode_literals, print_function

import flask
from flask.ext.fas import fas_login_required
from six import string_types

from fresque import APP, FAS
from fresque.utils import is_safe_url, is_authenticated
from fresque.lib import views


@APP.route("/")
def index():
    return flask.render_template("index.html")

@APP.route("/search")
def search():
    raise NotImplementedError

@APP.route("/packages")
def packages():
    result = views.packages(flask.g.db)
    return flask.render_template('packages.html', **result.context)

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
    result = views.newpackage(
        flask.g.db, flask.request.method, flask.request.form,
        flask.g.fas_user.username)
    for msg, style in result.flash:
        flask.flash(msg, style)
    if result.redirect:
        return flask.redirect(flask.url_for(
            result.redirect[0], **result.redirect[1]))
    return flask.render_template('new.html', **result.context)


@APP.route("/my/packages")
@fas_login_required
def user_packages():
    result = views.user_packages(flask.g.db, flask.g.fas_user.username)
    return flask.render_template("user/packages.html", **result.context)

@APP.route("/my/reviews")
@fas_login_required
def user_reviews():
    result = views.user_reviews(flask.g.db, flask.g.fas_user.username)
    return flask.render_template("user/reviews.html", **result.context)


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
