# Fields
class Field(object):
    def __init__(self, field_type, field_id=None):
        self.field_type = field_type
        self.field_id = field_id

    def __get__(self, instance, owner):
        dct = Field.dict_for_instance(instance)
        return None if dct is None else dct.get(self.field_id, None)

    def __set__(self, instance, value):
        dct = Field.dict_for_instance(instance)

        if dct is None:
            instance._cf_cda = dct = {}

        dct[self.field_id] = value

    @staticmethod
    def dict_for_instance(instance):
        return getattr(instance, '_cf_cda', None)


class FieldOwner(type):
    registry = {}

    def __new__(mcs, name, bases, attrs):
        is_custom = name != 'Entry'
        content_type_id = None

        fields = {}
        for n, v in attrs.items():
            if isinstance(v, Field):
                if v.field_id is None:
                    v.field_id = n
                fields[n] = v
            elif is_custom and n == '__content_type__':
                content_type_id = v

        if is_custom and content_type_id is None:
            raise AttributeError('Class {0} does not have a __content_type__ specified.'.format(name))

        attrs['__entry_fields__'] = fields
        return super(FieldOwner, mcs).__new__(mcs, name, bases, attrs)


# Field Types
class FieldType(object):
    pass


class Boolean(FieldType):
    pass


class Date(FieldType):
    pass


class Integer(FieldType):
    pass


class Link(FieldType):
    pass


class Location(FieldType):
    pass


class Number(FieldType):
    pass


class Object(FieldType):
    pass


class Symbol(FieldType):
    pass


class Text(FieldType):
    pass


class MultipleAssets(FieldType):
    pass


class MultipleEntries(FieldType):
    pass