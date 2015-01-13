"""resources module.

Classes provided include:

- :class:`Resource` - Base CDA resource.

- :class:`Array` - Collection of multiple :class:`.Resource` instances.

- :class:`Asset` - CDA Asset.

- :class:`ContentType` - CDA Content Type.

- :class:`Entry` - CDA Entry.

- :class:`Space` - CDA Space.

- :class:`ResourceType` - Enum of CDA resource types.
"""

from enum import Enum
from six import with_metaclass
from .fields import FieldOwner, MultipleAssets, MultipleEntries


class Resource(object):
    """Base CDA resource class."""
    def __init__(self, sys=None):
        """Resource constructor.

        :param sys: (dict) resource system attributes.
        :return: :class:`.Resource` instance.
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
    """Collection of multiple :class:`.Resource` instances.

    **Attributes**:

    - limit (int): `limit` parameter.
    - skip (int): `skip` parameter.
    - total (int): Total number of resources returned from the API.
    - items (list): Resources contained within the response.
    - items_mapped (dict): All contained resources mapped by Assets/Entries using the resource ID.
    """
    def __init__(self, sys=None):
        """Array constructor.

        :param sys: (dict) resource system attributes.
        :return: :class:`.Array` instance.
        """
        super(Array, self).__init__(sys)
        self.limit = None
        self.skip = None
        self.total = None
        self.items = []
        self.items_mapped = {}

    def __iter__(self):
        # Proxy to the `items` attribute
        return iter(self.items)

    def __getitem__(self, index):
        # Proxy to the `items` attribute
        return self.items[index]

    def _resolve_resource_link(self, link):
        return self.items_mapped[link.link_type].get(link.resource_id)

    def resolve_links(self):
        """Attempt to resolve all internal links (locally).

         In case the linked resources are found either as members of the array or within
         the `includes` element, those will be replaced and reference the actual resources.
         No network calls will be performed.
        """
        for resource in self.items_mapped['Entry'].values():
            for dct in [getattr(resource, '_cf_cda', {}), resource.fields]:
                for k, v in dct.items():
                    if isinstance(v, ResourceLink):
                        resolved = self._resolve_resource_link(v)
                        if resolved is not None:
                            dct[k] = resolved
                    elif isinstance(v, (MultipleAssets, MultipleEntries, list)):
                        for idx, ele in enumerate(v):
                            if not isinstance(ele, ResourceLink):
                                break

                            resolved = self._resolve_resource_link(ele)
                            if resolved is not None:
                                v[idx] = resolved


class Asset(Resource):
    """CDA resource of type Asset.

    **Attributes**:

    - fields (dict): Raw field values as returned from the API.
    - url (str): URL.
    - mimeType (str): MIME type.
    """
    def __init__(self, sys=None):
        """Asset constructor.

        :param sys: (dict) resource system attributes.
        :return: :class:`.Asset` instance.
        """
        super(Asset, self).__init__(sys)
        self.fields = {}
        self.url = None
        self.mimeType = None


class ContentType(Resource):
    """CDA resource of type Content Type.

    **Attributes**:

    - display_field (str): Identifier of the field which should be displayed as a title for Entries.
    - name (str): Name of the Content Type.
    - user_description (str): Description of the Content Type.
    - fields (dict): Content Type fields, mapped by field IDs.
    """
    def __init__(self, sys=None):
        """Content Type constructor.

        :param sys: (dict) resource system attributes.
        :return: :class:`.ContentType` instance.
        """
        super(ContentType, self).__init__(sys)
        self.display_field = None
        self.name = None
        self.user_description = None
        self.fields = {}


class Entry(with_metaclass(FieldOwner, Resource)):
    """CDA resource of type Entry.

    **Attributes**:

    - fields (dict): Entry fields.

    It is possible to define custom :class:`.Entry` models using the following syntax::

        class Cat(Entry):
            __content_type__ = 'cat'

            name = Field(Text)
            color = Field(Text)
            lives = Field(Number)
            likes = Field(List)
            birthday = Field(Date)
            best_friend = Field(Link, field_id='bestFriend')

    .. note::

        `field_id` is set explicitly for the `best_friend` field (which otherwise would be
        inferred from the field's, as in the other fields).

    """
    def __init__(self, sys=None):
        """Entry constructor.

        :param sys: dict containing the resource's remote system attributes.
        :return: Entry instance.
        """
        super(Entry, self).__init__(sys)
        self.fields = {}
        self.raw_fields = {}


class Space(Resource):
    """CDA resource of type Space.

    Attributes:
      name (str): Name of the Space.
    """
    def __init__(self, sys=None):
        """Space constructor.

        :param sys: dict containing the resource's remote system attributes.
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


class ResourceLink(object):
    """Represents a link to a CDA resource."""
    def __init__(self, sys):
        """ResourceLink constructor.

        :param sys: dict containing the resource's remote system attributes.
        :return: ResourceLink instance.
        """
        super(ResourceLink, self).__init__()

        self.resource_id = sys['id']
        self.link_type = sys['linkType']