import requests
import const
from lib.serialization import ResourceFactory
from resources import Entry, Asset, ContentType


class Client(object):
    def __init__(self, config):
        super(Client, self).__init__()
        self.validate_config(config)
        self.dispatcher = Dispatcher(config)

    @staticmethod
    def validate_config(config):
        if config is None:
            raise Exception('Config parameter must not be empty.')

        non_null_params = ['space_id', 'access_token']
        for param in non_null_params:
            if getattr(config, param) is None:
                raise Exception('Configuration for \"{0}\" must not be empty.'.format(param))

        for clazz in config.custom_entries:
            if not issubclass(clazz, Entry):
                raise Exception(
                    'Provided class \"{0}\" must be a subclass of Entry.'.format(clazz.__name__))
            elif clazz.__name__ == 'Entry':
                raise Exception('Cannot register "Entry" as a custom entry class.')

    def fetch(self, resource_type):
        if issubclass(resource_type, Entry):
            params = None
            content_type = getattr(resource_type, '__content_type__', None)
            if content_type is not None:
                # TODO ensure custom entry class was registered
                params = {'content_type': resource_type.__content_type__}
            return RequestArray(self.dispatcher, 'entries', params=params)

        else:
            remote_path = None

            if issubclass(resource_type, Asset):
                remote_path = 'assets'
            elif issubclass(resource_type, ContentType):
                remote_path = 'content_types'

            if remote_path is None:
                raise Exception('Invalid resource type \"{0}\".'.format(resource_type))

            return RequestArray(self.dispatcher, remote_path)

    def fetch_space(self):
        return self.dispatcher.invoke(RequestSingle(self.dispatcher, ''))


class Config(object):
    def __init__(self, space_id, access_token, custom_entries=None, secure=True, endpoint=None):
        super(Config, self).__init__()
        self.space_id = space_id
        self.access_token = access_token
        self.custom_entries = custom_entries or []
        self.secure = secure
        self.endpoint = endpoint or const.CDA_ADDRESS


class ApiException(Exception):
    def __init__(self, result, message=None):
        self.result = result
        super(ApiException, self).__init__(
            message or result.text or 'Request failed with status \"{0}\".'.format(result.status_code))


class Dispatcher(object):
    def __init__(self, config):
        super(Dispatcher, self).__init__()
        self.config = config
        self.resource_factory = ResourceFactory(config.custom_entries)

        scheme = 'https' if config.secure else 'http'
        self.base_url = '{0}://{1}/spaces/{2}'.format(scheme, config.endpoint, config.space_id)

    def invoke(self, request):
        url = '{0}/{1}'.format(self.base_url, request.remote_path)
        r = requests.get(url, params=request.params, headers=self.get_headers())
        if 200 <= r.status_code < 300:
            return self.resource_factory.from_json(r.json())
        else:
            raise ApiException(r)

    def get_headers(self):
        return {'Authorization': 'Bearer {0}'.format(self.config.access_token)}


class RequestBase(object):
    def __init__(self, dispatcher, remote_path, params=None):
        super(RequestBase, self).__init__()
        self.dispatcher = dispatcher
        self.remote_path = remote_path
        self.params = params or {}


class RequestSingle(RequestBase):
    def __init__(self, dispatcher, remote_path, params=None):
        super(RequestSingle, self).__init__(dispatcher, remote_path, params)
        self.dispatcher.invoke(self)


class RequestArray(RequestBase):
    def all(self):
        return self.dispatcher.invoke(self)

    def first(self):
        self.params['limit'] = 1
        result = self.dispatcher.invoke(self)
        return result.items[0] if result.total > 0 else None

    def where(self, params):
        self.params = dict(params + self.params)  # TODO check for conflicts
        return self