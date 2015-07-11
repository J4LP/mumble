import os
import binascii
from flask import render_template, url_for, redirect, flash, request, session
from flask.ext.classy import FlaskView, route
from flask.ext.login import current_user, login_required
from mumble.forms import GuestAccessForm, GuestUserForm
from mumble.m_api import mumble_api
from mumble.models import db, GuestPass, GuestUser


class GuestView(FlaskView):

    route_base = '/guest'

    @login_required
    @route('/new', methods=['GET', 'POST'])
    def new(self):
        form = GuestAccessForm()
        if form.validate_on_submit():
            guest_pass = GuestPass(
                reason=form.reason.data,
                expires_on=form.expiration.datetime,
                max_guests=form.max_guests.data,
                created_by=current_user
            )
            db.session.add(guest_pass)
            db.session.commit()
            flash('New guest pass created with success.', 'success')
            return redirect(url_for('GuestView:get', pass_id=guest_pass.id))
        return render_template('guest/new.html', form=form)

    @login_required
    def get(self, pass_id):
        guest_pass = GuestPass.query.get_or_404(pass_id)
        return render_template('guest/get.html', guest_pass=guest_pass)

    @route('/token/<token>', methods=['GET', 'POST'])
    def token(self, token):
        guest_pass = GuestPass.by_token(token)
        if len(guest_pass.users) >= guest_pass.max_guests:
            return render_template('guest/guest_pass_full.html')
        form = GuestUserForm()
        if form.validate_on_submit():
            password = binascii.b2a_hex(os.urandom(16))
            guest_user = GuestUser(
                password=password,
                name=form.name.data,
                guest_pass=guest_pass
            )
            if form.corporation.data:
                guest_user.corporation = form.corporation.data
                guest_user.corporation_id = form.corporation.corporation_id
            if form.alliance.data:
                guest_user.alliance = form.alliance.data
                guest_user.alliance_id = form.alliance.alliance_id
            db.session.add(guest_user)
            db.session.commit()
            return render_template('guest/user.html', guest_pass=guest_pass, guest_user=guest_user, password=password)
        return render_template('guest/token.html', guest_pass=guest_pass, token=token, form=form)

    @login_required
    @route('/ban/<user_id>', methods=['POST'])
    def ban_user(self, user_id):
        guest_user = GuestUser.query.get_or_404(user_id)
        guest_user.banned = True
        db.session.add(guest_user)
        db.session.commit()
        flash('Guest user banned and kicked from Mumble', 'success')
        return redirect(url_for('GuestView:get', pass_id=guest_user.guest_pass_id))

    @login_required
    def admin(self):
        guest_passes = GuestPass.query.filter_by(expired=request.args.get('expired', 'False') == 'True').all()
        return render_template('guest/admin.html', guest_passes=guest_passes)
