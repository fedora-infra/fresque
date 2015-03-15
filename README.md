Fresque
=======

Fedora Review Server

Installation
----------------
To download the project, open your terminal and type the following command

```bash
	$ git clone https://github.com/fedora-infra/fresque.git
	$ cd fresque
	$ python setup.py install
```
It will clone and install the project on your local machine

Dependencies
------------
Fresque is a [Flask] application. The review data is stored into a relational database
using [SQLAlchemy] as Object Relational Mapper and [alembic] to handle database
schema changes.

The dependecies can be found in the `requirements.txt` file of the project

Running a development instance:
-------------------------------
First lets make a seperate virtual environment for the project
to avoid conflicts of its dependecy with other python packages.
after that install [virtualenv wrapper] which provides better CLI interface
for the [virtualenv].

```bash
	$ pip install virtualenv
	$ pip install virtualwrapper
```
Then setup the path for the virtualenv by adding below lines
in your `bashrc` file.

```bash
 	export WORKON_HOME=$HOME/.virtualenvs
  	export VIRTUALENVWRAPPER_VIRTUALENV_ARGS='--no-site-packages'
  	export PIP_VIRTUALENV_BASE=$WORKON_HOME
  	source /usr/local/bin/virtualenvwrapper.sh
```
after the bash profile setup, now you can create a seperate
virtualenv for this project.

```bash
	// create a virtualenv named fresque
	$ mkvirtualenv fresque
	// if not automatically switched to fresque virtualenv, then type
	$ workon fresque
	// now your bash prompt line will change to
	(fresque) $
```

Now clone the source:

```bash
	$ git clone https://github.com/fedora-infra/fresque.git
	$ cd fresque
	$ pip install -r requirements.txt
	// set up the database before running the server
	$ python createdb.py
	// now start the server
	$ python runserver.py
```
Thats all now head to [http://localhost:5000](http://localhost:5000)

Testing
-------

Currently fresque doesn't have any unit tests.


License:
--------
This project is licensed GPLv3+.

[Flask]:http://flask.pocoo.org/
[SQLAlchemy]:http://www.sqlalchemy.org/
[alembic]:https://bitbucket.org/zzzeek/alembic
[virtualenv]:https://virtualenv.pypa.io/en/latest/
[virtualenv wrapper]:https://virtualenvwrapper.readthedocs.org/en/latest/

