import os
import uuid
import hashlib
import Ice
import Murmur
from mumble.models import User, GuestUser, GuestPass, db
from six import itervalues, viewvalues
import evelink
import arrow

RET_FALLTHROUGH = (-2, '', [])
RET_DENIED = (-1, '', [])
TICKER_CACHE = {'Fweddit': 'FWORT'}


class Authenticator(Murmur.ServerAuthenticator):

    def __init__(self, server, adapter, app):
        self.server = server
        self.adapter = adapter
        self.app = app

    def authenticate(self, name, password, certificates, certhash, certstrong, current=None):
        with self.app.app_context():
            if name == 'SuperUser':
                return RET_FALLTHROUGH
            user = User.query.filter_by(user_id=name).first()
            if not user:
                try:
                    uuid.UUID(name, version=4)
                except ValueError:
                    return RET_DENIED
                guest_user = GuestUser.query.get(name)
                if guest_user:
                    if not guest_user.password == password or guest_user.banned:
                        return RET_DENIED
                    return int(hashlib.sha1(guest_user.id.hex).hexdigest()[:8], 16), '[{}] Guest - {}'.format(self.get_ticker(guest_user.corporation), guest_user.name), ['Guest']
                else:
                    return RET_DENIED
            if not user.mumble_password == password:
                return RET_DENIED
            return int(hashlib.sha1(user.user_id).hexdigest()[:8], 16), '[{}] {}'.format(self.get_ticker(user.corporation_name), user.main_character), user.groups

    def get_ticker(self, corporation):
        if not corporation in TICKER_CACHE:
            api = evelink.api.API()
            eve = evelink.eve.EVE()
            corporation_id = eve.character_id_from_name(corporation)[0]
            corp = evelink.corp.Corp(api)
            sheet = corp.corporation_sheet(corp_id=corporation_id)[0]
            TICKER_CACHE[corporation] = sheet['ticker']
        return TICKER_CACHE[corporation]

    def getInfo(self, user_id):
        return (False, {})

    def nameToId(self, name):
        return -2

    def idToName(self, id):
        return ''

    def idToTexture(self, id, name):
        return []


class MumbleServer(object):

    def __init__(self, server, meta):
        self.server = server
        self.meta = meta

    @property
    def configuration(self):
        return self.server.getAllConf()

    @property
    def id(self):
        return self.server.id()

    @property
    def online(self):
        return self.server.isRunning()

    @property
    def uptime(self):
        return self.server.getUptime()

    @property
    def host(self):
        return self.server.getConf('host')

    @property
    def port(self):
        port = self.server.getConf('port')
        if not port:
            port = int(self.meta.getDefaultConf().get('port', 0)) + self.id - 1
        return int(port)

    @property
    def users(self):
        return viewvalues(self.server.getUsers())

    @property
    def rooms(self):
        return viewvalues(self.server.getChannels())

    def room_users(self, room):
        return [user for user in self.users if user.channel == room.id]

    def set_authenticator(self, authenticator):
        return self.server.setAuthenticator(authenticator)

    def set_server_callback(self, callback):
        return self.server.addCallback(callback)

class ServerCallback(Murmur.ServerCallback):

    def __init__(self, app):
        self.app = app

    def userConnected(self, user, current=None):
        print('User connected')
        try:
            with self.app.app_context():
                if 'Guest' in user.name:
                    parsed_name = user.name.split('Guest - ')[1]
                    guest_user = GuestUser.query.filter_by(name=parsed_name).first()
                    if not guest_user:
                        return
                    db_user = guest_user
                else:
                    parsed_name = user.name.split('] ')[1]
                    db_user = User.query.filter_by(main_character=parsed_name).first()
                    if not db_user:
                        return
                db_user.last_ip = '.'.join([str(x) for x in user.address[-4:]])
                db_user.last_login_on = arrow.utcnow()
                db.session.add(db_user)
                db.session.commit()
        except Exception as e:
            self.app.logger.exception(e)

    def userDisconnected(self, user, current=None):
        pass

    def userStateChanged(self, user, current=None):
        pass

    def userTextMessage(self, user, message, current=None):
        pass

    def channelCreated(self, channel, current=None):
        pass

    def channelRemoved(self, channel, current=None):
        pass

    def channelStateChanged(self, channel, current=None):
        pass


class MumbleAPI(object):

    app = None
    server_id = 1

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.server_id = app.config.get('SERVER_ID', 1)
        self.ice = Ice.initialize()
        self.proxy = self.ice.stringToProxy('Meta:tcp ' + app.config['ICE_HOST'].encode('ascii'))
        self.meta = Murmur.MetaPrx.checkedCast(self.proxy)
        adapter = self.ice.createObjectAdapterWithEndpoints('Callback.Client', 'tcp -h 127.0.0.1')
        adapter.activate()
        authenticator = Authenticator(self.server, adapter, app)
        server_authenticator = Murmur.ServerAuthenticatorPrx.uncheckedCast(adapter.addWithUUID(authenticator))
        self.server.set_authenticator(server_authenticator)
        server_callback = Murmur.ServerCallbackPrx.uncheckedCast(adapter.addWithUUID(ServerCallback(self.app)))
        self.server.set_server_callback(server_callback)

    @property
    def server(self):
        return MumbleServer(self.meta.getServer(self.server_id), meta=self.meta)




mumble_api = MumbleAPI()
