from tinyhttpserver import HttpRequest, HttpResponse


class HttpRequestHandler:
    """Handles HTTP requests.

    This base class needs to be subclassed to handle HTTP requests. The subclass
    needs to override the handle_request method.
    """

    def handle_request(self, request: HttpRequest) -> HttpResponse | None:
        """This method is called when a request is received.

        Args:
            request (HttpRequest): The request that was received.

        Returns:
            HttpResponse | None: The response to send back to the client. If None, a 404 Not Found response is returned.
        """
        raise NotImplementedError()
