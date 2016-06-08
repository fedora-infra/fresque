# -*- coding: utf-8 -*-
'''
filter for the fresque flask application
'''

from __future__ import absolute_import, unicode_literals, print_function

import arrow
import time

from pygments import highlight
from pygments.lexers.text import DiffLexer
from pygments.formatters import HtmlFormatter

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


@APP.template_filter('strftime')
def strftime(timestamp, format):
    return time.strftime(format, time.gmtime(timestamp))


@APP.template_filter('html_diff')
def html_diff(diff):
    """Display diff as HTML"""
    if diff is None:
        return
    return highlight(
        diff,
        DiffLexer(),
        HtmlFormatter(
            noclasses=True,
            style="pastie",)
    )


@APP.template_filter('patch_to_diff')
def patch_to_diff(patch):
    """Render a hunk as a diff"""
    content = ""
    for hunk in patch.hunks:
        content = content + "@@ -%i,%i +%i,%i @@\n" % (
            hunk.old_start, hunk.old_lines, hunk.new_start, hunk.new_lines)
        for line in hunk.lines:
            content = content + ' '.join(line)
    return content
