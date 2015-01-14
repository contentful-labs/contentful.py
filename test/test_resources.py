from contentful.cda.resources import Asset, ContentType, Entry, Space
from test import BaseTestCase


class ResourcesTestCase(BaseTestCase):
    def test_fails_entry_no_contenttype(self):
        exception = None
        try:
            class BadEntry(Entry):
                pass
        except AttributeError as e:
            exception = e

        self.assertIsNotNone(exception)
        self.assertEqual('Class BadEntry does not have a __content_type__ specified.', str(exception))

    def test_repr(self):
        for clz in [Asset, ContentType, Entry, Space]:
            self.assertEqual(clz({'id': 'id'}).__repr__(), '<{0}(sys.id=id)>'.format(clz.__name__))
            self.assertEqual(clz().__repr__(), '<{0}>'.format(clz.__name__))
