'''
filter for the fresque flask application
'''

from __future__ import absolute_import, unicode_literals, print_function
import time


def shorted_commit(cid):
    """Gets short version of the commit id"""
    return cid[:6]


def human_readable_time(ctime):
    timediff = time.time() - ctime
    if timediff < 0:
        return 'in the future'
    if timediff < 60:
        return 'just now'
    if timediff < 120:
        return 'a minute ago'
    if timediff < 3600:
        return "%d minutes ago" % (timediff / 60)
    if timediff < 7200:
        return "an hour ago"
    if timediff < 86400:
        return "%d hours ago" % (timediff / 3600)
    if timediff < 172800:
        return "a day ago"
    if timediff < 2592000:
        return "%d days ago" % (timediff / 86400)
    if timediff < 5184000:
        return "a month ago"
    if timediff < 31104000:
        return "%d months ago" % (timediff / 2592000)
    if timediff < 62208000:
        return "a year ago"
    return "%d years ago" % (timediff / 31104000)
