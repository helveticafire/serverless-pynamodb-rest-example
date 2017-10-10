import json
import http


class HttpResponseLambdaBase:
    """
    An HTTP response base class with dictionary-accessed headers.

    This class doesn't handle content. It should not be used directly.
    Use the HttpResponse and StreamingHttpResponse subclasses instead.
    """

    status_code = http.HTTPStatus.OK.value
    is_base_64_encoded = False
    headers = {}
    body = None

    def __dict__(self):
        result = {'statusCode': self.status_code,
                  'isBase64Encoded': self.is_base_64_encoded}
        if self.headers:
            result['headers'] = self.headers
        if self.body:
            result['body'] = self.body
        return result


class HttpNoContentResponse(HttpResponseLambdaBase):
    status_code = http.HTTPStatus.NO_CONTENT.value


class HttpJSONResponse(HttpResponseLambdaBase):

    def __init__(self, status=None, body=None):
        if status is not None:
            try:
                self.status_code = int(status)
            except (ValueError, TypeError):
                raise TypeError('HTTP status code must be an integer.')

            if not http.HTTPStatus.CONTINUE.value <= self.status_code <= 599:
                raise ValueError('HTTP status code must be an integer from 100 to 599.')
        if body:
            self.body = json.dumps(body)


class HttpErrorResponseBase(HttpJSONResponse):

    def __init__(self, status=None, error_code=None, error_message=None):
        body = {'error_code': error_code,
                'error_message': error_message}
        super().__init__(status, body)


class HttpResponseNotFound(HttpErrorResponseBase):

    def __init__(self, error_message=None):
        super().__init__(status=http.HTTPStatus.NOT_FOUND.value,
                         error_code='NOT_FOUND',
                         error_message=error_message)


class HttpResponseBadRequest(HttpErrorResponseBase):

    def __init__(self, error_code=None, error_message=None):
        super().__init__(status=http.HTTPStatus.BAD_REQUEST.value,
                         error_code=error_code,
                         error_message=error_message)


class HttpResponseServerError(HttpErrorResponseBase):

    def __init__(self, error_code=None, error_message=None):
        super().__init__(status=http.HTTPStatus.INTERNAL_SERVER_ERROR.value,
                         error_code=error_code,
                         error_message=error_message)