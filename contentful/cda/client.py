"""Core client module.

Classes provided include:

:class:`.Client` - Core client class for
connecting and retrieving resources from the Contentful Delivery API.

:class:`.Config` - Client configuration container.

:class:`.Dispatcher` - Class responsible for
invoking requests.

:class:`.Request` - Represents a future invokable
API request.

:class:`.RequestArray` - Represents a type of request
whose response may contain multiple resources.
"""


import requests
import const
from contentful.cda import utils
from contentful.cda.fields import MultipleAssets, MultipleEntries
from errors import ErrorMapping, ApiError
from serialization import ResourceFactory
from resources import Entry, ResourceLink


class Client(object):
    """Allows connecting and retrieving of resources from the Contentful Delivery API.

    Attributes:
      dispatcher (Dispatcher): Dispatcher for invoking requests.
    """
    def __init__(self, config):
        """Client constructor.

        :param config: Configuration settings.
        :return: Client instance.
        """
        super(Client, self).__init__()
        self.validate_config(config)
        self.dispatcher = Dispatcher(config)

    @staticmethod
    def validate_config(config):
        """Validate the given Config parameter for sane values.

        This will complete silently if validations pass, otherwise will raise
        an exception.

        :param config: Configuration container as passed to the constructor.
        """
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
            elif clazz.__name__ == Entry.__name__:
                raise Exception('Cannot register "Entry" as a custom entry class.')

    def fetch(self, resource_class):
        """Return a :class:`.Request` according to the given parameters.

        If used with a custom Entry class the Content Type ID will be inferred and provided with the request.

        Examples:
          client.fetch(Asset)
          client.fetch(Entry)
          client.fetch(ContentType)
          client.fetch(CustomEntryClass)

        :param resource_class: The type of resource to be fetched.
        :return: Request instance.
        """
        if issubclass(resource_class, Entry):
            params = None
            content_type = getattr(resource_class, '__content_type__', None)
            if content_type is not None:
                params = {'content_type': resource_class.__content_type__}
            return RequestArray(self.dispatcher, utils.path_for_class(resource_class), params=params)

        else:
            remote_path = utils.path_for_class(resource_class)
            if remote_path is None:
                raise Exception('Invalid resource type \"{0}\".'.format(resource_class))

            return RequestArray(self.dispatcher, remote_path)

    def fetch_space(self):
        """Fetch the Space associated with this client.

        :return: :class:`.resources.Space` result instance.
        """
        return Request(self.dispatcher, '').invoke()

    def resolve(self, link_resource_type, resource_id, array=None):
        """Resolve a link to a CDA resource.

        Given an `array` argument, attempt to retrieve the resource from the `mapped_items`
        section of that array (containing both included and regular resources), in case the
        resource cannot be found in the array or if no `array` is provided - attempt to fetch
        the resource from the API by issuing a network request.

        :param link_resource_type: Resource type as str.
        :param resource_id: Remote ID of the linked resource.
        :param array: Optional array resource to attempt fetching the item from.
        :return: Resource object, None if it cannot be retrieved.
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

        Extract the proper values and pass those to the `resolve` method of this class.

        :param resource_link: ResourceLink instance.
        :param array: Optional array resource to attempt fetching the item from.
        :return: Resource object, None if it cannot be retrieved.
        """
        return self.resolve(resource_link.link_type, resource_link.resource_id, array)

    def resolve_dict_link(self, dct, array=None):
        """Convenience method for resolving links given a dict object.

        Extract the proper values and pass those to the `resolve` method of this class.

        :param dct: Dictionary with the link data.
        :param array: Optional array resource to attempt fetching the item from.
        :return: Resource object, None if it cannot be retrieved.
        """
        sys = dct.get('sys')
        return self.resolve(sys['linkType'], sys['id'], array) if sys is not None else None

    # noinspection PyProtectedMember
    def resolve_array_links(self, array):
        """Attempt to resolve all links contained within an :class:`.resources.Array` object.

        :param array: Array instance.
        """
        for resource in array.items_mapped['Entry'].values():
            if issubclass(type(resource), Entry):
                for dct in [getattr(resource, '_cf_cda', {}), resource.fields]:
                    for k, v in dct.items():
                        if isinstance(v, ResourceLink):
                            resolved = self.resolve_resource_link(v, array)
                            if resolved is not None:
                                dct[k] = resolved
                        elif isinstance(v, (MultipleAssets, MultipleEntries, list)):
                            for idx, ele in enumerate(v):
                                if not isinstance(ele, ResourceLink):
                                    break

                                resolved = self.resolve_resource_link(ele, array)
                                if resolved is not None:
                                    v[idx] = resolved


class Config(object):
    """Configuration container to provide when creating :class:`.Client` objects."""
    def __init__(self, space_id, access_token, custom_entries=None, secure=True, endpoint=None):
        """Config constructor.

        :param space_id: Space ID.
        :param access_token: Access Token.
        :param custom_entries: Optional list of subclasses of the :class:`.resources.Entry` class. Provide
          this parameter in order to register custom Entry subclasses to be instantiated by the client
          when Entries of the given Content Type are retrieved from the server.
        :param secure: Indicates whether the connection should be encrypted or not.
        :param endpoint: Allows configuring a custom remote API endpoint.
        :return: Config instance.
        """
        super(Config, self).__init__()
        self.space_id = space_id
        self.access_token = access_token
        self.custom_entries = custom_entries or []
        self.secure = secure
        self.endpoint = endpoint or const.CDA_ADDRESS


class Dispatcher(object):
    """Responsible for invoking :class:`.Request` instances and delegating result processing.

    Attributes:
      config (Config): Configuration settings.
      resource_factory (ResourceFactory): Factory to use for generating resources out of JSON responses.
      base_url (str): Base URL of the remote endpoint.
    """
    def __init__(self, config):
        """Dispatcher constructor.

        :param config: Configuration settings.
        :return: Dispatcher instance.
        """
        super(Dispatcher, self).__init__()
        self.config = config
        self.resource_factory = ResourceFactory(config.custom_entries)

        scheme = 'https' if config.secure else 'http'
        self.base_url = '{0}://{1}/spaces/{2}'.format(scheme, config.endpoint, config.space_id)

    def invoke(self, request):
        """Invoke a given :class:`.Request` using the associated :class:`.Dispatcher`

        :param request: Request instance to invoke.
        :return: Result object, depending on the request type, could either
          be a :class:`.Array` or a single resource.
        """
        url = '{0}/{1}'.format(self.base_url, request.remote_path)
        r = requests.get(url, params=request.params, headers=self.get_headers())
        if 200 <= r.status_code < 300:
            return self.resource_factory.from_json(r.json())
        else:
            if r.status_code in ErrorMapping.mapping:
                raise ErrorMapping.mapping[r.status_code](r)
            else:
                raise ApiError(r)

    def get_headers(self):
        """Create and return a base set of headers to be carried with all requests.

        :return: Dictionary containing header values.
        """
        return {'Authorization': 'Bearer {0}'.format(self.config.access_token)}


class Request(object):
    """Represents a single request, later to be invoked by a :class:`.Dispatcher` instance."""
    def __init__(self, dispatcher, remote_path, params=None):
        """Request constructor.

        :param dispatcher: Dispatcher instance.
        :param remote_path: str representing the API path to point this request to.
        :param params: Optional dictionary of query parameters to provide with the request.
        :return: Request instance.
        """
        super(Request, self).__init__()
        self.dispatcher = dispatcher
        self.remote_path = remote_path
        self.params = params or {}

    def invoke(self):
        """Invoke request instance using the associated Dispatcher.

        :return: Result instance as returned by the Dispatcher.
        """
        return self.dispatcher.invoke(self)


class RequestArray(Request):
    """Represents a single request for retrieving multiple resources from the Delivery API."""
    def all(self):
        """Attempt to retrieve all available resources matching this request.

        :return: Result instance as returned by the Dispatcher.
        """
        return self.invoke()

    def first(self):
        """Attempt to retrieve only the first resource matching this request.

        :return: Result resource, or None if there are no matching resources.
        """
        self.params['limit'] = 1
        result = self.invoke()
        return result.items[0] if result.total > 0 else None

    def where(self, params):
        """Set a dict of parameters to be passed to the Delivery API when invoking this request.

        :param params: dict containing a collection of key-value properties to pass with this request.
        :return: this RequestArray instance for convenience.
        """
        self.params = dict(params.items() + self.params.items())  # TODO check for conflicts
        return self