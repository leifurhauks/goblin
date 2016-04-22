from __future__ import unicode_literals
from tornado import gen
from goblin.tests import BaseGoblinTestCase
from goblin.properties import GraphProperty
from nose.plugins.attrib import attr
from goblin.exceptions import ValidationError
from goblin._compat import print_
from goblin.spec import get_property_key, make_property_key


@gen.coroutine
def create_key(key, data_type):
    resp = yield get_property_key(key)
    if resp.data[0] is None:
        yield make_property_key(key, data_type, 'SINGLE')


@attr('unit', 'property')
class GraphPropertyBaseClassTestCase(BaseGoblinTestCase):
    """ Test Base Strategy Callable Object """
    klass = GraphProperty
    good_cases = ('', 'a', 1, 1.1, None, [], [1], {}, {'a': 1})
    bad_cases = ()

    def test_subclass(self):
        """ Test if Property is a GraphProperty """
        self.assertIsSubclass(self.klass, GraphProperty)

    def test_validation(self):
        for case in self.good_cases:
            print_("testing good case: {}".format(case))
            self.assertNotRaise(self.klass().validate, case)

        for case in self.bad_cases:
            print_("testing bad case: {}".format(case))
            self.assertRaises(ValidationError, self.klass().validate, case)
