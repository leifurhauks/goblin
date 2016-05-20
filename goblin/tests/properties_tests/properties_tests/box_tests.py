from __future__ import unicode_literals
import unittest

from tornado.testing import gen_test

import geojson

from goblin.tests import BaseGoblinTestCase
from goblin._compat import PY2
from .base_tests import GraphPropertyBaseClassTestCase, create_key
from goblin.properties.properties import Box, GraphProperty
from goblin._compat import print_
from goblin.models import Vertex
from goblin.exceptions import ValidationError


class BoxPropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = Box
    good_cases = (
        geojson.Polygon([(23.72, 37.97), (24.72, 37.97),
                         (24.72, 38.97), (23.72, 38.97)]),
        [(23.72, 37.97), (24.72, 37.97), (24.72, 38.97), (23.72, 38.97)],
        '{"type": "Polygon", "coordinates": [(23.72, 37.97), (24.72, 37.97), (24.72, 38.97), (23.72, 38.97)]}')
    bad_cases = (
        [(23.72, 37.97), (24.72, 37.97), (25.72, 38.97), (23.72, 38.97)],
        [(23.72, 37.97), (23.72, 37.97), (24.72, 38.97), (23.72, 38.97)])

    def test_to_database_method(self):
        d = self.klass()
        self.assertIsNone(d.to_database(None))
        self.assertIsInstance(
            d.to_database(geojson.Polygon([(23.72, 37.97), (24.72, 37.97),
                                           (24.72, 38.97), (23.72, 38.97)])), tuple)


    # def test_input_output_equality(self):
    #     # This is weird due to Titan
    #     # Values are submitted as (lat, lng), returned as (lng, lat)
    #     # Also, while Titan doesn't accept geojson
    #     # it returns it...
    #     # p = geojson.Polygon([(23.72, 37.97), (24.72, 37.97),
    #     #                      (24.72, 38.97), (23.72, 38.97)])
    #     # prop = self.klass()
    #     # result = prop.to_python(prop.to_database(p))
    #     # print_("Input: %s, Output: %s" % (p, result))
    #     # self.assertEqual(
    #     #     p['coordinates'],
    #     #     [result['coordinates'][1], result['coordinates'][0],
    #     #      result['coordinates'][2]])


class BoxTestVertex(Vertex):
    element_type = 'test_box_vertex'
    test_val = Box()


CHOICES = (
    (geojson.Polygon([(23.72, 37.97), (24.72, 37.97),
                      (24.72, 38.97), (23.72, 38.97)]), 'A'),
    (geojson.Polygon([(21.72, 37.97), (24.72, 37.97),
                      (24.72, 39.97), (21.72, 39.97)]), 'B')
)


class BoxTestChoicesVertex(Vertex):
    element_type = 'test_box_choices_vertex'

    test_val = Box(choices=CHOICES)


class BoxVertexTestCase(GraphPropertyBaseClassTestCase):

    @gen_test
    def test_circle_io(self):
        print_("creating vertex")
        key = BoxTestVertex.get_property_by_name('test_val')
        yield create_key(key, 'Geoshape')
        circle = geojson.Polygon([(23.72, 37.97), (24.72, 37.97),
                                  (24.72, 38.97), (23.72, 38.97)])
        p1 = yield BoxTestVertex.create(test_val=circle)
        print_("getting vertex from vertex: %s" % p1)
        p2 = yield BoxTestVertex.get(p1._id)
        print_("got vertex: %s\n" % p2)
        self.assertEqual(p2.test_val['coordinates'], p1.test_val['coordinates'])
        self.assertEqual(p2.test_val['type'], p1.test_val['type'])
        print_("deleting vertex")
        yield p2.delete()


class TestPointVertexChoicesTestCase(BaseGoblinTestCase):

    @gen_test
    def test_good_choices_key_io(self):
        print_("creating vertex")
        key = BoxTestChoicesVertex.get_property_by_name('test_val')
        yield create_key(key, 'Geoshape')
        dt = yield BoxTestChoicesVertex.create(
            test_val=geojson.Polygon([(23.72, 37.97), (24.72, 37.97),
                                      (24.72, 38.97), (23.72, 38.97)]))
        print_("validating input")
        self.assertEqual(
            dt.test_val['coordinates'],
            geojson.Polygon([[23.72, 37.97], [24.72, 37.97],
                             [24.72, 38.97], [23.72, 38.97]])['coordinates'])
        print_("deleting vertex")
        yield dt.delete()

    @gen_test
    def test_good_choices_value_io(self):
        print_("creating vertex")
        key = BoxTestChoicesVertex.get_property_by_name('test_val')
        yield create_key(key, 'Geoshape')
        dt = yield BoxTestChoicesVertex.create(test_val='B')
        print_("validating input")
        box = geojson.Polygon([[21.72, 37.97], [24.72, 37.97],
                               [24.72, 39.97], [21.72, 39.97]])
        self.assertEqual(
            dt.test_val['coordinates'], box['coordinates'])
        print_("deleting vertex")
        yield dt.delete()

    @gen_test
    def test_bad_choices_io(self):
        key = BoxTestChoicesVertex.get_property_by_name('test_val')
        yield create_key(key, 'Geoshape')

        with self.assertRaises(ValidationError):
            print_("creating vertex")
            dt = yield BoxTestChoicesVertex.create(
                test_val=geojson.Polygon([[21.72, 37.97], [25.72, 37.97],
                                          [25.72, 39.97], [21.72, 39.97]]))
