# -*- coding: utf-8 -*-

'''
Forms used in the web interface
'''

from __future__ import absolute_import, unicode_literals, print_function

import re

import flask
from flask_wtf import Form
from wtforms import (BooleanField, StringField, TextAreaField,
    SelectMultipleField, validators)
from wtforms.widgets import html_params, HTMLString

from fresque.lib.models import Package


def strip(s):
    if s:
        return s.strip()
    else:
        return ""


# http://wtforms.readthedocs.org/en/latest/widgets.html#custom-widgets
def select_multi_checkbox(field, ul_class='', **kwargs):
    kwargs.setdefault('type', 'checkbox')
    field_id = kwargs.pop('id', field.id)
    #html = ['<ul %s>' % html_params(id=field_id, class_=ul_class)]
    html = []
    for value, label, checked in field.iter_choices():
        choice_id = '%s-%s' % (field_id, value)
        options = dict(kwargs, name=field.name, value=value, id=choice_id)
        if checked:
            options['checked'] = 'checked'
        html.append('<div class="checkbox">\n  <label>')
        html.append('<input %s /> ' % html_params(**options))
        html.append(label)
        html.append('</label>\n</div>\n')
    return HTMLString(''.join(html))


class MultipleCheckboxesField(SelectMultipleField):
    """
    Reimplement the iter_choices method to take the defaults into account. Set
    the default widget to the proper checkbox-generating function while we're
    at it.
    """
    widget = select_multi_checkbox

    def iter_choices(self):
        for value, label in self.choices:
            ref = self.data or self.default
            selected = ref is not None and self.coerce(value) in ref
            yield (value, label, selected)


def existing_package(form, field):
    if flask.g.db.query(Package).filter_by(name=field.data).count() != 0:
        raise validators.ValidationError("Package already exists.")

RPM_NAME_RE = re.compile('^[\w_.-]+$') # TODO: use the real RPM regex
def package_naming_format(form, field):
    if not RPM_NAME_RE.match(field.data):
        raise validators.ValidationError(
            "Only letters, numbers, dots, dashes and underscores are allowed "
            "in the package name.")

class ListMinLength(object):
    def __init__(self, minlength):
        self.minlength = int(minlength)
    def __call__(self, form, field):
        if len(field.data) < self.minlength:
            raise validators.ValidationError(
                "You must choose at least %d of them." % self.minlength)


class NewPackage(Form):
    name          = StringField("Name", filters=[strip],
        validators=[validators.InputRequired(),
                    validators.Length(max=128),
                    existing_package,
                    package_naming_format])
    summary       = StringField("Summary", filters=[strip],
        validators=[validators.InputRequired(), validators.Length(max=255)])
    description   = TextAreaField("Description", filters=[strip],
        validators=[validators.InputRequired()])
    distributions = MultipleCheckboxesField("Distributions",
        validators=[ListMinLength(1)],
        widget=select_multi_checkbox)
