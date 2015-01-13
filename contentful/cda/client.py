"""Core client module.

Classes provided include:

- :class:`.Client` - Interface for retrieving resources from the Contentful Delivery API.

- :class:`.Config` - Configuration container for :class:`.Client` objects.

- :class:`.Dispatcher` - Class responsible for invoking :class:`.Request` instances.

- :class:`.Request` - API request representation.

- :class:`.RequestArray` - Request whose response may contain multiple resources.
"""
from . import utils
from . import const
from .errors import ErrorMapping, ApiError
from .serialization import ResourceFactory
from .resources import Entry
from .version import __version__
import requests


class Client(object):
    """Interface for retrieving resources from the Contentful Delivery API.

    **Attributes**:

    - dispatcher (:class:`.Dispatcher`): Dispatcher for invoking requests.
    - config (:class:`.Config`): Configuration container.
    """
    def __init__(self, space_id, access_token, custom_entries=None, secure=True, endpoint=None, resolve_links=True):
        """Client constructor.

        :param space_id: (str) Space ID.
        :param access_token: (str) Access Token.
        :param custom_entries: (list) Optional list of :class:`.Entry` subclasses
            used in order to register custom Entry subclasses to be instantiated by the client
            when Entries of the given Content Type are retrieved from the server.
        :param secure: (bool) Indicates whether the connection should be encrypted or not.
        :param endpoint: (str) Custom remote API endpoint.
        :param resolve_links: (bool) Indicates whether or not to resolve links automatically.
        :return: :class:`Client` instance.
        """
        super(Client, self).__init__()
        config = Config(space_id, access_token, custom_entries, secure, endpoint, resolve_links)
        self.config = config
        self.validate_config(config)
        self.dispatcher = Dispatcher(config, requests)

    @staticmethod
    def validate_config(config):
        """Verify sanity for a :class:`.Config` instance.

        This will raise an exception in case conditions are not met, otherwise
        will complete silently.

        :param config: (:class:`.Config`) Configuration container.
        """
        non_null_params = ['space_id', 'access_token']
        for param in non_null_params:
            if getattr(config, param) is None:
                raise Exception('Configuration for \"{0}\" must not be empty.'.format(param))

        for clazz in config.custom_entries:
            if not issubclass(clazz, Entry):
                raise Exception(
                    'Provided class \"{0}\" must be a subclass of Entry.'.format(clazz.__name__))
            elif clazz is Entry:
                raise Exception('Cannot register "Entry" as a custom entry class.')

    def fetch(self, resource_class):
        """Construct a :class:`.Request` for the given resource type.

        Provided an :class:`.Entry` subclass, the Content Type ID will be inferred and requested explicitly.

        Examples::

            client.fetch(Asset)
            client.fetch(Entry)
            client.fetch(ContentType)
            client.fetch(CustomEntryClass)

        :param resource_class: The type of resource to be fetched.
        :return: :class:`.Request` instance.
        """
        if issubclass(resource_class, Entry):
            params = None
            content_type = getattr(resource_class, '__content_type__', None)
            if content_type is not None:
                params = {'content_type': resource_class.__content_type__}
            return RequestArray(self.dispatcher, utils.path_for_class(resource_class), self.config.resolve_links,
                                params=params)

        else:
            remote_path = utils.path_for_class(resource_class)
            if remote_path is None:
                raise Exception('Invalid resource type \"{0}\".'.format(resource_class))

            return RequestArray(self.dispatcher, remote_path, self.config.resolve_links)

    def fetch_space(self):
        """Fetch the Space associated with this client.

        :return: :class:`.Space` result instance.
        """
        return Request(self.dispatcher, '').invoke()

    def resolve(self, link_resource_type, resource_id, array=None):
        """Resolve a link to a CDA resource.

        Provided an `array` argument, attempt to retrieve the resource from the `mapped_items`
        section of that array (containing both included and regular resources), in case the
        resource cannot be found in the array (or if no `array` was provided) - attempt to fetch
        the resource from the API by issuing a network request.

        :param link_resource_type: (str) Resource type as str.
        :param resource_id: (str) Remote ID of the linked resource.
        :param array: (:class:`.Array`) Optional array resource.
        :return: :class:`.Resource` subclass, `None` if it cannot be retrieved.
        """
        result = None

        if array is not None:
            container = array.items_mapped.get(link_resource_type)
            result = container.get(resource_id)

        if result is None:
            clz = utils.class_for_type(link_resource_type)
            result = self.fetch(clz).where({'sys.id': resource_id}).first()

        return result

    def resolve_resource_link(self, resource_link, array=None):
        """Convenience method for resolving links given a :class:`.resources.ResourceLink` object.

        Extract link values and pass to the :func:`.resolve` method of this class.

        :param resource_link: (:class:`.ResourceLink`) instance.
        :param array: (:class:`.Array`) Optional array resource.
        :return: :class:`.Resource` subclass, `None` if it cannot be retrieved.
        """
        return self.resolve(resource_link.link_type, resource_link.resource_id, array)

    def resolve_dict_link(self, dct, array=None):
        """Convenience method for resolving links given a dict object.

        Extract link values and pass to the :func:`.resolve` method of this class.

        :param dct: (dict) Dictionary with the link data.
        :param array: (:class:`.Array`) Optional array resource.
        :return: :class:`.Resource` subclass, `None` if it cannot be retrieved.
        """
        sys = dct.get('sys')
        return self.resolve(sys['linkType'], sys['id'], array) if sys is not None else None


class Config(object):
    """Configuration container for :class:`.Client` objects."""
    def __init__(self, space_id, access_token, custom_entries, secure, endpoint, resolve_links):
        """Config constructor.

        :param space_id: (str) Space ID.
        :param access_token: (str) Access Token.
        :param custom_entries: (list) Optional list of :class:`.Entry` subclasses
            used in order to register custom Entry subclasses to be instantiated by the client
            when Entries of the given Content Type are retrieved from the server.
        :param secure: (bool) Indicates whether the connection should be encrypted or not.
        :param endpoint: (str) Custom remote API endpoint.
        :param resolve_links: (bool) Indicates whether or not to resolve links automatically.
        :return: Config instance.
        """
        super(Config, self).__init__()
        self.space_id = space_id
        self.access_token = access_token
        self.custom_entries = custom_entries or []
        self.secure = secure
        self.endpoint = endpoint or const.CDA_ADDRESS
        self.resolve_links = resolve_links


class Dispatcher(object):
    """Responsible for invoking :class:`.Request` instances and delegating result processing.

    **Attributes**:

    - config (:class:`.Config`): Configuration settings.
    - resource_factory (:class:`.ResourceFactory`): Factory to use for generating resources out of JSON responses.
    - httpclient (module): HTTP client module.
    - base_url (str): Base URL of the remote endpoint.
    - user_agent (str): ``User-Agent`` header to pass with requests.
    """
    def __init__(self, config, httpclient):
        """Dispatcher constructor.

        :param config: Configuration container.
        :param httpclient: HTTP client.
        :return: :class:`.Dispatcher` instance.
        """
        super(Dispatcher, self).__init__()
        self.config = config
        self.resource_factory = ResourceFactory(config.custom_entries)
        self.httpclient = httpclient
        self.user_agent = 'contentful.py/{0}'.format(__version__)

        scheme = 'https' if config.secure else 'http'
        self.base_url = '{0}://{1}/spaces/{2}'.format(scheme, config.endpoint, config.space_id)

    def invoke(self, request):
        """Invoke the given :class:`.Request` instance using the associated :class:`.Dispatcher`.

        :param request: :class:`.Request` instance to invoke.
        :return: :class:`.Resource` subclass.
        """
        url = '{0}/{1}'.format(self.base_url, request.remote_path)
        r = self.httpclient.get(url, params=request.params, headers=self.get_headers())
        if 200 <= r.status_code < 300:
            return self.resource_factory.from_json(r.json())
        else:
            if r.status_code in ErrorMapping.mapping:
                raise ErrorMapping.mapping[r.status_code](r)
            else:
                raise ApiError(r)

    def get_headers(self):
        """Create and return a base set of headers to be carried with all requests.

        :return: dict containing header values.
        """
        return {'Authorization': 'Bearer {0}'.format(self.config.access_token), 'User-Agent': self.user_agent}


class Request(object):
    """Represents a single request, later to be invoked by a :class:`.Dispatcher`."""
    def __init__(self, dispatcher, remote_path, params=None):
        """Request constructor.

        :param dispatcher: (:class:`.Dispatcher`) Dispatcher.
        :param remote_path: (str) API path.
        :param params: Optional dictionary of query parameters.
        :return: :class:`.Request` instance.
        """
        super(Request, self).__init__()
        self.dispatcher = dispatcher
        self.remote_path = remote_path
        self.params = params or {}

    def invoke(self):
        """Invoke :class:`.Request` instance using the associated :class:`.Dispatcher`.

        :return: Result instance as returned by the :class:`.Dispatcher`.
        """
        return self.dispatcher.invoke(self)


class RequestArray(Request):
    """Represents a single request for retrieving multiple resources from the API."""

    def __init__(self, dispatcher, remote_path, resolve_links, params=None):
        super(RequestArray, self).__init__(dispatcher, remote_path, params)
        self.resolve_links = resolve_links

    def all(self):
        """Attempt to retrieve all available resources matching this request.

        :return: Result instance as returned by the :class:`.Dispatcher`.
        """
        result = self.invoke()
        if self.resolve_links:
            result.resolve_links()

        return result

    def first(self):
        """Attempt to retrieve only the first resource matching this request.

        :return: Result instance, or `None` if there are no matching resources.
        """
        self.params['limit'] = 1
        result = self.invoke()
        return result.items[0] if result.total > 0 else None

    def where(self, params):
        """Set a dict of parameters to be passed to the API when invoking this request.

        :param params: (dict) query parameters.
        :return: this :class:`.RequestArray` instance for convenience.
        """
        self.params = dict(self.params, **params)   # params overrides self.params
        return self