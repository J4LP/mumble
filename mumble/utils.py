import bleach
import evelink
import markdown
import arrow
from mumble.exceptions import InvalidCorporationError, InvalidAllianceError
from mumble.models import redis
from six import iteritems


try:
    from urlparse import urlparse, urljoin
except ImportError:
    from urllib.parse import urlparse, urljoin
from flask import request, redirect, url_for


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def safe_redirect(endpoint='MetaView:index', next=None, **kwargs):
    if is_safe_url(next):
        return redirect(next)
    target = get_redirect_target()
    return redirect(target or url_for(endpoint, **kwargs))


def humanize(date):
    try:
        return arrow.get(date).humanize()
    except Exception:
        return 'Invalid date'


def format_datetime(date):
    try:
        return arrow.get(date).format('DD MMMM YYYY - HH:mm')
    except Exception:
        return 'Invalid date'


def markdown_filter(content):
    bleach.ALLOWED_TAGS += 'p'
    return bleach.clean(markdown.markdown(content, strip=True))


def get_corporation_id_by_name(name):
    corporation_id = redis.hget('corporations', name.lower())
    if not corporation_id:
        eve = evelink.eve.EVE()
        corporation_id = eve.character_id_from_name(name)[0]
        if corporation_id == 0:
            raise InvalidCorporationError(name)
        try:
            api = evelink.api.API()
            corp = evelink.corp.Corp(api)
            sheet = corp.corporation_sheet(corp_id=corporation_id)[0]
        except evelink.api.APIError:
            raise InvalidCorporationError(name)
        redis.hset('corporations', sheet['name'], sheet['id'])
    return int(corporation_id)

def get_alliance_id_by_name(name):
    if not redis.exists('alliances'):
        eve = evelink.eve.EVE()
        alliance_map = {}
        for alliance_id, alliance in iteritems(eve.alliances()[0]):
            alliance_map[alliance['name'].lower()] = alliance_id
        redis.hmset('alliances', alliance_map)
    alliance_id = redis.hget('alliances', name.lower())
    if not alliance_id:
        raise InvalidAllianceError(name)
    return int(alliance_id)
