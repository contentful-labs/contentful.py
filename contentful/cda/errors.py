"""errors module."""


class ErrorMapping(object):
    """Holds a mapping of HTTP status codes and :class:`.ApiError` subclasses."""
    mapping = {}


class ApiError(Exception):
    """Class representing an error returned by the API."""
    def __init__(self, result, message=None):
        """ApiError constructor.

        :param result: Raw result object.
        :param message: (str) Optional message.
        :return: :class:`.ApiError` instance.
        """
        self.result = result
        super(ApiError, self).__init__(
            message or result.text or 'Request failed with status \"{0}\".'.format(result.status_code))


def api_exception(http_code):
    """Convenience decorator to associate HTTP status codes with :class:`.ApiError` subclasses.

    :param http_code: (int) HTTP status code.
    :return: wrapper function.
    """
    def wrapper(*args):
        code = args[0]
        ErrorMapping.mapping[http_code] = code
        return code
    return wrapper


@api_exception(400)
class BadRequest(ApiError):
    """Bad Request"""


@api_exception(401)
class Unauthorized(ApiError):
    """Unauthorized"""


@api_exception(403)
class AccessDenied(ApiError):
    """Access Denied"""


@api_exception(404)
class NotFound(ApiError):
    """Not Found"""


@api_exception(500)
class ServerError(ApiError):
    """Internal Server Error"""


@api_exception(503)
class ServiceUnavailable(ApiError):
    """Service Unavailable Error"""