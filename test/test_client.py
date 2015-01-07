from datetime import date

from contentful.cda import const
from contentful.cda.client import Client, Config
from contentful.cda.errors import ApiError
from contentful.cda.resources import Entry, Asset, ContentType, ResourceLink, Space
from test import BaseTestCase
from test.lib import utils
from test.lib.utils import Cat, DemoConfig


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

        self.assertIsInstance(result.best_friend, ResourceLink)
        self.assertEqual('nyancat', result.best_friend.resource_id)
        self.assertEqual('Entry', result.best_friend.link_type)

    def test_mapped_items(self):
        result = utils.fetch_array_and_assert(self, Entry, 'mapped_items', const.PATH_ENTRIES, query={'limit': '2'})

        self.assertEqual(2, len(result.items))
        self.assertEqual(1, len(result.items_mapped['Asset']))
        self.assertTrue(isinstance(result.items_mapped['Asset']['1x0xpXu4pSGS4OukSyWGUK'], Asset))
        self.assertEqual(2, len(result.items_mapped['Entry']))

        for item in result:
            self.assertTrue(result.items_mapped['Entry'][item.sys['id']] is item)
            
    def test_resolve_resource_link(self):
        cli = Client(DemoConfig([Cat]))
        result = utils.fetch_first_and_assert(self, Cat, 'resolve_resource_link', const.PATH_ENTRIES, cli)

        best_friend = result.best_friend
        self.assertIsInstance(best_friend, ResourceLink)
        self.assertIsInstance(self.client.resolve_resource_link(best_friend), Entry)

    def test_resolve_dict_link(self):
        dct = {'sys': {'linkType': 'Entry', 'type': 'Link', 'id': 'nyancat'}}
        self.assertIsInstance(self.client.resolve_dict_link(dct), Entry)

    def test_resolve_array_links(self):
        cli = Client(DemoConfig([Cat]))
        result = utils.fetch_array_and_assert(self, Entry, 'resolve_array_links', const.PATH_ENTRIES, cli)
        cli.resolve_array_links(result)

        self.assertIsInstance(result.items_mapped['Entry']['6KntaYXaHSyIw8M6eo26OK'].fields['image'], Asset)
        happy_cat = result.items_mapped['Entry']['happycat']
        self.assertIsInstance(happy_cat.best_friend, Cat)
        self.assertIsInstance(happy_cat.fields['bestFriend'], Cat)
        self.assertIsInstance(happy_cat._cf_cda['bestFriend'], Cat)
        nyan_cat = result.items_mapped['Entry']['nyancat']
        self.assertIsInstance(nyan_cat.best_friend, Cat)
        self.assertIs(happy_cat, nyan_cat.best_friend)
        self.assertIs(nyan_cat, happy_cat.best_friend)
        jake = result.items_mapped['Entry']['jake']
        self.assertIsInstance(jake.fields['image'], Asset)

    def test_space(self):
        space = self.client.fetch_space()
        self.assertIsInstance(space, Space)
        self.assertEqual('Contentful Example API', space.name)
        self.assertIsNotNone(space.sys)

    def test_raises_apierror(self):
        cli = Client(Config('', ''))
        self.assertRaises(ApiError, cli.fetch_space)