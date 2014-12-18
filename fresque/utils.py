# -*- coding: utf-8 -*-

"""
Some Flask-specific utility functions.
"""

from __future__ import absolute_import, unicode_literals, print_function

import urlparse

import flask
from six import string_types

from fresque import APP


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


def is_fresque_admin(user):
    """ Is the user a fresque admin.
    """
    if not user:
        return False

    if not user.cla_done or len(user.groups) < 1:
        return False

    admins = APP.config['ADMIN_GROUP']
    if isinstance(admins, string_types):
        admins = [admins]
    admins = set(admins)

    return len(admins.intersection(set(user.groups))) > 0


def admin_required(function):
    """ Flask decorator to ensure that the user is logged in. """
    @wraps(function)
    def decorated_function(*args, **kwargs):
        ''' Wrapped function actually checking if the user is logged in.
        '''
        if not is_authenticated():
            return flask.redirect(flask.url_for(
                'auth_login', next=flask.request.url))
        elif not is_fresque_admin(flask.g.fas_user):
            flask.flash('You are not an admin', 'danger')
            return flask.redirect(flask.url_for('index'))
        return function(*args, **kwargs)
    return decorated_function


def handle_result(result, template):
    for msg, style in result.flash:
        flask.flash(msg, style)
    if result.redirect:
        return flask.redirect(flask.url_for(
            result.redirect[0], **result.redirect[1]))
    return flask.render_template(template, **result.context)
