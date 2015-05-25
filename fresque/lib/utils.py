# -*- coding: utf-8 -*-

"""
Framework-independant wrappers.

Those functions are proxies for the framework's functions.
"""

from __future__ import absolute_import, unicode_literals, print_function
import chardet


def _is_flask():
    try:
        from flask import current_app
        current_app.name
    except (ImportError, RuntimeError):
        return False
    else:
        return True

def _is_pyramid():
    return False # TODO: implement this


FRAMEWORK = None
def framework_name():
    if FRAMEWORK is None:
        if _is_flask():
            FRAMEWORK = "flask"
        elif _is_pyramid():
            FRAMEWORK = "pyramid"
        raise RuntimeError("Unknown Framework")
    return FRAMEWORK


class Result:
    def __init__(self, context=None, code=200):
        self.context = context or {}
        self.flash = []
        # `redirect` must be None or a tuple: (view_name, view_kwargs)
        self.redirect = None
        self.code = code


def redirect_to_url(url):
    if framework_name() == "flask":
        import flask
        return flask.redirect(url)
    if framework_name() == "pyramid":
        from pyramid.httpexceptions import HTTPFound
        return HTTPFound(location=url)


def decode(data, encoding=None):
    if isinstance(data, unicode):
        return data
    if encoding:
        return data.decode(encoding)
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        encoding = chardet.detect(data)['encoding']
        if not encoding:
            return "(Binary data)"
        return data.decode(encoding)
