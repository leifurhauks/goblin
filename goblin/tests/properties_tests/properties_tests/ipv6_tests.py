from __future__ import unicode_literals

import ipaddress
from nose.plugins.attrib import attr

from tornado.testing import gen_test
from .base_tests import GraphPropertyBaseClassTestCase, create_key
from goblin.properties.properties import IPV6
from goblin.models import Vertex
from goblin._compat import print_
from goblin.constants import LIST


class IPV6TestVertex7(Vertex):
    element_type = 'test_ipv6_vertex'

    test_val = IPV6()


@attr('unit', 'property', 'property_ipv6')
class IPV6VertexTestCase(GraphPropertyBaseClassTestCase):

    @gen_test
    def test_ipv6_io(self):
        print_("creating vertex")
        key = IPV6TestVertex7.get_property_by_name('test_val')
        yield create_key(key, 'Long', cardinality=LIST)
        dt = yield IPV6TestVertex7.create(
            test_val=ipaddress.IPv6Address('1:2:3:4:5:6:7:8'))
        print_("getting vertex from vertex: %s" % dt)
        dt2 = yield IPV6TestVertex7.get(dt._id)
        print_("got vertex: %s\n" % dt2)
        self.assertEqual(dt2.test_val, dt.test_val)
        print_("deleting vertex")
        yield dt2.delete()

        dt = yield IPV6TestVertex7.create(test_val='1::7:8')
        print_("\ncreated vertex: %s" % dt)
        dt2 = yield IPV6TestVertex7.get(dt._id)
        print_("Got vertex: %s" % dt2)
        self.assertEqual(str(dt2.test_val), '1::7:8')
        print_("deleting vertex")
        yield dt2.delete()
