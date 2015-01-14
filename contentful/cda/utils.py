"""Utilities module."""

from . import const
from .resources import ResourceType, Asset, ContentType, Entry, Space


def path_for_class(clz):
    if issubclass(clz, Asset):
        return const.PATH_ASSETS
    elif issubclass(clz, ContentType):
        return const.PATH_CONTENT_TYPES
    elif issubclass(clz, Entry):
        return const.PATH_ENTRIES


def class_for_type(resource_type):
    if resource_type == ResourceType.Asset.value:
        return Asset
    elif resource_type == ResourceType.ContentType.value:
        return ContentType
    elif resource_type == ResourceType.Entry.value:
        return Entry
    elif resource_type == ResourceType.Space.value:
        return Space
