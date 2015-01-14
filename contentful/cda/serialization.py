"""serialization module.

Classes provided include:

:class:`ResourceFactory` - Factory for generating :class:`.resources.Resource` subclasses out of JSON data.
"""
from .fields import Boolean, Date, Number, Object, Symbol, Text, List, MultipleAssets, MultipleEntries
from .resources import ResourceType, Array, Entry, Asset, Space, ContentType, ResourceLink
from dateutil import parser
import ast
import copy


class ResourceFactory(object):
    """Factory for generating :class:`.resources.Resource` subclasses out of JSON data.

    Attributes:
      entries_mapping (dict): Mapping of Content Type IDs to custom Entry subclasses.
    """
    def __init__(self, custom_entries):
        """ResourceFactory constructor.

        :param custom_entries: list of custom Entry subclasses.
        :return: ResourceFactory instance.
        """
        super(ResourceFactory, self).__init__()

        self.entries_mapping = {}
        if custom_entries is not None:
            for c in custom_entries:
                ct = c.__content_type__
                self.entries_mapping[ct] = c

    def from_json(self, json):
        """Create resource out of JSON data.

        :param json: JSON dict.
        :return: Resource with a type defined by the given JSON data.
        """
        res_type = json['sys']['type']

        if ResourceType.Array.value == res_type:
            return self.create_array(json)
        elif ResourceType.Entry.value == res_type:
            return self.create_entry(json)
        elif ResourceType.Asset.value == res_type:
            return ResourceFactory.create_asset(json)
        elif ResourceType.ContentType.value == res_type:
            return ResourceFactory.create_content_type(json)
        elif ResourceType.Space.value == res_type:
            return ResourceFactory.create_space(json)

    @staticmethod
    def _extract_link(obj):
        if not isinstance(obj, dict):
            return None

        sys = obj.get('sys')
        if isinstance(sys, dict) and sys.get('type') == ResourceType.Link.value:
            return ResourceLink(sys)

        return None

    def create_entry(self, json):
        """Create :class:`.resources.Entry` from JSON.

        :param json: JSON dict.
        :return: Entry instance.
        """
        sys = json['sys']
        ct = sys['contentType']['sys']['id']
        fields = json['fields']
        raw_fields = copy.deepcopy(fields)

        # Replace links with :class:`.resources.ResourceLink` objects.
        for k, v in fields.items():
            link = ResourceFactory._extract_link(v)
            if link is not None:
                fields[k] = link
            elif isinstance(v, list):
                for idx, ele in enumerate(v):
                    link = ResourceFactory._extract_link(ele)
                    if link is not None:
                        v[idx] = link

        if ct in self.entries_mapping:
            clazz = self.entries_mapping[ct]
            result = clazz()

            for k, v in clazz.__entry_fields__.items():
                field_value = fields.get(v.field_id)
                if field_value is not None:
                    setattr(result, k, ResourceFactory.convert_value(field_value, v))
        else:
            result = Entry()

        result.sys = sys
        result.fields = fields
        result.raw_fields = raw_fields

        return result

    @staticmethod
    def create_asset(json):
        """Create :class:`.resources.Asset` from JSON.

        :param json: JSON dict.
        :return: Asset instance.
        """
        result = Asset(json['sys'])
        file_dict = json['fields']['file']
        result.url = file_dict['url']
        result.mimeType = file_dict['contentType']
        return result

    @staticmethod
    def create_content_type(json):
        """Create :class:`.resource.ContentType` from JSON.

        :param json: JSON dict.
        :return: ContentType instance.
        """
        result = ContentType(json['sys'])

        for field in json['fields']:
            field_id = field['id']
            del field['id']
            result.fields[field_id] = field

        result.name = json['name']
        result.display_field = json.get('displayField')

        return result

    @staticmethod
    def create_space(json):
        """Create :class:`.resources.Space` from JSON.

        :param json: JSON dict.
        :return: Space instance.
        """
        result = Space(json['sys'])
        result.name = json['name']
        return result

    @staticmethod
    def convert_value(value, field):
        """Given a :class:`.fields.Field` and a value, ensure that the value matches the given type, otherwise
        attempt to convert it.

        :param value: field value.
        :param field: :class:`.fields.Field` instance.
        :return: Result value.
        """
        clz = field.field_type

        if clz is Boolean:
            if not isinstance(value, bool):
                return bool(value)

        elif clz is Date:
            if not isinstance(value, str):
                value = str(value)
            return parser.parse(value)

        elif clz is Number:
            if not isinstance(value, int):
                return int(value)

        elif clz is Object:
            if not isinstance(value, dict):
                return ast.literal_eval(value)

        elif clz is Text or clz is Symbol:
            if not isinstance(value, str):
                return str(value)

        elif clz is List or clz is MultipleAssets or clz is MultipleEntries:
            if not isinstance(value, list):
                return [value]

        # No need to convert :class:`.fields.Link` types as the expected value
        # should be of type :class:`.resources.ResourceLink` for links.

        return value

    # Array
    def process_array_items(self, array, json):
        """Iterate through all `items` and create a resource for each.

        In addition map the resources under the `items_mapped` by the resource id and type.

        :param array: Array resource.
        :param json: Raw JSON dictionary.
        """
        for item in json['items']:
            key = None
            processed = self.from_json(item)

            if isinstance(processed, Asset):
                key = 'Asset'
            elif isinstance(processed, Entry):
                key = 'Entry'

            if key is not None:
                array.items_mapped[key][processed.sys['id']] = processed

            array.items.append(processed)

    def process_array_includes(self, array, json):
        """Iterate through all `includes` and create a resource for every item.

        In addition map the resources under the `items_mapped` by the resource id and type.

        :param array: Array resource.
        :param json: Raw JSON dictionary.
        """
        includes = json.get('includes') or {}
        for key in array.items_mapped.keys():
            if key in includes:
                for resource in includes[key]:
                    processed = self.from_json(resource)
                    array.items_mapped[key][processed.sys['id']] = processed

    def create_array(self, json):
        """Create :class:`.resources.Array` from JSON.

        :param json: JSON dict.
        :return: Array instance.
        """
        result = Array(json['sys'])
        result.total = json['total']
        result.skip = json['skip']
        result.limit = json['limit']
        result.items = []
        result.items_mapped = {'Asset': {}, 'Entry': {}}

        self.process_array_items(result, json)
        self.process_array_includes(result, json)

        return result