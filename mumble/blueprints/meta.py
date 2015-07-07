from flask import render_template, url_for, redirect
from flask.ext.classy import FlaskView
from flask.ext.login import current_user

class MetaView(FlaskView):
    route_base = '/'

    def index(self):
        if current_user.is_authenticated():
            return redirect(url_for('ServerView:index'))
        return render_template('meta/index.html')
