from __future__ import absolute_import, unicode_literals, print_function

import os

from alembic import command
from alembic.config import Config
from flask import current_app
from flask.ext.migrate import MigrateCommand
from sqlalchemy import MetaData



def _get_alembic_config():
    directory = current_app.extensions['migrate'].directory
    config = Config(os.path.join(directory, 'alembic.ini'))
    config.set_main_option('script_location', directory)
    return config

def sync_initial_data(db):
    from fresque import models
    ## Sync distributions
    # Remove distributions not in the config file
    for distro in models.Distribution.query.all():
        if distro.id not in current_app.config["DISTRIBUTIONS"].keys():
            distro.delete()
    # Add distributions in the config file
    for distro_id, distro_name in current_app.config["DISTRIBUTIONS"].items():
        if models.Distribution.query.get(distro_id) is None:
            db.session.add(models.Distribution(id=distro_id, name=distro_name))


@MigrateCommand.option('--sql', dest='sql', action='store_true', default=False, help="Don't emit SQL to database - dump to standard output instead")
def setupdb(sql=False):
    """Creates the database"""
    # Check for an existing database
    db = current_app.extensions["sqlalchemy"].db
    current_md = MetaData(db.engine)
    current_md.reflect()
    if current_md.tables:
        # Upgrade the existing DB
        command.upgrade(_get_alembic_config(), "head", sql=sql)
        print("Database upgraded.")
    else:
        # Create the DB from scratch
        from fresque import models
        db.Model.metadata.create_all(db.engine)
        command.stamp(_get_alembic_config(), "head", sql=sql)
        print("Database created.")
    sync_initial_data(db)
    db.session.commit()
