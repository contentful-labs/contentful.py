import os
from unittest import TestCase
import vcr as vcr_base
from test.lib import utils


if hasattr(TestCase, 'assertRaisesRegex'):
    TestCase = TestCase
else:
    class TestCase(TestCase):
        assertRaisesRegex = TestCase.assertRaisesRegexp

def before_record_cb(request):
    space_id = request.path.split('/')[2]
    token = utils.DEMO_ACCESS_TOKEN if space_id == utils.DEMO_SPACE_ID else utils.SDK_ACCESS_TOKEN
    assert request.headers.get('Authorization') == 'Bearer {0}'.format(token)
    return request

vcr = vcr_base.VCR(cassette_library_dir=os.path.dirname(__file__), before_record=before_record_cb)


class BaseTestCase(TestCase):
    def use_cassette(self, name):
        return vcr.use_cassette('fixtures/vcr_cassettes/{0}.yaml'.format(name))
