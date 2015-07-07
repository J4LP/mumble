import uuid
import arrow
from flask import current_app
from itsdangerous import URLSafeSerializer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils import IPAddressType, ArrowType, UUIDType, PasswordType
from mumble.exceptions import GuestPassExpiredError
from mumble.models import db


class GuestUser(db.Model):
    id = db.Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)
    password = db.Column(PasswordType(schemes=['bcrypt']), nullable=False)
    name = db.Column(db.String, nullable=False)
    corporation_id = db.Column(db.Integer, nullable=False)
    corporation = db.Column(db.String, nullable=False)
    alliance_id = db.Column(db.Integer, nullable=True)
    alliance = db.Column(db.String, nullable=True)
    guest_pass_id = db.Column(UUIDType(binary=False), db.ForeignKey('guest_pass.id'))
    banned = db.Column(db.Boolean, default=False)
    last_ip = db.Column(IPAddressType, default=u'127.0.0.1')
    last_login_on = db.Column(ArrowType, default=arrow.utcnow)
    created_on = db.Column(ArrowType, default=arrow.utcnow, nullable=False)
    updated_on = db.Column(ArrowType, default=arrow.utcnow, nullable=False)


class GuestPass(db.Model):
    id = db.Column(UUIDType(binary=False), default=uuid.uuid4, primary_key=True)
    reason = db.Column(db.String, nullable=False)
    expires_on = db.Column(ArrowType, nullable=False)
    max_guests = db.Column(db.Integer, default=0)
    created_on = db.Column(ArrowType, default=arrow.utcnow, nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    users = db.relationship('GuestUser', backref='guest_pass')

    @property
    def token(self):
        return URLSafeSerializer(current_app.config['SECRET_KEY'], salt='new_guest').dumps(str(self.id))

    @hybrid_property
    def expired(self):
        return self.expires_on < arrow.utcnow()

    @staticmethod
    def by_token(token):
        pass_id = URLSafeSerializer(current_app.config['SECRET_KEY'], salt='new_guest').loads(token)
        guest_pass = GuestPass.query.get(pass_id)
        if guest_pass.expired:
            raise GuestPassExpiredError(guest_pass)
        return guest_pass

    users = db.relationship('GuestUser', backref='guest_pass')
