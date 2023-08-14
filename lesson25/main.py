import math
from machine import Pin, I2C

# https://github.com/stlehmann/micropython-ssd1306
# https://docs.micropython.org/en/latest/esp8266/tutorial/ssd1306.html
from ssd1306 import SSD1306, SSD1306_I2C


def draw_circle(x: int, y: int, r: int, lw: int, dsp: SSD1306):
    """
    Draw a circle on the display

    Args:
        x (int): x coordinate of the center of the circle
        y (int): y coordinate of the center of the circle
        r (int): radius of the circle
        lw (int): line width of the circle
        dsp (SSD1306): display object
    """
    for lw in range(0, lw):
        for deg in range(0, 360, 1):
            x1 = int((r - lw) * math.cos(math.radians(deg)))
            y1 = int((r - lw) * math.sin(math.radians(deg)))
            dsp.pixel(x + x1, y + y1, 1)


dsp = SSD1306_I2C(128, 64, I2C(1, sda=Pin(18), scl=Pin(19)))

dsp.text("My Circle", 0, 0, 1)
draw_circle(64, 40, 20, 1, dsp)
dsp.show()
