import arrow
from flask import current_app
from sqlalchemy_utils import IPAddressType, ArrowType, ScalarListType, PasswordType
from mumble.models import db
from mumble.oauth import j4oauth


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, unique=True)
    mumble_password = db.Column(PasswordType(schemes=['bcrypt']))
    main_character = db.Column(db.String)
    main_character_id = db.Column(db.Integer)
    alliance_id = db.Column(db.Integer, nullable=True)
    alliance_name = db.Column(db.String, nullable=True)
    corporation_id = db.Column(db.Integer)
    corporation_name = db.Column(db.String)
    groups = db.Column(ScalarListType)
    last_ip = db.Column(IPAddressType, default=u'127.0.0.1')
    last_login_on = db.Column(ArrowType, default=lambda: arrow.utcnow())
    anonymous = True
    authenticated = False

    guest_passes = db.relationship('GuestPass', backref='created_by', foreign_keys="GuestPass.created_by_id")

    @property
    def full_name(self):
        return '{} / {} / {}'.format(self.main_character, self.corporation_name, self.alliance_name)

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return True

    def is_anonymous(self):
        return self.anonymous

    @property
    def is_admin(self):
        return current_app.config['ADMIN_GROUP'] in self.groups

    @property
    def is_allowed(self):
        if self.is_admin:
            return True
        return any(group in self.groups for group in current_app.config['ALLOWED_FC_GROUPS'])

    def get_id(self):
        return str(self.id)
