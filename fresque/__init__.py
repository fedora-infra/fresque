from __future__ import absolute_import, unicode_literals, print_function

import os

from flask import Flask
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.sqlalchemy import SQLAlchemy
from pkg_resources import resource_filename


app = Flask(__name__)
app.config.from_object('fresque.default_config')
if 'FRESQUE_CONFIG' in os.environ: # pragma: no cover
    app.config.from_envvar('FRESQUE_CONFIG')

from fresque import database

db = SQLAlchemy(app)
Migrate(app, db, directory=resource_filename("fresque", "migrations"))
manager = Manager(app)
manager.add_command('db', MigrateCommand)


from fresque import views
#from fresque import views, models



if __name__ == '__main__':
    manager.run()
