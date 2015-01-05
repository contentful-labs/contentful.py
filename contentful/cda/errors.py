"""Errors module."""


class ErrorMapping(object):
    """Holds a mapping of HTTP status codes and :class:`.ApiError` subclasses."""
    mapping = {}


class ApiError(Exception):
    """Class representing an error returned by the remote API."""
    def __init__(self, result, message=None):
        """ApiError constructor.

        :param result: Raw result object.
        :param message: Optional message to provide with the exception.
        :return: ApiError instance.
        """
        self.result = result
        super(ApiError, self).__init__(
            message or result.text or 'Request failed with status \"{0}\".'.format(result.status_code))


def api_exception(http_code):
    """Convenience decorator to associate HTTP status codes with :class:`.ApiError` subclasses.

    :param http_code: HTTP status code
    :return: ...
    """
    def wrapper(*args):
        code = args[0]
        ErrorMapping.mapping[http_code] = code
        return code
    return wrapper


@api_exception(400)
class BadRequest(ApiError):
    """BadRequest, malformed data sent by the client."""
    pass


@api_exception(401)
class Unauthorized(ApiError):
    """Unauthorized error, raised when providing invalid credentials."""
    pass


@api_exception(403)
class AccessDenied(ApiError):
    """AccessDenied, raised when referencing a resource without proper credentials."""
    pass


@api_exception(404)
class NotFound(ApiError):
    """NotFound error, raised when referencing a missing resource."""
    pass


@api_exception(500)
class ServerError(ApiError):
    """ServerError, raised when the server fails internally."""
    pass


@api_exception(503)
class ServiceUnavailable(ApiError):
    """ServiceUnavailable error, raised when the server overloads."""
    pass