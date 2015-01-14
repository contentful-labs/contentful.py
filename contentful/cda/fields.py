"""fields module.

Classes provided include:

- :class:`.Field` - An Entry field.

- :class:`.FieldOwner` - Meta-class to enable usage of :class:`.Field`-typed fields.

- :class:`.FieldType` - Type of a field.

- :class:`.Boolean` - Field holding a boolean value.

- :class:`.Date` - Field holding a date value.

- :class:`.Link` - Field holding a link value.

- :class:`.Location` - Field holding a location value.

- :class:`.Number` - Field holding a numeric value.

- :class:`.Object` - Field holding an object value.

- :class:`.Symbol` - Field holding a symbol value.

- :class:`.Text` - Field holding a text value.

- :class:`.List` - Field holding a list value.

- :class:`.MultipleAssets` - Field holding multiple Assets as a value.

- :class:`.MultipleEntries` - Field holding multiple Entries as a value.
"""


class Field(object):
    """Class representing a single Entry field."""

    def __init__(self, field_type, field_id=None):
        """Field constructor.

        :param field_type: (:class:`.FieldType`) type of field.
        :param field_id: (str) Custom ID to set for this field, by default this will
            be inferred by the name of the attribute.
        :return: Field instance.
        """
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
    """Metaclass for the :class:`.Entry` class.

    For any subclass (i.e. representing a custom Entry class), ensure the extending class has
    a valid `__content_type__` attribute specified, otherwise raise an exception.
    In addition, iterate through all of the class attributes, identify any :class:`.Field`-typed
    attributes and keep those in a dict under the class's `__entry_fields__` attribute.
    """
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
    """Base field type."""


class Boolean(FieldType):
    """Boolean typed field"""


class Date(FieldType):
    """Date typed field."""


class Link(FieldType):
    """Link typed field."""


class Location(FieldType):
    """Location typed field."""


class Number(FieldType):
    """Number typed field."""


class Object(FieldType):
    """Object typed field."""


class Symbol(FieldType):
    """Symbol typed field."""


class Text(FieldType):
    """Text typed field."""


class List(FieldType):
    """List typed field."""


class MultipleAssets(FieldType):
    """Multiple Assets typed field."""


class MultipleEntries(FieldType):
    """Multiple Entries typed field."""