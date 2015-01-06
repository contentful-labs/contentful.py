from datetime import date
from contentful.cda import const
from contentful.cda.client import Client, Config
from contentful.cda.resources import Entry, Asset, ContentType
from test import BaseTestCase
from test import utils
from test.utils import Cat, DemoConfig


class ClientConfigTestCase(BaseTestCase):
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
        self.client = Client(DemoConfig())

    def test_asset_all(self):
        utils.fetch_array_and_assert(self, Asset, 'asset_all', const.PATH_ASSETS)

    def test_asset_first(self):
        utils.fetch_first_and_assert(self, Asset, 'asset_first', const.PATH_ASSETS)

    def test_content_type_all(self):
        utils.fetch_array_and_assert(self, ContentType, 'content_type_all', const.PATH_CONTENT_TYPES)

    def test_content_type_first(self):
        utils.fetch_first_and_assert(self, ContentType, 'content_type_first', const.PATH_CONTENT_TYPES)

    def test_entry_all(self):
        utils.fetch_array_and_assert(self, Entry, 'entry_all', const.PATH_ENTRIES)

    def test_entry_first(self):
        utils.fetch_first_and_assert(self, Entry, 'entry_first', const.PATH_ENTRIES)

    def test_entry_custom_class_mixed(self):
        cli = Client(DemoConfig([Cat]))
        result = utils.fetch_array_and_assert(self, Entry, 'entry_custom_class_mixed', const.PATH_ENTRIES, cli)
        for resource in [result[2], result[4], result[5]]:
            self.assertIsInstance(resource, Cat)

    def test_entry_custom_class_explicit_all(self):
        cli = Client(DemoConfig([Cat]))
        result = utils.fetch_array_and_assert(self, Cat, 'entry_custom_class_explicit_all', const.PATH_ENTRIES, cli)
        for resource in result:
            self.assertIsInstance(resource, Cat)

    def test_entry_custom_class_explicit_first(self):
        cli = Client(DemoConfig([Cat]))
        result = utils.fetch_first_and_assert(self, Cat, 'entry_custom_class_explicit_first', const.PATH_ENTRIES, cli)
        self.assertIsInstance(result, Cat)

        self.assertEqual('Happy Cat', result.name)
        self.assertEqual('gray', result.color)
        self.assertEqual(1, result.lives)
        self.assertIsInstance(result.likes, list)
        self.assertEqual(1, len(result.likes))
        self.assertEqual('cheezburger', result.likes[0])
        self.assertIsInstance(result.birthday, date)

        self.assertIsNotNone(result.best_friend)
        self.assertIsInstance(result.best_friend, dict)
        self.assertEqual('Link', result.best_friend['sys']['type'])
        self.assertEqual('Entry', result.best_friend['sys']['linkType'])
        self.assertEqual('nyancat', result.best_friend['sys']['id'])