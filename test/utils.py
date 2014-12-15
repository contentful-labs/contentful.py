from contentful.cda.resources import Asset, ContentType


def assert_resource(test_case, resource, resource_type):
    test_case.assertIsNotNone(resource)
    test_case.assertTrue(isinstance(resource, resource_type))
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


def fetch_array_and_assert(test_case, resource_type, cassette_name, last_path_segment):
    with test_case.use_cassette(cassette_name) as cass:
        # response
        result = test_case.client.fetch(resource_type).all()
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


def fetch_first_and_assert(test_case, resource_type, cassette_name, last_path_segment):
        with test_case.use_cassette(cassette_name) as cass:
            # response
            result = test_case.client.fetch(resource_type).first()
            assert_resource(test_case, result, resource_type)

            # request
            request = cass.requests[0]
            test_case.assertEqual('GET', request.method)
            test_case.assertEqual('/spaces/cfexampleapi/{0}'.format(last_path_segment), request.path)

            param = request.query[0]
            test_case.assertEqual('limit', param[0])
            test_case.assertEqual('1', param[1])
