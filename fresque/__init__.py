# -*- coding: utf-8 -*-

'''
Top level of the fresque application.
'''

from __future__ import absolute_import, unicode_literals, print_function

import logging
import logging.handlers
import os
import sys

import flask
import flask_fas_openid


APP = flask.Flask(__name__)
APP.config.from_object('fresque.default_config')
if 'FRESQUE_CONFIG' in os.environ: # pragma: no cover
    APP.config.from_envvar('FRESQUE_CONFIG')


# Set up FAS extension
FAS = flask_fas_openid.FAS(APP)


# TODO: Add email handler (except on debug mode)

# Log to stderr as well
STDERR_LOG = logging.StreamHandler(sys.stderr)
STDERR_LOG.setLevel(logging.INFO)
APP.logger.addHandler(STDERR_LOG)

LOG = APP.logger

import fresque.proxy
APP.wsgi_app = fresque.proxy.ReverseProxied(APP.wsgi_app)


# Database

from fresque.lib.database import create_session

@APP.before_request
def before_request():
    flask.g.db = create_session(APP.config["SQLALCHEMY_DATABASE_URI"])

@APP.teardown_appcontext
def shutdown_session(exception=None): # pylint: disable=unused-argument
    if hasattr(flask.g, "db"):
        flask.g.db.remove()


from fresque import views
