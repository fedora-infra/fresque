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
from inspect import getmembers, isfunction

APP = flask.Flask(__name__)
APP.jinja_env.trim_blocks = True
APP.jinja_env.lstrip_blocks = True

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

from fresque.lib.database import create_session, DatabaseNeedsUpgrade

@APP.before_request
def before_request():
    try:
        flask.g.db = create_session(APP.config["SQLALCHEMY_DATABASE_URI"])
    except DatabaseNeedsUpgrade:
        return flask.render_template("error.html", code=500,
            message="The database schema must be upgraded "
                    "by the administrator",
            ), 500

@APP.teardown_appcontext
def shutdown_session(exception=None): # pylint: disable=unused-argument
    if hasattr(flask.g, "db"):
        flask.g.db.remove()


from fresque import views, gitview, filters
