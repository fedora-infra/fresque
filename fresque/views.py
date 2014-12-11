# -*- coding: utf-8 -*-

'''
Views for the fresque flask application
'''

from __future__ import absolute_import, unicode_literals, print_function

from flask import request, g, render_template

from fresque import APP


@APP.route("/")
def index():
    return render_template("index.html")

@APP.route("/search")
def search():
    raise NotImplementedError

@APP.route("/new")
def newpackage():
    return "newpackage"

@APP.route("/my/packages")
def user_packages():
    return "user_packages"

@APP.route("/my/reviews")
def user_reviews():
    return "user_reviews"

@APP.route("/review/<int:rid>")
def review(rid):
    return "review %d" % rid

@APP.route("/login")
def login():
    return "login"

@APP.route("/logout")
def logout():
    return "logout"
