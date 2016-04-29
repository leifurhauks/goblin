from __future__ import unicode_literals
import datetime
from pytz import utc
from decimal import Decimal as D
from nose.plugins.attrib import attr

from goblin.properties import *
from goblin.tests.base import BaseGoblinTestCase


@attr('unit', 'value_manager')
class TestChangedProperty(BaseGoblinTestCase):
    """
    Tests that the `changed` property works as intended
    """

    def test_string_update(self):
        """ Tests changes on string types """
        vm = String.value_manager(String(), 'str', strategy=SaveOnChange)
        self.assertFalse(vm.changed)
        vm.value = 'unicode'
        self.assertTrue(vm.changed)

    def test_string_inplace_update(self):
        """ Tests changes on string in place types """
        vm = String.value_manager(String(), 'str', strategy=SaveOnChange)
        self.assertFalse(vm.changed)
        vm.value += 's'
        self.assertTrue(vm.changed)

    def test_integer_update(self):
        """ Tests changes on integer types """
        vm = Integer.value_manager(Integer(), 5, strategy=SaveOnChange)
        self.assertFalse(vm.changed)
        vm.value = 4
        self.assertTrue(vm.changed)

    def test_integer_inplace_update(self):
        """ Tests changes on integer in place types """
        vm = Integer.value_manager(Integer(), 5, strategy=SaveOnChange)
        self.assertFalse(vm.changed)
        vm.value += 1
        self.assertTrue(vm.changed)

    def test_datetime_update(self):
        """ Tests changes on datetime types """
        now = datetime.datetime.now(tz=utc)
        vm = DateTime.value_manager(DateTime(), now, strategy=SaveOnChange)
        self.assertFalse(vm.changed)
        vm.value = now + datetime.timedelta(days=1)
        self.assertTrue(vm.changed)

    def test_decimal_update(self):
        """ Tests changes on decimal types """
        vm = Decimal.value_manager(Decimal(), D('5.00'), strategy=SaveOnChange)
        self.assertFalse(vm.changed)
        vm.value = D('4.00')
        self.assertTrue(vm.changed)

    def test_decimal_inplace_update(self):
        """ Tests changes on decimal in place types """
        vm = Decimal.value_manager(Decimal(), D('5.00'), strategy=SaveOnChange)
        self.assertFalse(vm.changed)
        vm.value += D('1.00')
        self.assertTrue(vm.changed)
