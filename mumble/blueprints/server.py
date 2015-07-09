from flask import render_template, url_for, redirect
from flask.ext.classy import FlaskView
from flask.ext.login import current_user, login_required
from mumble.m_api import mumble_api


class ServerView(FlaskView):

    decorators = [login_required]
    route_base = '/server'

    def index(self):
        return render_template('server/index.html', server=mumble_api.server)
