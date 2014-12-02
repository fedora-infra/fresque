# -*- coding: utf-8 -*-

'''
Top level of the fresque application.
'''

from __future__ import absolute_import, unicode_literals, print_function

import logging
import logging.handlers
import os
import sys
import urlparse

import flask
from flask.ext.fas_openid import FAS

APP = flask.Flask(__name__)
APP.config.from_object('fresque.default_config')
if 'FRESQUE_CONFIG' in os.environ: # pragma: no cover
    APP.config.from_envvar('FRESQUE_CONFIG')


# Set up FAS extension
FAS = FAS(APP)


# TODO: Add email handler (except on debug mode)

# Log to stderr as well
STDERR_LOG = logging.StreamHandler(sys.stderr)
STDERR_LOG.setLevel(logging.INFO)
APP.logger.addHandler(STDERR_LOG)

LOG = APP.logger

import fresque.lib
import fresque.proxy


APP.wsgi_app = fresque.proxy.ReverseProxied(APP.wsgi_app)
SESSION = fresque.lib.create_session(APP.config['SQLALCHEMY_DATABASE_URI'])


def is_authenticated():
    """ Returns wether a user is authenticated or not.
    """
    return hasattr(flask.g, 'fas_user') and flask.g.fas_user is not None


def is_safe_url(target):
    """ Checks that the target url is safe and sending to the current
    website not some other malicious one.
    """
    ref_url = urlparse.urlparse(flask.request.host_url)
    test_url = urlparse.urlparse(
        urlparse.urljoin(flask.request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc

from fresque import views

