import math
from machine import Pin, I2C

# https://github.com/stlehmann/micropython-ssd1306
# https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html
from ssd1306 import SSD1306, SSD1306_I2C


# Draw Lissajous pattern
# https://en.wikipedia.org/wiki/Lissajous_curve
def draw_lissajous_curve(a: int, b: int, delta: float, dsp: SSD1306):
    for deg in range(0, 360, 1):
        t = math.radians(deg)
        x = int(64 * math.sin(a * t + delta))
        y = int(32 * math.sin(b * t))
        dsp.pixel(x + 64, y + 32, 1)  # Shift by half screen size


dsp = SSD1306_I2C(128, 64, I2C(1, sda=Pin(18), scl=Pin(19)))

# Lissajous parameters
# Change these to get different patterns
a = 1
b = 2

while True:
    for deg in range(0, 360, 1):
        delta = math.radians(deg)
        dsp.fill(0)
        draw_lissajous_curve(a, b, delta, dsp)
        dsp.show()
