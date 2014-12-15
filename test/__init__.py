from unittest import TestCase
import vcr as vcr_base

vcr = vcr_base.VCR(match_on=('method', 'scheme', 'host', 'port', 'path', 'query', 'headers'))


class BaseTestCase(TestCase):
    def use_cassette(self, name):
        return vcr.use_cassette('fixtures/vcr_cassettes/{0}.yaml'.format(name))