import os
from unittest import TestCase
import vcr as vcr_base
from test.lib.utils import DemoConfig, SDKSpaceConfig


def before_record_cb(request):
    space_id = request.path.split('/')[2]
    cfg_demo = DemoConfig()
    cfg_sdk = SDKSpaceConfig()

    token = cfg_demo.access_token if space_id == cfg_demo.space_id else cfg_sdk.access_token
    assert request.headers.get('Authorization') == 'Bearer {0}'.format(token)
    return request

vcr = vcr_base.VCR(cassette_library_dir=os.path.dirname(__file__), before_record=before_record_cb)


class BaseTestCase(TestCase):
    def use_cassette(self, name):
        return vcr.use_cassette('fixtures/vcr_cassettes/{0}.yaml'.format(name))