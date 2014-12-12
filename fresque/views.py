# -*- coding: utf-8 -*-

'''
Views for the fresque flask application
'''

from __future__ import absolute_import, unicode_literals, print_function

import flask
from flask.ext.fas import fas_login_required

from fresque import APP, FAS


@APP.route("/")
def index():
    return flask.render_template("index.html")

@APP.route("/search")
def search():
    raise NotImplementedError

@APP.route("/new")
@fas_login_required
def newpackage():
    return "newpackage"

@APP.route("/my/packages")
@fas_login_required
def user_packages():
    return "user_packages"

@APP.route("/my/reviews")
@fas_login_required
def user_reviews():
    return "user_reviews"

@APP.route("/review/<int:rid>")
def review(rid):
    return "review %d" % rid

# Login / logout

@APP.route('/login', methods=['GET', 'POST'])
def login():
    # Your application should probably do some checking to make sure the URL
    # given in the next request argument is sane. (For example, having next set
    # to the login page will cause a redirect loop.) Some more information:
    # http://flask.pocoo.org/snippets/62/
    next_url = flask.request.args.get("next", flask.url_for("index"))
    # If user is already logged in, return them to where they were last
    if flask.g.fas_user:
        flask.flash("Welcome {}!".format(flask.g.fas_user.username), "success")
        return flask.redirect(next_url)
    return FAS.login(return_url=next_url)

@APP.route('/logout')
def logout():
    if flask.g.fas_user:
        flask.flash("Sucessfully disconnected, goodbye!", "success")
        FAS.logout()
    return flask.redirect(flask.url_for('index'))
