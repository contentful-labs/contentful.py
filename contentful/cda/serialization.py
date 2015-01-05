import ast
from dateutil import parser
from fields import Boolean, Date, Number, Object, Symbol, Text, List, MultipleAssets, MultipleEntries
from resources import ResourceType, Array, Entry, Asset, Space, ContentType


class ResourceFactory(object):
    def __init__(self, custom_entries):
        super(ResourceFactory, self).__init__()

        self.entries_mapping = {}
        if custom_entries is not None:
            for c in custom_entries:
                ct = c.__content_type__
                self.entries_mapping[ct] = c

    def from_json(self, json):
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

    def create_array(self, json):
        result = Array(json['sys'])
        result.total = json['total']
        result.skip = json['skip']
        result.limit = json['limit']

        result.items = items = []
        for item in json['items']:
            items.append(self.from_json(item))

        return result

    def create_entry(self, json):
        sys = json['sys']
        ct = sys['contentType']['sys']['id']
        fields = json['fields']

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
        return result

    @staticmethod
    def create_asset(json):
        result = Asset(json['sys'])
        file_dict = json['fields']['file']
        result.url = file_dict['url']
        result.mimeType = file_dict['contentType']
        return result

    @staticmethod
    def create_content_type(json):
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
        result = Space(json['sys'])
        result.name = json['name']
        return result

    @staticmethod
    def convert_value(value, field):
        clz = field.field_type.__name__

        if clz == Boolean.__name__:
            if not isinstance(value, bool):
                return bool(value)

        elif clz == Date.__name__:
            if not isinstance(value, str):
                value = str(value)
            return parser.parse(value)

        elif clz == Number.__name__:
            if not isinstance(value, int):
                return long(value)

        elif clz == Object.__name__:
            if not isinstance(value, dict):
                return ast.literal_eval(value)

        elif clz == Text.__name__ or clz == Symbol.__name__:
            if not isinstance(value, str):
                return str(value)

        elif clz == List.__name__ or clz == MultipleAssets.__name__ or clz == MultipleEntries.__name__:
            if not isinstance(value, list):
                return [value]

        return value