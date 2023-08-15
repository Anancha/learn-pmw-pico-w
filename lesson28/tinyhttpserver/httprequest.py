class HttpRequest:
    def __init__(self, method: str, target: str, version: str):
        """Creates a new instance of HttpRequest.

        Args:
            method (str): The HTTP method (GET, PUT, POST, HEAD, OPTIONS).
            target (str): The request target (typically a URL)
            version (str): The HTTP version (ex: HTTP/1.1).
        """
        self.method = method
        self.target = target
        self.version = version
