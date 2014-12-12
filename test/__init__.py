from unittest import TestCase
import vcr


class BaseTestCase(TestCase):
    def use_cassette(self, name):
        return vcr.use_cassette('fixtures/vcr_cassettes/{0}.yaml'.format(name))