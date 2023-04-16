# Lesson: https://youtu.be/yZkx-KWbATY
from machine import PWM, Pin

# setup led as a tuple of 3 values (red pin, green pin, blue pin)
rgb_led = tuple(PWM(Pin(x)) for x in (12, 11, 10))
for pin in rgb_led:
    pin.freq(1000)
    pin.duty_u16(0)

# create a dictionary of supported colors and their respective rgb values
# the values are in 8-bit format (0-255 or 0x00 to 0xFF)
color_dict = {
    "RED": (0xFF, 0x00, 0x00),
    "GREEN": (0x00, 0xFF, 0x00),
    "BLUE":(0x00, 0x00, 0xFF),
    "CYAN": (0x00, 0xFF, 0xFF),
    "MAGENTA": (0xFF, 0x00, 0xFF),
    "YELLOW":(0xFF, 0xFF, 0x00),
    "ORANGE": (0xFF, 0xA5, 0x00),
    "WHITE":(0xFF, 0xFF, 0xFF),
    "OFF": (0x00, 0x00, 0x00)
}

# gamma correction value used to compensate for non-linearility of human vision
# Based on https://cdn-learn.adafruit.com/downloads/pdf/led-tricks-gamma-correction.pdf
gamma = 2.8

def convert_rgb_to_analog(rgb, gamma):
    rgb = tuple(x / 0xFF for x in rgb) # normalize rgb values so they are between 0 and 1
    rgb = tuple(x ** gamma for x in rgb) # apply gamma correction
    rgb = tuple(int(round(x * 65535)) for x in rgb) # convert to 16-bit analog value
    return rgb

while True:
    color = input("Please chose a color (" + ", ".join(sorted(color_dict.keys())) + "): ")

    try:
        rgb_values = color_dict[color.upper()]
        analog_values = convert_rgb_to_analog(rgb_values, gamma) 
        for led_pin, analog_value in zip(rgb_led, analog_values):
            led_pin.duty_u16(analog_value)
    except KeyError:
        print(f"'{color}' is not a valid color.")
