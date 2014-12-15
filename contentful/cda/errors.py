class ErrorMapping(object):
    mapping = {}


class ApiError(Exception):
    def __init__(self, result, message=None):
        self.result = result
        super(ApiError, self).__init__(
            message or result.text or 'Request failed with status \"{0}\".'.format(result.status_code))


def api_exception(http_code):
    def wrapper(*args):
        code = args[0]
        ErrorMapping.mapping[http_code] = code
        return code
    return wrapper


@api_exception(400)
class BadRequest(ApiError):
    pass


@api_exception(401)
class Unauthorized(ApiError):
    pass


@api_exception(403)
class AccessDenied(ApiError):
    pass


@api_exception(404)
class NotFound(ApiError):
    pass


@api_exception(500)
class ServerError(ApiError):
    pass


@api_exception(503)
class ServiceUnavailable(ApiError):
    pass