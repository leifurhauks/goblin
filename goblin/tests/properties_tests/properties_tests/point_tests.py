from __future__ import unicode_literals
import unittest

from tornado.testing import gen_test

import geojson

from goblin.tests import BaseGoblinTestCase
from goblin._compat import PY2
from .base_tests import GraphPropertyBaseClassTestCase, create_key
from goblin.properties.properties import Point, GraphProperty
from goblin._compat import print_
from goblin.models import Vertex
from goblin.exceptions import ValidationError


class PointPropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = Point
    good_cases = (geojson.Point((-115.81, 37.24)), (11.81, -37.24),
                  '{"type": "Point", "coordinates": [-115.81, 37.24]}')
    bad_cases = (11, ("11.81", "-37.24"))

    def test_to_database_method(self):
        d = self.klass()
        self.assertIsNone(d.to_database(None))
        self.assertIsInstance(d.to_database(geojson.Point((-115.81, 37.24))), tuple)

    def test_input_output_equality(self):
        # This is weird due to Titan
        # Values are submitted as (lat, lng), returned as (lng, lat)
        # Also, while Titan doesn't accept geojson
        # it returns it...
        p = geojson.Point([-115.81, 37.24])
        prop = self.klass()
        result = prop.to_python(dict(prop.validate(prop.to_database(p))))
        print_("Input: %s, Output: %s" % (p, result))
        self.assertEqual(
            p['coordinates'],
            [result['coordinates'][1], result['coordinates'][0]])


class PointTestVertex(Vertex):
    element_type = 'test_point_vertex'

    test_val = Point()


CHOICES = (
    (geojson.Point((115.81, 37.24)), 'A'),
    (geojson.Point((11.81, 56.24)), 'B')
)


class PointTestChoicesVertex(Vertex):
    element_type = 'test_point_choices_vertex'

    test_val = Point(choices=CHOICES)


class PointVertexTestCase(GraphPropertyBaseClassTestCase):

    @gen_test
    def test_point_io(self):
        print_("creating vertex")
        key = PointTestVertex.get_property_by_name('test_val')
        yield create_key(key, 'Geoshape')
        point = geojson.Point((115.81, 37.24))
        p1 = yield PointTestVertex.create(test_val=point)

        print_("getting vertex from vertex: %s" % p1)
        p2 = yield PointTestVertex.get(p1._id)
        print_("got vertex: %s\n" % p2)
        self.assertEqual(p2.test_val['coordinates'], p1.test_val['coordinates'])
        self.assertEqual(p2.test_val['type'], p1.test_val['type'])
        print_("deleting vertex")
        yield p2.delete()


class TestPointVertexChoicesTestCase(BaseGoblinTestCase):

    @gen_test
    def test_good_choices_key_io(self):
        print_("creating vertex")
        key = PointTestChoicesVertex.get_property_by_name('test_val')
        yield create_key(key, 'Geoshape')
        dt = yield PointTestChoicesVertex.create(
            test_val=geojson.Point((115.81, 37.24)))
        print_("validating input")
        self.assertEqual(
            dt.test_val['coordinates'],
            geojson.Point([115.81, 37.24])['coordinates'])
        print_("deleting vertex")
        yield dt.delete()

    @gen_test
    def test_good_choices_value_io(self):
        print_("creating vertex")
        key = PointTestChoicesVertex.get_property_by_name('test_val')
        yield create_key(key, 'Geoshape')
        dt = yield PointTestChoicesVertex.create(test_val='B')
        print_("validating input")
        point = geojson.Point([11.81, 56.24])
        self.assertEqual(
            dt.test_val['coordinates'], point['coordinates'])
        print_("deleting vertex")
        yield dt.delete()

    @gen_test
    def test_bad_choices_io(self):
        key = PointTestChoicesVertex.get_property_by_name('test_val')
        yield create_key(key, 'Geoshape')

        with self.assertRaises(ValidationError):
            print_("creating vertex")
            dt = yield PointTestChoicesVertex.create(
                test_val=geojson.Point((100.01, 37.24)))
