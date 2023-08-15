import usocket as socket
import utime as time
from tinyhttpserver import HttpRequest, HttpResponse, HttpRequestHandler

class ServerStatus:
    STOPPED = 0
    STARTING = 1
    RUNNING = 2
    STOPPING = 3

class TinyHttpServer:
    _DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    _MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    def __init__(self, addr: str, port: int, request_handler: HttpRequestHandler):
        self.addr = addr
        self.port = port
        self.request_handler = request_handler
        self.max_request_size = 1024
        self.max_concurrent_requests = 1
        self.status = ServerStatus.STOPPED
        self._server_socket = None

    def start(self):
        # The server can start only if it's stopped
        if self.status != ServerStatus.STOPPED:
            return

        # Create a new server socket
        print("Starting TinyHttpServer...")
        self.status = ServerStatus.STARTING
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket = server_socket

        try:
            # Starts listening for incoming connections
            server_socket.bind((self.addr, self.port))
            server_socket.listen(self.max_concurrent_requests)
            self.status = ServerStatus.RUNNING
            print("TinyHttpServer listening at address {0} port {1}".format(self.addr, self.port))

            while self.status == ServerStatus.RUNNING:
                client_socket = None

                try:
                    # Parse the incoming request
                    client_socket, client_addr = server_socket.accept()
                    request = self._parse_request(client_socket.recv(self.max_request_size))

                    if request is None:
                        print(client_addr, "<Invalid request>")
                        self._send_response(HttpResponse(400, "Bad Request", None, None), client_socket)
                        continue

                    print(client_addr, request.method, request.target, request.version)

                    # We only support support HTTP/1.x (not HTTP/2.x)
                    if not request.version.startswith("HTTP/1."):
                        self._send_response(HttpResponse(505, "HTTP Version Not Supported", None, None), client_socket)
                        continue

                    # Handle the request. If the handler returns None, it's
                    # because it didn't know how to handle the request. We
                    # return a 404 response in that case.
                    response = self.request_handler.handle_request(request)
                    if response is None:
                        response = HttpResponse(404, "Not Found", None, None)
                    self._send_response(response, client_socket)
                except OSError as ex:
                    # Log the error only if the server is running as it is
                    # normal to get an error when stopping the server
                    if self.status == ServerStatus.RUNNING:
                        print("TinyHttpServer client socket error: ", ex)
                finally:
                    if client_socket is not None:
                        client_socket.close()
        finally:
            # Make sure the server is stopped when we exit this method so
            # the server socket is properly closed, even if an exception
            # occurred
            self.stop()

    def stop(self):
        # If we don't have a server socket, we're not running
        if self.status != ServerStatus.RUNNING:
            return

        print("Stopping TinyHttpServer...")
        self.status = ServerStatus.STOPPING
        socket = self._server_socket
        self._server_socket = None

        try:
            if socket is not None:
                socket.close()
        except:
            pass

        self.status = ServerStatus.STOPPED
        print("TinyHttpServer stopped")

    def _encode_response(self, http_response: HttpResponse) -> bytes:
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages#http_responses

        # Status line
        response = "HTTP/1.1 {} {}\r\n".format(http_response.code, http_response.status_message)

        # Headers
        content_type = "text/plain" if http_response.content_type is None else http_response.content_type
        response += "Content-Type: {}\r\n".format(content_type)

        content_length = 0 if http_response.content is None else len(http_response.content.encode("utf-8"))
        response += "Content-Length: {}\r\n".format(content_length)
        response += "Server: TinyHttpServer\r\n"

        response += "Date: {}\r\n".format(self._get_timestamp())
        response += "Connection: close\r\n"
        response += "Cache-Control: no-cache\r\n"

        # Payload
        if http_response.content is not None:
            response += "\r\n"
            response += http_response.content

        # Encode and return the response
        return response.encode("utf-8")

    def _get_timestamp(self) -> str:
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Date
        # Date: <day-name>, <day> <month> <year> <hour>:<minute>:<second> GMT
        current_time = time.gmtime()
        timestamp = "{}, {:02} {} {:04} {:02}:{:02}:{:02} GMT".format(
            TinyHttpServer._DAYS[current_time[6]],  # Day name
            current_time[2],  # Day
            TinyHttpServer._MONTHS[current_time[1]],  # Month
            current_time[0],  # Year
            current_time[3],  # Hour
            current_time[4],  # Minute
            current_time[5],  # Second
        )
        return timestamp

    def _parse_request(self, request: bytes) -> HttpRequest | None:
        # Decode the request
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages#http_requests
        lines = None
        try:
            lines = request.decode("utf-8").replace("\r", "").split("\n")
        except UnicodeError:
            return None

        # Parse the start line
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages#start_line
        request_line = lines[0].split(" ")
        if len(request_line) != 3:
            return None
        method = request_line[0].strip()
        target = request_line[1].strip()
        version = request_line[2].strip()

        # Parse the headers
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages#headers
        # This is not implemented

        # Parse the body
        # https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages#body
        # This is not implemented

        # Return the request
        return HttpRequest(method, target, version)

    def _send_response(self, response: HttpResponse, client_socket: socket.socket):
        if self.status == ServerStatus.RUNNING:
            print(response.code, response.status_message)
            encoded_response = self._encode_response(response)
            client_socket.send(encoded_response)