from contentful.cda import utils
from contentful.cda.resources import Asset, ContentType, Entry, Space
from test import BaseTestCase


class UtilsTestCase(BaseTestCase):
    def test_class_for_type(self):
        self.assertIs(utils.class_for_type('Asset'), Asset)
        self.assertIs(utils.class_for_type('ContentType'), ContentType)
        self.assertIs(utils.class_for_type('Entry'), Entry)
        self.assertIs(utils.class_for_type('Space'), Space)
