from umachine import Pin
from tinyhttpserver import HttpRequest, HttpResponse, HttpRequestHandler


class RequestHandler(HttpRequestHandler):
    def __init__(self, red_led: Pin, green_led: Pin, blue_led: Pin):
        super().__init__()
        self.red_led = red_led
        self.green_led = green_led
        self.blue_led = blue_led

    def handle_request(self, request: HttpRequest) -> HttpResponse | None:
        if request.method == "GET":
            if request.target == "/" or request.target.startswith("/?"):
                with open("index.html", "r") as f:
                    index_page = f.read()
                if request.target == "/?color=red":
                    self.red_led.on()
                    self.green_led.off()
                    self.blue_led.off()
                elif request.target == "/?color=green":
                    self.red_led.off()
                    self.green_led.on()
                    self.blue_led.off()
                elif request.target == "/?color=blue":
                    self.red_led.off()
                    self.green_led.off()
                    self.blue_led.on()
                elif request.target == "/?color=off":
                    self.red_led.off()
                    self.green_led.off()
                    self.blue_led.off()

                return HttpResponse(200, "OK", index_page, "text/html")
        return None
