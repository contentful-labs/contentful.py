"""resources module.

Classes provided include:

:class:`Resource` - Base CDA resource class.

:class:`Array` - A collection of zero or more CDA resources.

:class:`Asset` - CDA resource of type Asset.

:class:`ContentType` - CDA resource of type Content Type.

:class:`Entry` - CDA resource of type Entry.

:class:`Space` - CDA resource of type Space.

:class:`ResourceType` - Enum of CDA resource types.
"""

from enum import Enum
from fields import FieldOwner


class Resource(object):
    """Base CDA resource class."""
    def __init__(self, sys=None):
        """Resource constructor.

        :param sys: dict containing the resource's remote system attributes
        :return: Resource instance.
        """
        super(Resource, self).__init__()
        self.sys = sys or {}

    def __repr__(self):
        """Custom representation.

        Examples:
          <Asset(sys.id=xxx)>
          <Entry(sys.id=xxx)>
          <ContentType(sys.id=xxx)>
          <Space(sys.id=xxx)>

        :return: representation string
        """
        suffix = None

        if 'id' in self.sys:
            suffix = '(sys.id={0})'.format(self.sys['id'])

        return '<{0}{1}>'.format(self.__class__.__name__, '' if suffix is None else suffix)


class Array(Resource):
    """A collection of zero or more CDA resources.

    Attributes:
      limit (int): `limit` value as sent to the API.
      skip (int): `skip` value as sent to the API.
      total (int): Total number of resources returned from the API.
      items (list): List of resources contained within the response.
    """
    def __init__(self, sys=None):
        """Array constructor.

        :param sys: dict containing the resource's remote system attributes
        :return: Array instance.
        """
        super(Array, self).__init__(sys)
        self.limit = None
        self.skip = None
        self.total = None
        self.items = []

    def __iter__(self):
        # Proxy to the `items` attribute
        return iter(self.items)

    def __getitem__(self, index):
        # Proxy to the `items` attribute
        return self.items[index]


class Asset(Resource):
    """CDA resource of type Asset.

    Attributes:
      fields (dict): Raw field values as returned from the API.
      url (str): URL associated with the Asset.
      mimeType (str): MIME type of the Asset.
    """
    def __init__(self, sys=None):
        """Asset constructor.

        :param sys: dict containing the resource's remote system attributes
        :return: Asset instance.
        """
        super(Asset, self).__init__(sys)
        self.fields = {}
        self.url = None
        self.mimeType = None


class ContentType(Resource):
    """CDA resource of type Content Type.

    Attributes:
      display_field (str): Identifier of the Field which should be displayed as a title for Entries.
      name (str): Name of the Content Type.
      user_description (str): Description of the Content Type.
      fields (dict): Content Type fields, mapped by field IDs.
    """
    def __init__(self, sys=None):
        """Content Type constructor.

        :param sys: dict containing the resource's remote system attributes
        :return: ContentType instance.
        """
        super(ContentType, self).__init__(sys)
        self.display_field = None
        self.name = None
        self.user_description = None
        self.fields = {}


class Entry(Resource):
    """CDA resource of type Entry.

    Attributes:
      fields (dict): Entry fields.

    It is possible to define custom Entry models using the following syntax::

        class Cat(Entry):
            __content_type__ = 'cat'

            name = Field(Text)
            color = Field(Text)
            lives = Field(Number)
            likes = Field(List)
            birthday = Field(Date)
            best_friend = Field(Link, field_id='bestFriend')
    ::
    """
    __metaclass__ = FieldOwner

    def __init__(self, sys=None):
        """Entry constructor.

        :param sys: dict containing the resource's remote system attributes
        :return: Entry instance.
        """
        super(Entry, self).__init__(sys)
        self.fields = {}


class Space(Resource):
    """CDA resource of type Space.

    Attributes:
      name (str): Name of the Space.
    """
    def __init__(self, sys=None):
        """Space constructor.

        :param sys: dict containing the resource's remote system attributes
        :return: Space instance.
        """
        super(Space, self).__init__(sys)
        self.name = None


class ResourceType(Enum):
    """Enum of CDA resource types."""
    Array = 'Array'
    Asset = 'Asset'
    ContentType = 'ContentType'
    Entry = 'Entry'
    Link = 'Link'
    Space = 'Space'