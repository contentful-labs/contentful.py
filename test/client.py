from unittest import TestCase

from contentful.cda.client import Client, Config
from contentful.cda.resources import Entry
from test import BaseTestCase


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

    def test_entry_all(self):
        with self.use_cassette('entry_all') as cass:
            # response
            result = self.client.fetch(Entry).all()
            self.assertTrue(result.total > 0)
            self.assertEqual(result.total, len(result.items))
            self.assertEqual(0, result.skip)
            self.assertEqual(100, result.limit)

            for entry in result.items:
                self.assertTrue(isinstance(entry, Entry))
                self.assertTrue('id' in entry.sys)
                self.assertTrue(len(entry.fields) > 0)

            # request
            request = cass.requests[0]
            self.assertEqual('GET', request.method)
            self.assertEqual('/spaces/cfexampleapi/entries', request.path)
