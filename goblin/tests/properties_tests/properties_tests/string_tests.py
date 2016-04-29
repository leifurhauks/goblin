from __future__ import unicode_literals
from nose.plugins.attrib import attr
from tornado.testing import gen_test
from goblin import connection
from goblin.tests import BaseGoblinTestCase
from .base_tests import GraphPropertyBaseClassTestCase, create_key
from goblin.properties.properties import String, GraphProperty
from goblin.models import Vertex
from goblin.exceptions import ValidationError
from goblin._compat import print_


@attr('unit', 'property', 'property_string')
class StringPropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = String
    good_cases = ('test', None)
    bad_cases = (0, 1.1, [], (), {})

    def test_max_min_length_validation_error(self):
        s = self.klass(max_length=5, min_length=2)
        with self.assertRaises(ValidationError):
            s.validate('123456')
        with self.assertRaises(ValidationError):
            s.validate('1')


class StringTestVertex(Vertex):
    element_type = 'test_string_vertex'

    test_val = String()

CHOICES = (
    ('A', 1),
    ('B', 2)
)


class StringTestChoicesVertex(Vertex):
    element_type = 'test_string_choices_vertex'

    test_val = String(choices=CHOICES)


@attr('unit', 'property', 'property_string')
class StringVertexTestCase(GraphPropertyBaseClassTestCase):

    @gen_test
    def test_manual_schema(self):
        key = StringTestVertex.get_property_by_name('test_val')
        label = StringTestVertex.get_label()
        yield create_key(key, 'String')
        stream = yield connection.execute_query(
            "graph.addVertex(label, l0, k0, v0)",
            bindings={'l0': label, 'k0': key, 'v0': 'hello'})
        resp = yield stream.read()
        self.assertEqual(
            resp.data[0]['properties'][key][0]['value'], 'hello')

    # titan converts pretty much anythin to string

    @gen_test
    def test_string_io(self):
        key = StringTestVertex.get_property_by_name('test_val')
        yield create_key(key, 'String')
        print_("creating vertex")
        dt = yield StringTestVertex.create(test_val='test')
        print_("getting vertex from vertex: %s" % dt)
        dt2 = yield StringTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        yield dt2.delete()

        dt = yield StringTestVertex.create(test_val='tset')
        print_("\ncreated vertex: %s" % dt)
        dt2 = yield StringTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, 'tset')
        print_("deleting vertex")
        yield dt2.delete()


@attr('unit', 'property', 'property_string')
class TestVertexChoicesTestCase(BaseGoblinTestCase):

    @gen_test
    def test_good_choices_value_io(self):
        key = StringTestChoicesVertex.get_property_by_name('test_val')
        yield create_key(key, 'String')
        print_("creating vertex")
        dt = yield StringTestChoicesVertex.create(test_val=1)
        print_("validating input")
        self.assertEqual(dt.test_val, 'A')
        print_("deleting vertex")
        yield dt.delete()

    @gen_test
    def test_good_choices_key_io(self):
        key = StringTestChoicesVertex.get_property_by_name('test_val')
        yield create_key(key, 'String')
        print_("creating vertex")
        dt = yield StringTestChoicesVertex.create(test_val='B')
        print_("validating input")
        self.assertEqual(dt.test_val, 'B')
        print_("deleting vertex")
        yield dt.delete()

    @gen_test
    def test_bad_choices_io(self):
        with self.assertRaises(ValidationError):
            print_("creating vertex")
            dt = yield StringTestChoicesVertex.create(test_val=3)
            print_("validating input")
            self.assertEqual(dt.test_val, 'C')
            print_("deleting vertex")
            yield dt.delete()
