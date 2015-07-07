import base64
import json
import arrow
from flask import render_template, redirect, url_for, flash, session, request
from flask.ext.classy import FlaskView, route
from flask.ext.login import login_user, current_user
from ..models import db, User
from ..oauth import j4oauth
from ..utils import safe_redirect


class AccountView(FlaskView):

    def login(self):
        state = {'next': request.args.get('next') or url_for('MetaView:index')}
        state = base64.b64encode(str(json.dumps(state)))
        return j4oauth.authorize(callback=url_for('AccountView:authorize', _external=True), state=state)

    def authorize(self):
        """
        OAuth callback. Will load the state and the response and login the user if it can.

        TODO: Check for groups and set attributes based on that (admin or not, etc...)
        """
        try:
            state = json.loads(base64.b64decode(request.args.get('state')).decode('UTF-8'))
        except Exception as e:
            print(e)
            state = {'next': url_for('MetaView:index')}
        res = j4oauth.authorized_response()
        if not res:
            flash('Invalid login attempt.')
            return redirect(url_for('MetaView:index'))
        session['j4oauth_token'] = (
            res['access_token'], ''
        )
        user_info = j4oauth.get('auth_user').data['user']
        if user_info['auth_status'] not in ('Internal', 'Ally'):
            flash('You are not authorized to access this application', 'danger')
            return redirect(url_for('Metaview:index'))
        user = User.query.filter_by(user_id=user_info['user_id']).first()
        if not user:
            user = User(user_id=user_info['user_id'])
        user.main_character = user_info['main_character']
        user.main_character_id = user_info['main_character_id']
        user.alliance_name = user_info['alliance']
        user.corporation_name = user_info['corporation']
        user.groups = j4oauth.get('auth_groups').data['groups']
        db.session.add(user)
        db.session.commit()
        if login_user(user):
            user.last_login_on = arrow.utcnow()
            user.last_ip = request.remote_addr
            flash('Welcome back {}!'.format(user.main_character))
            return safe_redirect(next=state['next'])
        else:
            flash('There was an issue logging you in.', 'danger')
            return redirect(url_for('MetaView:index'))

    def logout(self):
        session.clear()
        return redirect(url_for('MetaView:index'))

    @route('/password', methods=['POST'])
    def password(self):
        password = request.form.get('password')
        if not password:
            flash('Invalid password given.', 'danger')
        elif len(password) <= 6:
            flash('Password must be > 6 characters.', 'danger')
        else:
            user = current_user._get_current_object()
            user.mumble_password = password
            db.session.add(user)
            db.session.commit()
            flash('Mumble password updated with success.', 'success')
        return redirect(url_for('MetaView:index'))

