from unittest import TestCase
import vcr as vcr_base


def before_record_cb(request):
    assert request.headers.get('Authorization') == 'Bearer b4c0n73n7fu1'
    return request


vcr = vcr_base.VCR(before_record=before_record_cb)


class BaseTestCase(TestCase):
    def use_cassette(self, name):
        return vcr.use_cassette('fixtures/vcr_cassettes/{0}.yaml'.format(name))