import arrow
from flask.ext.login import LoginManager
from flask.ext.migrate import Migrate
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy_utils import force_auto_coercion

force_auto_coercion()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

from .user import User
from .guest import GuestPass, GuestUser

login_manager.login_view = 'AccountView:login'


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return None
    user.anonymous = False
    user.authenticated = True
    return user



# @db.event.listens_for(Structure, 'before_update', propagate=True)
# def timestamp_before_update(mapper, connection, target):
#     target.updated_on = arrow.utcnow()

