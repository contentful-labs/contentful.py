from contentful.cda.fields import Field, Text, Number, List, Date, Link
from contentful.cda.resources import Asset, ContentType, Entry


def assert_resource(test_case, resource, resource_type):
    test_case.assertIsNotNone(resource)
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


def fetch_array_and_assert(test_case, resource_type, cassette_name, last_path_segment, client=None):
    if client is None:
        client = test_case.client

    with test_case.use_cassette(cassette_name) as cass:
        # response
        result = client.fetch(resource_type).all()
        test_case.assertTrue(result.total > 0)
        test_case.assertEqual(result.total, len(result.items))
        test_case.assertEqual(0, result.skip)
        test_case.assertEqual(100, result.limit)

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