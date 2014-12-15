# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os

from datetime import timedelta

basedir = os.path.abspath(
    os.path.dirname(__file__)) # pylint: disable=invalid-name

# Set the time after which the session expires. Flask's default is 31 days.
# Default: ``timedelta(days=1)`` corresponds to 1 day.
PERMANENT_SESSION_LIFETIME = timedelta(days=1)


# url to the database server:
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
    basedir, '..', 'fresque.sqlite')


# secret key used to generate unique csrf token
SECRET_KEY = 'Change-me-Im-famous'


DISTRIBUTIONS = {
    "f21": "Fedora 21",
    "f22": "Fedora 22",
    "f23": "Fedora 23",
    "el7": "Enterprise Linux 7",
    "el8": "Enterprise Linux 8",
    "rawhide": "Rawhide",
}

STATES = {
    "new": "just created", # No review yet. Don't delete this one.
    "review": "under review",
    "rejected": "rejected",
    "done": "included",
}
