from enum import Enum
import itertools

from fields import FieldOwner


# Resources
class Resource(object):
    def __init__(self, sys=None):
        super(Resource, self).__init__()
        self.sys = sys or {}

    def __repr__(self):
        suffix = None

        if 'id' in self.sys:
            suffix = '(sys.id={0})'.format(self.sys['id'])

        return '<{0}{1}>'.format(self.__class__.__name__, '' if suffix is None else suffix)


class Array(Resource):
    def __init__(self, sys=None):
        super(Array, self).__init__(sys)
        self.limit = None
        self.skip = None
        self.total = None
        self.items = []

    def __iter__(self):
        return iter(self.items)

    def __getitem__(self, index):
        return self.items[index]


class Asset(Resource):
    def __init__(self, sys=None):
        super(Asset, self).__init__(sys)
        self.fields = {}
        self.url = None
        self.mimeType = None


class ContentType(Resource):
    def __init__(self, sys=None):
        super(ContentType, self).__init__(sys)
        self.display_field = None
        self.name = None
        self.user_description = None
        self.fields = {}


class Entry(Resource):
    __metaclass__ = FieldOwner

    def __init__(self, sys=None):
        super(Entry, self).__init__(sys)
        self.fields = {}


class Space(Resource):
    def __init__(self, sys=None):
        super(Space, self).__init__(sys)
        self.name = None


class ResourceType(Enum):
    Array = 'Array'
    Asset = 'Asset'
    ContentType = 'ContentType'
    Entry = 'Entry'
    Link = 'Link'
    Space = 'Space'