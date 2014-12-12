# -*- coding: utf-8 -*-

'''
Views for the fresque flask application
'''

from __future__ import absolute_import, unicode_literals, print_function

import flask
from flask.ext.fas import fas_login_required

from fresque import APP, FAS, forms
from fresque.lib.models import Distribution


@APP.route("/")
def index():
    return flask.render_template("index.html")

@APP.route("/search")
def search():
    raise NotImplementedError

@APP.route("/packages")
def packages():
    return "all packages"

@APP.route("/packages/<name>")
def package(name):
    return "package %s" % name

@APP.route("/pacakges/<pname>/reviews/")
def reviews(pname):
    return "review for package %d" % pid

@APP.route("/pacakges/<pname>/reviews/<int:rid>")
def review(pname, rid):
    return "review %d" % rid


@APP.route("/new")
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
        g.db.add(pkg)
        pkg.distributions = form.distributions.data
        flask.flash("Package successfully created!", "success")
        return flask.redirect(flask.url_for('package', pid=pkg.name))
    return flask.render_template('new.html', form=form)


@APP.route("/my/packages")
@fas_login_required
def user_packages():
    return "user_packages"

@APP.route("/my/reviews")
@fas_login_required
def user_reviews():
    return "user_reviews"


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
