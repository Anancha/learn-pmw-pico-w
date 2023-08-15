class HttpResponse:
    def __init__(self, code: int, status_message: str, content: str | None, content_type: str | None):
        """Creates a new instance of HttpResponse.

        Args:
            code (int): The HTTP status code.
            status_message (str): The HTTP status message.
            content (str | None): The response's content.
            content_type (str | None): The response's MIME content type.
        """
        self.code = code
        self.status_message = status_message
        self.content = content
        self.content_type = content_type
