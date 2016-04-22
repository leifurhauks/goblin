from __future__ import unicode_literals
from nose.plugins.attrib import attr
from tornado.testing import gen_test
from goblin.tests import BaseGoblinTestCase
from .base_tests import GraphPropertyBaseClassTestCase, create_key
from goblin import connection
from goblin.properties.properties import Boolean, GraphProperty
from goblin.models import Vertex
from goblin.exceptions import ValidationError
from goblin._compat import print_


@attr('unit', 'property', 'property_boolean')
class BooleanPropertyTestCase(GraphPropertyBaseClassTestCase):
    klass = Boolean
    good_cases = (True, False, None)
    bad_cases = (0, 1.1, 'val', [], (), {})


class BooleanTestVertex(Vertex):
    element_type = 'test_boolean_vertex'

    test_val = Boolean()

CHOICES = (
    (True, True),
    (False, False)
)


class BooleanTestChoicesVertex(Vertex):
    element_type = 'test_boolean_choices_vertex'
    test_val = Boolean(choices=CHOICES)


@attr('unit', 'property', 'property_boolean')
class BooleanVertexTestCase(GraphPropertyBaseClassTestCase):

    @gen_test
    def test_manual_schema(self):
        key = BooleanTestVertex.get_property_by_name('test_val')
        label = BooleanTestVertex.get_label()
        yield create_key(key, 'Boolean')
        stream = yield connection.execute_query(
            "graph.addVertex(label, l0, k0, v0)",
            bindings={'l0': label, 'k0': key, 'v0': True})
        resp = yield stream.read()
        self.assertEqual(
            resp.data[0]['properties'][key][0]['value'], True)

    @gen_test
    def test_violate_manual_schema(self):
        key = BooleanTestVertex.get_property_by_name('test_val')
        label = BooleanTestVertex.get_label()
        yield create_key(key, 'Boolean')
        with self.assertRaises(RuntimeError):
            stream = yield connection.execute_query(
                "graph.addVertex(label, l0, k0, v0)",
                bindings={'l0': label, 'k0': key, 'v0': 21})
            resp = yield stream.read()

    @gen_test
    def test_boolean_io(self):
        key = BooleanTestVertex.get_property_by_name('test_val')
        yield create_key(key, 'Boolean')
        print_("creating vertex")
        dt = yield BooleanTestVertex.create(test_val=True)
        print_("getting vertex from vertex: %s" % dt)
        dt2 = yield BooleanTestVertex.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        yield dt2.delete()

        dt = yield BooleanTestVertex.create(test_val=True)
        print_("\ncreated vertex: %s" % dt)
        dt2 = yield BooleanTestVertex.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(dt2.test_val, True)
        print_("deleting vertex")
        yield dt2.delete()


@attr('unit', 'property', 'property_boolean')
class TestVertexChoicesTestCase(BaseGoblinTestCase):

    @gen_test
    def test_good_choices_value_io(self):
        key = BooleanTestVertex.get_property_by_name('test_val')
        yield create_key(key, 'Boolean')
        print_("creating vertex")
        dt = yield BooleanTestChoicesVertex.create(test_val=True)
        print_("validating input")
        self.assertEqual(dt.test_val, True)
        print_("deleting vertex")
        yield dt.delete()

    @gen_test
    def test_good_choices_key_io(self):
        key = BooleanTestVertex.get_property_by_name('test_val')
        yield create_key(key, 'Boolean')
        print_("creating vertex")
        dt = yield BooleanTestChoicesVertex.create(test_val=False)
        print_("validating input")
        self.assertEqual(dt.test_val, False)
        print_("deleting vertex")
        yield dt.delete()

    @gen_test
    def test_bad_choices_io(self):
        with self.assertRaises(ValidationError):
            print_("creating vertex")
            dt = yield BooleanTestChoicesVertex.create(test_val=None)
            print_("validating input")
            self.assertEqual(dt.test_val, None)
            print_("deleting vertex")
            yield dt.delete()
