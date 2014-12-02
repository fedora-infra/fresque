
import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..', 'fresque.sqlite')
#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

SECRET_KEY = 'Change-me-Im-famous'

DISTRIBUTIONS = {
    "f21": "Fedora 21",
    "f22": "Fedora 22",
    "f23": "Fedora 23",
    "el7": "Enterprise Linux 7",
    "el8": "Enterprise Linux 8",
    "rawhide": "Rawhide",
}
