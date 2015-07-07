from flask import session
from flask_oauthlib.client import OAuth

oauth = OAuth()
j4oauth = oauth.remote_app('j4oauth', app_key='J4OAUTH')


@j4oauth.tokengetter
def j4oauth_tokengetter(token=None):
    return session.get('j4oauth_token')
