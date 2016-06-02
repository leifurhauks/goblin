from __future__ import unicode_literals

import copy
import datetime
from calendar import timegm
from decimal import Decimal as _D
import re
import time
import warnings
from uuid import uuid1, uuid4
from uuid import UUID as _UUID

from goblin._compat import (
    text_type, string_types, float_types, integer_types, long_, PY3)

from goblin.properties.base import GraphProperty
from goblin.properties import geoshapes
from goblin.properties.validators import *


class String(GraphProperty):
    """
    String/CharField property

    :param str min_length: minimum string length
    :param str max_length: minimum string length
    :param str encoding: string encoding - 'utf-8' by default
    """

    validator = string_validator

    def __init__(self, *args, **kwargs):
        required = kwargs.get('required', False)
        self.min_length = kwargs.pop('min_length', 1 if required else None)
        self.max_length = kwargs.pop('max_length', None)
        self.encoding = kwargs.pop('encoding', 'utf-8')
        if 'default' in kwargs and isinstance(kwargs['default'], string_types):
            if not PY3:
                kwargs['default'] = kwargs['default'].encode(self.encoding)
        super(String, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value is not None:
            if isinstance(value, (bytes, bytearray)) and not isinstance(value,
                                                                        str):
                return value.decode(self.encoding)
            else:
                return value

    def validate(self, value):
        # Make sure it gets encoded correctly
        if isinstance(value, text_type) and not PY3:
            value = value.encode(self.encoding)

        if self.max_length:
            if len(value) > self.max_length:
                raise ValidationError('{} is longer than {} characters'.format(
                    self.property_name, self.max_length))
        if self.min_length:
            if len(value) < self.min_length:
                raise ValidationError(
                    '{} is shorter than {} characters'.format(
                        self.property_name, self.min_length))

        value = super(String, self).validate(value)
        return value


class Short(GraphProperty):
    """
    Short Data property type
    """
    deserializer = int
    serializer = int
    validator = integer_validator


class Integer(GraphProperty):
    """
    Integer Data property type
    """
    serializer = long_
    deserializer = long_
    validator = long_validator


class PositiveInteger(Integer):
    """
    Positive Integer Data property type
    """
    serializer = long_
    deserializer = long_
    validator = positive_integer_validator


class Long(GraphProperty):
    """
    Long Data property type
    """
    serializer = long_
    deserializer = long_
    validator = long_validator


class PositiveLong(Long):
    """
    Positive Long Data property type
    """
    serializer = long_
    deserializer = long_
    validator = positive_integer_validator


class DateTimeNaive(GraphProperty):
    """
    DateTime Data property type
    """
    data_type = "Double"
    validator = datetime_validator

    def __init__(self, strict=True, **kwargs):
        """
        Initialize date-time column with the given settings.

        :param strict: Whether or not to attempt to automatically coerce types
        :type strict: boolean

        """
        self.strict = strict
        super(DateTimeNaive, self).__init__(**kwargs)

    def to_python(self, value):
        if value is not None:
            if isinstance(value, datetime.datetime):
                return value
            return datetime.datetime.fromtimestamp(value / 1000)

    def to_database(self, value):
        value = super(DateTimeNaive, self).to_database(value)
        if value is None:
            return
        if not isinstance(value, datetime.datetime):
            if not self.strict and isinstance(value, string_types +
                                              integer_types + float_types):
                value = datetime.datetime.fromtimestamp(float(value))
            else:
                raise ValidationError(
                    "'{}' is not a datetime object".format(value))

        tmp = time.mktime(value.timetuple())
        tmp = int(tmp) * 1000
        return tmp


class DateTime(GraphProperty):
    """
    UTC DateTime Data property type
    """
    data_type = "Double"
    validator = datetime_utc_validator

    def __init__(self, strict=True, **kwargs):
        """
        Initialize date-time column with the given settings.

        :param strict: Whether or not to attempt to automatically coerce types
        :type strict: boolean

        """
        self.strict = strict
        super(DateTime, self).__init__(**kwargs)

    def to_python(self, value):
        if value is None:
            return
        try:
            if isinstance(value, datetime.datetime):
                if value.tzinfo == utc:
                    return self.validator(value)  # .astimezone(tz=utc)
                else:
                    return self.validator(value).astimezone(tz=utc)
        except:  # pragma: no cover
            # this shouldn't happen unless the validator has changed
            pass
        value = value / 1000
        return datetime.datetime.utcfromtimestamp(value).replace(tzinfo=utc)

    def to_database(self, value):
        value = super(DateTime, self).to_database(value)
        if value is None:
            return
        if not isinstance(value, datetime.datetime):
            if isinstance(value, string_types + integer_types + float_types):
                value = datetime.datetime.utcfromtimestamp(
                    float(value)).replace(tzinfo=utc)
            else:
                raise ValidationError(
                    "'{}' is not a datetime object".format(value))

        tmp = timegm(value.utctimetuple())
        tmp = tmp * 1000
        return tmp


class Date(DateTime):
    """For convenience, a wrapper around the DateTime property type."""
    def to_python(self, value):
        python_value = super(Date, self).to_python(value)
        return python_value.date()

    def to_database(self, value):
        if isinstance(value, datetime.date):
            value = datetime.datetime(value.year, value.month, value.day, tzinfo=utc)
        return super(Date, self).to_database(value)


class UUID(GraphProperty):
    """Universally Unique Identifier (UUID) type"""
    serializer = str
    validator = validate_uuid

    def to_python(self, value):
        val = super(UUID, self).to_python(value)
        if value is not None:
            if isinstance(value, (bytes, bytearray)) and not isinstance(value,
                                                                        str):
                return value.decode('utf-8')
            else:
                return value


class Boolean(GraphProperty):
    """
    Boolean Data property type
    """
    deserializer = bool
    validator = bool_validator


class Double(GraphProperty):
    """
    Double Data property type
    """
    deserializer = float
    validator = float_validator


Float = Double


class Decimal(GraphProperty):
    """
    Decimal Data property type
    """
    serializer = float
    validator = decimal_validator

    def to_python(self, value):
        val = super(Decimal, self).to_python(value)
        if val is not None:
            pos = 0
            if val < 0:
                pos = 1
            digs = [int(i) for i in str(val) if i.isdigit()]
            return _D((pos, digs, -3))


class URL(String):
    """
    URL Data property type
    String/CharField property

    :param str min_length: minimum string length
    :param str max_length: minimum string length
    :param str encoding: string encoding - 'utf-8' by default
    """

    validator = validate_url

    def __init__(self, *args, **kwargs):
        super(URL, self).__init__(*args, **kwargs)

    def validate(self, value):
        return super(URL, self).validate(value)


class Email(GraphProperty):
    """
    Email Data property type
    """

    validator = validate_email

    def __init__(self, *args, **kwargs):
        self.encoding = kwargs.pop('encoding', 'utf-8')
        if 'default' in kwargs and isinstance(kwargs['default'], string_types):
            if not PY3:
                kwargs['default'] = kwargs['default'].encode(self.encoding)
        super(Email, self).__init__(*args, **kwargs)

    def validate(self, value):
        # Make sure it gets encoded correctly
        if isinstance(value, text_type) and not PY3:
            value = value.encode(self.encoding)
        value = super(Email, self).validate(value)
        return value


class IPV4(GraphProperty):
    """
    IPv4 Data property type
    """
    serializer = int
    deserializer = ipaddress.IPv4Address
    validator = validate_ipv4_address

    def __init__(self, *args, **kwargs):
        self.encoding = kwargs.pop('encoding', 'utf-8')
        if 'default' in kwargs and isinstance(kwargs['default'], string_types):
            if not PY3:
                kwargs['default'] = kwargs['default'].encode(self.encoding)
        super(IPV4, self).__init__(*args, **kwargs)

    def validate(self, value):
        # Make sure it gets encoded correctly
        value = super(IPV4, self).validate(value)
        if value:
            if isinstance(value, text_type) and not PY3:
                value = value.encode(self.encoding)
            value = super(IPV4, self).validate(value)
        return value


class IPV6(GraphProperty):
    """
    IPv6 Data property type
    """

    validator = validate_ipv6_address

    def __init__(self, *args, **kwargs):
        super(IPV6, self).__init__(*args, **kwargs)

    def to_database(self, value):
        value = int(value)
        hi = value >> 64
        lo = value - (hi << 64)
        return [hi, lo]

    def to_python(self, value):
        if isinstance(value, list):
            hi, lo = value
            value = (hi << 64) + lo
            value = ipaddress.IPv6Address(value)
        return value

    def validate(self, value):
        return super(IPV6, self).validate(value)


class Point(GraphProperty):

    validator = validate_point

    def to_python(self, value):
        if isinstance(value, dict):
            value = geojson.Point(value['coordinates'])
        return value

    def to_database(self, value):
        if value:
            try:
                coords = list(geojson.utils.coords(value))[0]
            except:
                raise ValidationError(
                    "'{}' is not a datetime object".format(value))
            return (coords[1], coords[0])


class Circle(GraphProperty):

    validator = validate_circle

    def to_python(self, value):
        if isinstance(value, dict):
            coords = value['coordinates']
            value = geoshapes.Circle((coords[0], coords[1], value['radius']))
        return value

    def to_database(self, value):
        if value:
            coords = list(geojson.utils.coords(value))[0]
            lat = coords[1]
            lng = coords[0]
            radius = coords[2]
            return (lat, lng, radius)


class Box(GraphProperty):

    validator = validate_box

    def to_python(self, value):
        if isinstance(value, dict):
            coords = value['coordinates']
            value = geojson.Polygon(coords)
        return value

    def to_database(self, value):
        if value:
            coords = list(geojson.utils.coords(value))
            lngs = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            return (min(lats), min(lngs), max(lats), max(lngs))


class Slug(GraphProperty):
    """
    Slug Data property type
    """

    validator = validate_slug

    def __init__(self, *args, **kwargs):
        self.encoding = kwargs.pop('encoding', 'utf-8')
        if 'default' in kwargs and isinstance(kwargs['default'], string_types):
            if not PY3:
                kwargs['default'] = kwargs['default'].encode(self.encoding)
        super(Slug, self).__init__(*args, **kwargs)

    def validate(self, value):
        # Make sure it gets encoded correctly
        if isinstance(value, text_type) and not PY3:
            value = value.encode(self.encoding)

        value = super(Slug, self).validate(value)

        return value
