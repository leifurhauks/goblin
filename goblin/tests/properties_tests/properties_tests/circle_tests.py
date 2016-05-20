from __future__ import unicode_literals
import unittest

from tornado.testing import gen_test

import geojson

from goblin.tests import BaseGoblinTestCase
from goblin._compat import PY2
from .base_tests import GraphPropertyBaseClassTestCase, create_key
from goblin.properties.properties import Circle, GraphProperty
from goblin._compat import print_
from goblin.models import Vertex
from goblin.exceptions import ValidationError
from goblin.properties import geoshapes


class CirclePropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = Circle
    good_cases = (geoshapes.Circle((-115.81, 37.24, 10)), (11.81, -37.24, 10),
                  '{"type": "Circle", "coordinates": (-115.81, 37.24, 10)}')
    bad_cases = (11, ("11.81", "-37.24", "50"))

    def test_to_database_method(self):
        d = self.klass()
        self.assertIsNone(d.to_database(None))
        self.assertIsInstance(d.to_database(geoshapes.Circle((-115.81, 37.24, 50))), tuple)

    def test_input_output_equality(self):
        # This is weird due to Titan
        # Values are submitted as (lat, lng), returned as (lng, lat)
        # Also, while Titan doesn't accept geojson
        # it returns it...
        p = geoshapes.Circle([-115.81, 37.24, 50])
        prop = self.klass()
        result = prop.to_python(prop.validate(prop.to_database(p)))
        print_("Input: %s, Output: %s" % (p, result))
        self.assertEqual(
            p['coordinates'],
            [result['coordinates'][1], result['coordinates'][0],
             result['coordinates'][2]])


class CircleTestVertex(Vertex):
    element_type = 'test_circle_vertex'
    test_val = Circle()


CHOICES = (
    (geoshapes.Circle((115.81, 37.24, 100)), 'A'),
    (geoshapes.Circle((11.81, 56.24, 50)), 'B')
)


class CircleTestChoicesVertex(Vertex):
    element_type = 'test_circle_choices_vertex'

    test_val = Circle(choices=CHOICES)


class CircleVertexTestCase(GraphPropertyBaseClassTestCase):

    @gen_test
    def test_circle_io(self):
        print_("creating vertex")
        key = CircleTestVertex.get_property_by_name('test_val')
        yield create_key(key, 'Geoshape')
        circle = geoshapes.Circle((115.81, 37.24, 10))
        p1 = yield CircleTestVertex.create(test_val=circle)
        print_("getting vertex from vertex: %s" % p1)
        p2 = yield CircleTestVertex.get(p1._id)
        print_("got vertex: %s\n" % p2)
        self.assertEqual(p2.test_val['coordinates'], p1.test_val['coordinates'])
        self.assertEqual(p2.test_val['type'], p1.test_val['type'])
        print_("deleting vertex")
        yield p2.delete()


class TestPointVertexChoicesTestCase(BaseGoblinTestCase):

    @gen_test
    def test_good_choices_key_io(self):
        print_("creating vertex")
        key = CircleTestChoicesVertex.get_property_by_name('test_val')
        yield create_key(key, 'Geoshape')
        dt = yield CircleTestChoicesVertex.create(
            test_val=geoshapes.Circle((115.81, 37.24, 100)))
        print_("validating input")
        self.assertEqual(
            dt.test_val['coordinates'],
            geoshapes.Circle((115.81, 37.24, 100))['coordinates'])
        print_("deleting vertex")
        yield dt.delete()

    @gen_test
    def test_good_choices_value_io(self):
        print_("creating vertex")
        key = CircleTestChoicesVertex.get_property_by_name('test_val')
        yield create_key(key, 'Geoshape')
        dt = yield CircleTestChoicesVertex.create(test_val='B')
        print_("validating input")
        circle = geoshapes.Circle((11.81, 56.24, 50))
        self.assertEqual(
            dt.test_val['coordinates'], circle['coordinates'])
        print_("deleting vertex")
        yield dt.delete()

    @gen_test
    def test_bad_choices_io(self):
        key = CircleTestChoicesVertex.get_property_by_name('test_val')
        yield create_key(key, 'Geoshape')

        with self.assertRaises(ValidationError):
            print_("creating vertex")
            dt = yield CircleTestChoicesVertex.create(
                test_val=geoshapes.Circle((100.01, 37.24, 80)))
