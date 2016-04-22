from __future__ import unicode_literals
from goblin._compat import print_
from six import string_types
from nose.plugins.attrib import attr
from nose.tools import nottest


from tornado import gen
from tornado.ioloop import IOLoop
from tornado.testing import gen_test

from .base import BaseGoblinTestCase
from goblin import connection
from goblin.models import Vertex, Edge
from goblin.properties import String
from goblin.spec import (get_existing_indices, make_property_key,
                         get_property_key, change_property_key_name)


class TestIndexSpecVertex(Vertex):
    element_type = 'test_index_spec_vertex_model'

    name = String(default='test_vertex', index=True, index_ext='es')


class TestIndexSpecEdge(Edge):
    label = 'test_index_spec_edge_model'

    name = String(default='test_edge', index=True, index_ext='es')


@attr('unit', 'connection')
class TestSpecSystem(BaseGoblinTestCase):
    """ Test specification system """

    # def test_loaded(self):
    #     spec = connection.generate_spec()
    #     self.assertIsInstance(spec, (list, tuple))
    #     self.assertGreater(len(spec), 0)
    #     for s in spec:
    #         print_(s)
    #         self.assertIsInstance(s, dict)
    #         self.assertDictContainsKeyWithValueType(s, 'model', string_types)
    #         self.assertDictContainsKeyWithValueType(
    #             s, 'element_type', string_types)
    #         self.assertDictContainsKeyWithValueType(
    #             s, 'makeType', string_types)
    #         self.assertDictContainsKeyWithValueType(s, 'properties', dict)
    #         for pk, pv in s['properties'].items():
    #             self.assertDictContainsKeyWithValueType(
    #                 pv, 'data_type', string_types)
    #             self.assertDictContainsKeyWithValueType(
    #                 pv, 'index_ext', string_types)
    #             self.assertDictContainsKeyWithValueType(
    #                 pv, 'uniqueness', string_types)
    #             self.assertDictContainsKeyWithValueType(
    #                 pv, 'compiled', dict)
    #             self.assertDictContainsKeyWithValueType(
    #                 pv['compiled'], 'script', string_types)
    #             self.assertDictContainsKeyWithValueType(
    #                 pv['compiled'], 'params', dict)
    #             self.assertDictContainsKeyWithValueType(
    #                 pv['compiled'], 'transaction', bool)
    #
    # @gen_test
    # def test_gather_existing_indices(self):
    #     """ Make sure existing vertex and edge types can be gathered """
    #     v_idx, e_idx = get_existing_indices()
    #     v_idx = (yield (yield v_idx).read()).data
    #     e_idx = (yield (yield e_idx).read()).data
    #     self.assertEqual(len(v_idx), 0)
    #     self.assertEqual(len(e_idx), 0)
    #
    #     # create vertex and edge index
    #     yield connection.execute_query('mgmt = graph.openManagement(); mgmt.makeVertexLabel(name).make(); mgmt.commit()',
    #                              params={'name': 'testvertexindex'})
    #     yield connection.execute_query('mgmt = graph.openManagement(); mgmt.makeEdgeLabel(name).make(); mgmt.commit()',
    #                              params={'name': 'testedgeindex'})
    #     v_idx, e_idx = get_existing_indices()
    #     v_idx = (yield (yield v_idx).read()).data
    #     e_idx = (yield (yield e_idx).read()).data
    #     self.assertEqual(len(v_idx), 1)
    #     self.assertEqual(len(e_idx), 1)

    @gen_test
    def test_make_get_change_property_key(self):
        resp = yield make_property_key('test111', 'String', 'SINGLE')
        self.assertIsNone(resp.data[0])
        resp = yield get_property_key('test111')
        self.assertIsNotNone(resp.data[0])
        resp = yield change_property_key_name('test111', 'test112')
        self.assertIsNone(resp.data[0])
        resp = yield get_property_key('test111')
        self.assertIsNone(resp.data[0])

    @gen_test
    def test_get_property_key_doesnt_exist(self):
        resp = yield get_property_key('test1000')
        self.assertIsNone(resp.data[0])
