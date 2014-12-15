from unittest import TestCase

from contentful.cda.client import Client, Config
from contentful.cda.resources import Entry, Asset, ContentType
from test import BaseTestCase
from test import utils


class ClientConfigTestCase(TestCase):
    def test_fails_empty_config(self):
        self.assertRaisesRegexp(Exception, '^Config parameter must not be empty\\.$', Client, None)

    def test_fails_empty_space_id(self):
        config = Config(None, 'token')
        self.assertRaisesRegexp(Exception, '^Configuration for "space_id" must not be empty\\.$', Client, config)

    def test_fails_empty_access_token(self):
        config = Config('space_id', None)
        self.assertRaisesRegexp(Exception, '^Configuration for "access_token" must not be empty\\.$', Client, config)

    def test_fails_wrong_custom_entry_class(self):
        class BadClass(object):
            pass

        config = Config('space_id', 'token', [BadClass])
        self.assertRaisesRegexp(Exception, '^Provided class \\\"BadClass\\\" must be a subclass of Entry\\.$', Client,
                                config)

    def test_fails_entry_class_as_custom(self):
        config = Config('space_id', 'token', [Entry])
        self.assertRaisesRegexp(Exception, '^Cannot register \\\"Entry\\\" as a custom entry class\\.$', Client,
                                config)


class ClientTestCase(BaseTestCase):
    def setUp(self):
        super(ClientTestCase, self).setUp()
        self.client = Client(Config('cfexampleapi', 'b4c0n73n7fu1'))

    def test_asset_all(self):
        utils.fetch_array_and_assert(self, Asset, 'asset_all', 'assets')

    def test_asset_first(self):
        utils.fetch_first_and_assert(self, Asset, 'asset_first', 'assets')

    def test_content_type_all(self):
        utils.fetch_array_and_assert(self, ContentType, 'content_type_all', 'content_types')

    def test_content_type_first(self):
        utils.fetch_first_and_assert(self, ContentType, 'content_type_first', 'content_types')

    def test_entry_all(self):
        utils.fetch_array_and_assert(self, Entry, 'entry_all', 'entries')

    def test_entry_first(self):
        utils.fetch_first_and_assert(self, Entry, 'entry_first', 'entries')