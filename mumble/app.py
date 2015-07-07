import os
from flask import Flask, session
from flask_wtf import CsrfProtect


csrf = CsrfProtect()

def create_app(config_file=None, config_object=None):
    """
    Bootstrap the flask application, registering blueprints, modules and other fun things.
    :param config_file: a python file containing key/values variables
    :param config_object: a python object (can be a dict) containing key/values variables
    :return: the app object
    """
    app = Flask(__name__, static_folder='public')

    # Configuration
    app.config.from_object('mumble.settings.BaseConfig')
    app.environment = os.getenv('J4LP_MUMBLE_ENV', 'dev')

    if config_file:
        app.config.from_pyfile(config_file)
    if config_object:
        app.config.update(**config_object)

    if app.environment != 'test':
        csrf.init_app(app)


    # Database, Migration, Login and models
    from mumble.models import db, login_manager, migrate
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    # Blueprints
    from mumble.blueprints import AccountView, MetaView, ServerView, GuestView
    AccountView.register(app)
    MetaView.register(app)
    ServerView.register(app)
    GuestView.register(app)

    # OAuth
    from mumble.oauth import oauth
    oauth.init_app(app)

    from mumble.m_api import mumble_api
    mumble_api.init_app(app)

    from mumble.utils import format_datetime, humanize, markdown_filter
    app.jinja_env.filters['format_datetime'] = format_datetime
    app.jinja_env.filters['humanize'] = humanize
    app.jinja_env.filters['markdown'] = markdown_filter

    @app.before_request
    def make_session():
        session.permanent = True

    return app
