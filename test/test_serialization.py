from datetime import date
from contentful.cda.fields import Boolean, Date, Number, Object, Text, List
from contentful.cda.fields import Field
from contentful.cda.serialization import ResourceFactory
from test import BaseTestCase


class ResourceFactoryTests(BaseTestCase):
    def test_convert_boolean(self):
        field = Field(Boolean)
        self.assertIs(ResourceFactory.convert_value('', field), False)
        self.assertIs(ResourceFactory.convert_value(False, field), False)
        self.assertIs(ResourceFactory.convert_value(0, field), False)
        self.assertIs(ResourceFactory.convert_value('true', field), True)
        self.assertIs(ResourceFactory.convert_value(True, field), True)
        self.assertIs(ResourceFactory.convert_value(1, field), True)

    def test_convert_date(self):
        dt = ResourceFactory.convert_value('2013-11-18T09:13:37.808Z', Field(Date))
        self.assertIsInstance(dt, date)
        self.assertEqual(2013, dt.year)
        self.assertEqual(11, dt.month)
        self.assertEqual(18, dt.day)
        self.assertEqual(9, dt.hour)
        self.assertEqual(13, dt.minute)
        self.assertEqual(37, dt.second)
        self.assertEqual(808000, dt.microsecond)

    def test_convert_date_num(self):
        dt = ResourceFactory.convert_value(20130101, Field(Date))
        self.assertIsInstance(dt, date)
        self.assertEqual(2013, dt.year)
        self.assertEqual(1, dt.month)
        self.assertEqual(1, dt.day)

    def test_convert_number(self):
        value = int(1234567890)
        num = ResourceFactory.convert_value(str(value), Field(Number))
        self.assertIsInstance(num, int)
        self.assertEqual(value, num)

    def test_convert_object(self):
        dct = ResourceFactory.convert_value("{'ct' : 'di', 'nary' : 'io'}", Field(Object))
        self.assertIsInstance(dct, dict)
        self.assertEqual('di', dct['ct'])
        self.assertEqual('io', dct['nary'])

    def test_convert_text(self):
        value = 31337
        txt = ResourceFactory.convert_value(31337, Field(Text))
        self.assertIsInstance(txt, str)
        self.assertEqual(str(value), txt)

    def test_convert_list(self):
        item = 'item'
        lst = ResourceFactory.convert_value(item, Field(List))
        self.assertIsInstance(lst, list)
        self.assertEqual(1, len(lst))
        self.assertEqual(item, lst[0])