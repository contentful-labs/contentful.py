from contentful.cda.client import Config, Client
from contentful.cda.fields import Field, Text, Number, List, Date, Link
from contentful.cda.resources import Asset, ContentType, Entry

DEMO_SPACE_ID = 'cfexampleapi'
DEMO_ACCESS_TOKEN = 'b4c0n73n7fu1'

SDK_SPACE_ID = 'bada85bjrczm'
SDK_ACCESS_TOKEN = '5476537f4690baefad813b3b0f2e151693d57b1ac150d45b89df310ec097812b'


class DemoClient(Client):
    def __init__(self, custom_entries=None, secure=True, endpoint=None, resolve_links=True):
        super(DemoClient, self).__init__(DEMO_SPACE_ID, DEMO_ACCESS_TOKEN, custom_entries, secure, endpoint,
                                         resolve_links)


class SDKClient(Client):
    def __init__(self, custom_entries=None, secure=True, endpoint=None, resolve_links=True):
        super(SDKClient, self).__init__(SDK_SPACE_ID, SDK_ACCESS_TOKEN, custom_entries, secure, endpoint,
                                        resolve_links)


def assert_resource(test_case, resource, resource_type):
    test_case.assertIsInstance(resource, resource_type)
    test_case.assertTrue('id' in resource.sys)

    if resource_type is Asset:
        assert_asset(test_case, resource)
    elif resource_type is ContentType:
        assert_content_type(test_case, resource)


def assert_asset(test_case, asset):
    test_case.assertTrue(asset.url is not None)
    test_case.assertTrue(asset.mimeType is not None)
    test_case.assertTrue(asset.mimeType.startswith('image/'))


def assert_content_type(test_case, content_type):
    test_case.assertIsNotNone(content_type.name)
    test_case.assertIsNotNone(content_type.display_field)
    test_case.assertTrue(len(content_type.fields) > 0)


def fetch_array_and_assert(test_case, resource_type, cassette_name, last_path_segment, client=None, query=None):
    if client is None:
        client = test_case.client

    with test_case.use_cassette(cassette_name) as cass:
        # response
        req = client.fetch(resource_type)
        if query is not None:
            req.where(query)

        result = req.all()
        for resource in result:
            assert_resource(test_case, resource, resource_type)

        # request
        request = cass.requests[0]
        test_case.assertEqual('GET', request.method)
        test_case.assertEqual('/spaces/cfexampleapi/{0}'.format(last_path_segment), request.path)

    return result


def fetch_first_and_assert(test_case, resource_type, cassette_name, last_path_segment, client=None):
    if client is None:
        client = test_case.client

    with test_case.use_cassette(cassette_name) as cass:
        # response
        result = client.fetch(resource_type).first()
        assert_resource(test_case, result, resource_type)

        # request
        request = cass.requests[0]
        test_case.assertEqual('GET', request.method)
        test_case.assertEqual('/spaces/cfexampleapi/{0}'.format(last_path_segment), request.path)

        limit = None
        for param in request.query:
            if param[0] == 'limit':
                limit = param[1]

        test_case.assertIsNotNone(limit)
        test_case.assertEqual('1', limit)

    return result


class Cat(Entry):
    __content_type__ = 'cat'

    name = Field(Text)
    color = Field(Text)
    lives = Field(Number)
    likes = Field(List)
    birthday = Field(Date)
    best_friend = Field(Link, field_id='bestFriend')