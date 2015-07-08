from datetime import date
from mock import patch
from requests import Response

from contentful.cda import const
from contentful.cda.client import Client
from contentful.cda.errors import ApiError, Unauthorized
from contentful.cda.resources import Entry, Asset, ContentType, ResourceLink, Space
from test import BaseTestCase
from test.lib import utils
from test.lib.utils import Cat, DemoClient, SDKClient


class ClientConfigTestCase(BaseTestCase):
    def test_fails_empty_space_id(self):
        self.assertRaisesRegex(Exception, '^Configuration for "space_id" must not be empty\\.$', Client, None, 'token')

    def test_fails_empty_access_token(self):
        self.assertRaisesRegex(Exception, '^Configuration for "access_token" must not be empty\\.$', Client,
                                'space_id', None)

    def test_fails_wrong_custom_entry_class(self):
        class BadClass(object):
            pass
        self.assertRaisesRegex(Exception, '^Provided class \\\"BadClass\\\" must be a subclass of Entry\\.$', Client,
                                'space_id', 'token', [BadClass])

    def test_fails_entry_class_as_custom(self):
        self.assertRaisesRegex(Exception, '^Cannot register \\\"Entry\\\" as a custom entry class\\.$', Client,
                                'space_id', 'token', [Entry])


class ClientTestCase(BaseTestCase):
    def setUp(self):
        super(ClientTestCase, self).setUp()
        self.client = DemoClient()

    def test_fails_fetch_invalid_resource(self):
        self.assertRaisesRegex(Exception, '^Invalid resource type \\\"<(type|class) \\\'int\\\'>\\\".',
                                self.client.fetch, int)

    def test_user_agent(self):
        pattern = '^contentful\\.py/[0-9\\w\\.]+$'
        headers = self.client.dispatcher.get_headers()
        items = [self.client.dispatcher.user_agent, headers['User-Agent']]
        for i in items:
            self.assertRegexpMatches(i, pattern)

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
        cli = DemoClient([Cat])
        result = utils.fetch_array_and_assert(self, Entry, 'entry_custom_class_mixed', const.PATH_ENTRIES, cli)
        for resource in [result[2], result[4], result[5]]:
            self.assertIsInstance(resource, Cat)

    def test_entry_custom_class_explicit_all(self):
        cli = DemoClient([Cat])
        result = utils.fetch_array_and_assert(self, Cat, 'entry_custom_class_explicit_all', const.PATH_ENTRIES, cli)
        for resource in result:
            self.assertIsInstance(resource, Cat)

    def test_entry_custom_class_explicit_first(self):
        cli = DemoClient([Cat])
        result = utils.fetch_first_and_assert(self, Cat, 'entry_custom_class_explicit_first', const.PATH_ENTRIES, cli)
        self.assertIsInstance(result, Cat)

        self.assertEqual('Happy Cat', result.name)
        self.assertEqual('gray', result.color)
        self.assertEqual(1, result.lives)
        self.assertIsInstance(result.likes, list)
        self.assertEqual(1, len(result.likes))
        self.assertEqual('cheezburger', result.likes[0])
        self.assertIsInstance(result.birthday, date)

        self.assertIsInstance(result.best_friend, Cat)
        self.assertEqual('Nyan Cat', result.best_friend.name)
        self.assertIs(result, result.best_friend.best_friend)

    def test_mapped_items(self):
        result = utils.fetch_array_and_assert(self, Entry, 'mapped_items', const.PATH_ENTRIES, query={'limit': '2'})

        self.assertEqual(2, len(result.items))
        self.assertEqual(1, len(result.items_mapped['Asset']))
        self.assertTrue(isinstance(result.items_mapped['Asset']['1x0xpXu4pSGS4OukSyWGUK'], Asset))
        self.assertEqual(2, len(result.items_mapped['Entry']))

        for item in result:
            self.assertTrue(result.items_mapped['Entry'][item.sys['id']] is item)
            
    def test_resolve_resource_link(self):
        cli = DemoClient([Cat])
        with self.use_cassette('resolve_resource_link'):
            result = cli.fetch(Cat).where({'include': '0', 'sys.id': 'nyancat'}).first()
            self.assertIsNotNone(result)
            self.assertIsInstance(result, Cat)
            self.assertIsInstance(result.best_friend, ResourceLink)
            self.assertIsInstance(self.client.resolve_resource_link(result.best_friend), Entry)

    def test_resolve_dict_link(self):
        dct = {'sys': {'linkType': 'Entry', 'type': 'Link', 'id': 'nyancat'}}
        self.assertIsInstance(self.client.resolve_dict_link(dct), Entry)

    def test_resolve_array_links(self):
        cli = DemoClient([Cat])
        result = utils.fetch_array_and_assert(self, Entry, 'resolve_array_links', const.PATH_ENTRIES, cli)
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

    def test_resolve_resource_link_from_array(self):
        cli = DemoClient([Cat])
        result = utils.fetch_array_and_assert(self, Entry, 'resolve_array_links', const.PATH_ENTRIES, cli)

        bad_client = Client('', '')
        link = ResourceLink({'linkType': 'Entry', 'type': 'Link', 'id': 'nyancat'})
        resolved = bad_client.resolve_resource_link(link, result)
        self.assertIsInstance(resolved, Cat)

    def test_resolve_list_of_links(self):
        cli = SDKClient()

        with self.use_cassette('resolve_list_of_links'):
            result = cli.fetch(Entry).where({'sys.id': '399PKHUiJOsMuOGAcAsWmg'}).all()
            self.assertIsInstance(result[0].fields['entries'][0], Entry)

    def test_space(self):
        space = self.client.fetch_space()
        self.assertIsInstance(space, Space)
        self.assertEqual('Contentful Example API', space.name)
        self.assertIsNotNone(space.sys)

    @patch('requests.get')
    def test_raises_mapped_apierror(self, get_mock):
        get_mock.return_value = Response()
        get_mock.return_value.status_code = 401
        self.assertRaises(Unauthorized, self.client.fetch_space)

    @patch('requests.get')
    def test_raises_general_apierror(self, get_mock):
        get_mock.return_value = Response()
        get_mock.return_value.status_code = 504
        self.assertRaises(ApiError, self.client.fetch_space)
