import os


class BaseConfig(object):
    """File based configuration object."""

    #: Application absolute path
    APP_DIR = os.path.abspath(os.path.dirname(__file__))

    #: Project root
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))

    #: Turn on debug mode by environment
    DEBUG = os.getenv('DEBUG', True)

    #: Default SQLAlchemy database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + PROJECT_ROOT + '/mumble.sqlite'

    #: Turn on debug mode for SQLAlchemy (prints out queries)
    SQLALCHEMY_ECHO = os.getenv('DEBUG', False)

    #: Eve related settings, see :ref:`eve_settings`.
    EVE = {
        'auth_name': 'J4LP'
    }

    #: The admin group
    ADMIN_GROUP = 'Admin'

    #: HTTP scheme (can be http, https, etc...)
    HTTP_SCHEME = 'http'

    #: Serve name used to generate external urls
    #: See "More on SERVER_NAME" http://flask.pocoo.org/docs/0.10/config/#builtin-configuration-values
    #: You might have to change that and add it to your hosts file, adjust to your dev port if needed
