import arrow
from flask_wtf import Form
from sqlalchemy.orm.exc import NoResultFound
from wtforms import StringField, SelectField, TextAreaField, validators, ValidationError, SelectMultipleField
from wtforms.fields.html5 import IntegerField, DateTimeField
import requests
from mumble.exceptions import InvalidCorporationError, InvalidAllianceError
from mumble.utils import get_corporation_id_by_name, get_alliance_id_by_name


def validate_corporation(form, field):
    try:
        field.corporation_id = get_corporation_id_by_name(field.data)
    except requests.exceptions.ConnectionError:
        field.data = None
        return
    except InvalidCorporationError as e:
        raise ValidationError('Invalid corporation: {}'.format(e.corporation))
    except Exception as e:
        raise ValidationError('Unknown exception: {}'.format(str(e)))

def validate_alliance(form, field):
    try:
        field.alliance_id = get_alliance_id_by_name(field.data)
    except requests.exceptions.ConnectionError:
        field.data = None
        return
    except InvalidAllianceError as e:
        raise ValidationError('Invalid alliance: {}'.format(e.alliance))
    except Exception as e:
        raise ValidationError('Unknown exception: {}'.format(str(e)))


def validate_time(form, field):
    print(field.data)
    try:
        field.datetime = arrow.get(field.data, 'MM/DD/YYYY h:m A')
    except arrow.parser.ParserError as e:
        print(e)
        raise ValidationError('Invalid datetime format.')
    except Exception as e:
        raise ValidationError('Unknown exception: {}'.format(str(e)))


class GuestAccessForm(Form):
    reason = StringField(
        'Reason',
        validators=[validators.required()],
        description={
            'placeholder': 'Fleet by XXX',
            'icon': 'fa-info',
        }
    )
    expiration = StringField(
        'Expiration',
        validators=[validators.required(), validate_time],
        description={
            'placeholder': 'Click to open date picker',
            'icon': 'fa-clock-o',
            'help': ['UTC (Eve) time.']
        }
    )
    max_guests = IntegerField(
        'Maximum guests',
        validators=[validators.required()],
        description={'placeholder': '', 'help': ['How many guests will be allowed ?'], 'icon': 'fa-users'}
    )


class GuestUserForm(Form):
    name = StringField(
        'Name',
        validators=[validators.required()],
        description={
            'placeholder': 'Vadrin Hegirin',
            'icon': 'fa-user',
            'help': ['Try to write it with proper case']
        }
    )
    corporation = StringField(
        'Corporation',
        validators=[validators.optional(), validate_corporation],
        description={
            'placeholder': 'Fweddit',
            'icon': 'fa-group',
            'help': ['Corporation is not mandatory but recommended for Eve related OPs.']
        }
    )
    alliance = StringField(
        'Alliance',
        validators=[validators.optional(), validate_alliance],
        description={
            'placeholder': 'I Whip My Slaves Back and Forth',
            'icon': 'fa-group',
            'help': ['Alliance is not mandatory but recommended for Eve related OPs.']
        }
    )
