from __future__ import unicode_literals

from collections import Iterable
import datetime
import re
from decimal import Decimal as _D
import six

try:
    from urllib.parse import urlsplit, urlunsplit
except ImportError:     # Python 2
    from urlparse import urlsplit, urlunsplit

from pytz import utc
import ipaddress

import geojson

from goblin._compat import (string_types, text_type, float_types,
                            integer_types, array_types, bool_types, print_)
from goblin.exceptions import GoblinException, ValidationError
from goblin.properties import geoshapes


# These values, if given to validate(), will trigger the self.required check.
EMPTY_VALUES = (None, '', [], (), {})


class BaseValidator(object):
    message = 'Enter a valid value.'
    code = 'invalid'

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        """
        Validates that the input passes validation
        """
        return value


pass_all_validator = BaseValidator()


class BooleanValidator(BaseValidator):
    message = 'Enter a valid Boolean.'

    def __call__(self, value):
        if not isinstance(value, bool_types):
            raise ValidationError(self.message, self.code)
        return value


bool_validator = BooleanValidator()


class NumericValidator(BaseValidator):
    message = 'Enter a valid number.'
    data_types = float_types + integer_types + (_D, )

    def __call__(self, value):
        if not isinstance(value, self.__class__.data_types):
            raise ValidationError(self.message, code=self.code)
        return value


numeric_validator = NumericValidator()


class FloatValidator(NumericValidator):
    data_types = float_types


float_validator = FloatValidator()


class DecimalValidator(BaseValidator):
    data_types = float_types + (_D, )
    message = 'Please pass precision 3 Decimal or float'

    def __call__(self, value):
        dec_str = str(value)
        prec = dec_str[::-1].find('.')
        if not isinstance(value, self.__class__.data_types) or prec > 3:
            raise ValidationError(self.message, code=self.code)
        return value


decimal_validator = DecimalValidator()


class IntegerValidator(NumericValidator):
    data_types = integer_types


integer_validator = IntegerValidator()


class LongValidator(NumericValidator):
    data_types = integer_types


long_validator = LongValidator()


class PositiveIntegerValidator(NumericValidator):
    data_types = integer_types

    def __call__(self, value):
        super(PositiveIntegerValidator, self).__call__(value)
        if value < 0:
            raise ValidationError("Value must be 0 or greater")
        return value

positive_integer_validator = PositiveIntegerValidator()


class StringValidator(BaseValidator):
    message = 'Enter a valid string: {}'
    data_type = string_types

    def __call__(self, value):
        if not isinstance(value, self.data_type):
            raise ValidationError(self.message.format(value), code=self.code)
        return value


string_validator = StringValidator()


class DateTimeValidator(BaseValidator):
    message = 'Not a valid DateTime: {}'

    def __call__(self, value):
        if not isinstance(value, datetime.datetime):
            raise ValidationError(self.message.format(value), code=self.code)
        return value


datetime_validator = DateTimeValidator()


class DateTimeUTCValidator(BaseValidator):
    message = 'Not a valid UTC DateTime: {}'

    def __call__(self, value):
        super(DateTimeUTCValidator, self).__call__(value)
        if not isinstance(value, datetime.datetime):
            raise ValidationError(self.message.format(value), code=self.code)
        if value and value.tzinfo != utc:
            # print_("Got value with timezone: {} - {}".format(value, value.tzinfo))
            try:
                value = value.astimezone(tz=utc)
            except ValueError:  # last ditch effort
                try:
                    value = value.replace(tzinfo=utc)
                except (AttributeError, TypeError):
                    raise ValidationError(
                        self.message.format(value), code=self.code)
            except AttributeError:  # pragma: no cover
                # This should never happen, unless it isn't a datetime object
                raise ValidationError(self.message % (value, ), code=self.code)
        # print_("Datetime passed validation: {} - {}".format(value, value.tzinfo))
        return value


datetime_utc_validator = DateTimeUTCValidator()


class RegexValidator(BaseValidator):

    regex = ''
    data_type = string_types

    def __init__(self, regex=None, message=None, code=None):
        super(RegexValidator, self).__init__(message=message, code=code)
        if regex is not None:
            self.regex = regex

        # Compile the regex if it was not passed pre-compiled.
        if isinstance(self.regex, string_types):  # pragma: no cover
            self.regex = re.compile(self.regex)

    def __call__(self, value):
        """
        Validates that the input matches the regular expression.
        """
        if not isinstance(value, self.data_type):
            raise ValidationError(self.message.format(value), code=self.code)
        if not self.regex.search(text_type(value)):
            raise ValidationError(self.message, code=self.code)
        else:
            return value


class URLValidator(RegexValidator):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    message = 'Enter a valid URL address: {}'
    code = 'invalid'

    def __call__(self, value):
        try:
            super(URLValidator, self).__call__(value)
        except ValidationError as e:
            # Trivial case failed. Try for possible IDN domain
            if value:
                value = text_type(value)
                scheme, netloc, path, query, fragment = urlsplit(value)
                try:
                    # IDN -> ACE
                    netloc = netloc.encode('idna').decode('ascii')
                except UnicodeError:  # invalid domain part
                    raise ValidationError(self.message.format(value),
                                          code=self.code)
                url = urlunsplit((scheme, netloc, path, query, fragment))
                return super(URLValidator, self).__call__(url)
            else:
                raise ValidationError(self.message.format(value),
                                      code=self.code)
        return value


validate_url = URLValidator()


class EmailValidator(RegexValidator):

    regex = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
        r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)$)'  # domain
        r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$',  # literal form, ipv4 address (SMTP 4.1.3)
        re.IGNORECASE)

    message = 'Enter a valid email address: {}'
    code = 'invalid'

    def __call__(self, value):
        try:
            super(EmailValidator, self).__call__(value)
        except ValidationError as e:
            # Trivial case failed. Try for possible IDN domain-part
            if value and isinstance(value, string_types) and '@' in value:
                parts = value.split('@')
                try:
                    parts[-1] = parts[-1].encode('idna').decode('ascii')
                except UnicodeError:
                    raise ValidationError(self.message.format(value),
                                          code=self.code)
                super(EmailValidator, self).__call__('@'.join(parts))
            else:
                raise ValidationError(self.message.format(value),
                                      code=self.code)
        return value


validate_email = EmailValidator()


slug_re = re.compile(r'^[-a-zA-Z0-9_]+$')
validate_slug = RegexValidator(
    slug_re,
    "Enter a valid 'slug' - letters, numbers, underscores or hyphens.",
    'invalid')


class IPValidator(BaseValidator):

    def __init__(self, ipv_class):
        self.ipv_class = ipv_class

    def __call__(self, value):
        try:
            value = self.ipv_class(value)
        except Exception as exc:
            raise ValidationError(
                'Raised {}: {}'.format(exc.__class__, exc.args[0]),
                code=self.code)
        else:
            return value


validate_ipv4_address = IPValidator(ipaddress.IPv4Address)
validate_ipv6_address = IPValidator(ipaddress.IPv6Address)


class PointValidator(BaseValidator):

    def __init__(self):
        super(PointValidator, self).__init__()
        self.geotype = geojson.Point

    def __call__(self, value):
        if isinstance(value, string_types):
            try:
                value = geojson.loads(value)
            except Exception as exc:
                raise ValidationError(
                    'Raised {}: {}'.format(exc.__class__, exc.args[0]),
                    code=self.code)
            if not isinstance(value, self.geotype):
                raise ValidationError(
                    'Raised {}: {}'.format(exc.__class__, exc.args[0]),
                    code=self.code)
        elif not isinstance(value, self.geotype):
            try:
                value = self.geotype(value)
            except Exception as exc:
                raise ValidationError(
                    'Raised {}: {}'.format(exc.__class__, exc.args[0]),
                    code=self.code)
        return value


validate_point = PointValidator()


class CircleValidator(PointValidator):

    def __init__(self):
        super(CircleValidator, self).__init__()
        self.geotype = geoshapes.Circle


validate_circle = CircleValidator()


class BoxValidator(PointValidator):

    def __init__(self):
        super(BoxValidator, self).__init__()
        self.geotype = geojson.Polygon

    def __call__(self, value):
        value = super(BoxValidator, self).__call__(value)
        coords = list(geojson.utils.coords(value))
        lngs = {c[0] for c in coords}
        lats = {c[1] for c in coords}
        if not len(lngs) == 2 and not len(lats) == 2:
            raise ValidationError("Coordinates do not form box",code=self.code)
        for lng in lngs:
            for lat in lats:
                if (lng, lat) not in coords:
                    raise ValidationError("Coordinates do not form box",
                                          code=self.code)
        return value




validate_box = BoxValidator()


re_uuid = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')
validate_uuid = RegexValidator(re_uuid, 'Enter a valid UUID.', 'invalid')
