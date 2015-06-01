# -*- coding: utf-8 -*-
'''
filter for the fresque flask application
'''

from __future__ import absolute_import, unicode_literals, print_function
import arrow
from fresque import APP


@APP.template_filter('short')
def shorted_commit(cid):
    """Gets short version of the commit id"""
    return cid[:6]


@APP.template_filter('humanize')
def humanize_date(date):
    """ Template filter returning the last commit date of the provided repo.
    """
    return arrow.get(date).humanize()
