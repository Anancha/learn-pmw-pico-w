# Lesson: https://youtu.be/yZkx-KWbATY
from time import sleep
from machine import PWM, Pin

# setup led as a tuple of 3 values (red pin, green pin, blue pin)
RGB_LED = tuple(PWM(Pin(x)) for x in (12, 11, 10))
for pin in RGB_LED:
    pin.freq(1000)
    pin.duty_u16(0)

# create a dictionary of supported colors and their respective rgb values
# the values are in 8-bit format (0-255 or 0x00 to 0xFF)
COLOR_DICT = {
    "RED": (0xFF, 0x00, 0x00),
    "GREEN": (0x00, 0xFF, 0x00),
    "BLUE": (0x00, 0x00, 0xFF),
    "CYAN": (0x00, 0xFF, 0xFF),
    "MAGENTA": (0xFF, 0x00, 0xFF),
    "YELLOW": (0xFF, 0xFF, 0x00),
    "ORANGE": (0xFF, 0xA5, 0x00),
    "WHITE": (0xFF, 0xFF, 0xFF),
    "OFF": (0x00, 0x00, 0x00)
}

# gamma correction value used to compensate for non-linearility of human vision
# Based on https://cdn-learn.adafruit.com/downloads/pdf/led-tricks-gamma-correction.pdf
GAMMA = 2.8


def convert_rgb_to_analog(rgb, gamma):
    rgb = tuple(x / 0xFF for x in rgb)  # normalize rgb values so they are between 0 and 1
    rgb = tuple(x ** gamma for x in rgb)  # apply gamma correction
    rgb = tuple(int(round(x * 65535)) for x in rgb)  # convert to 16-bit analog value
    return rgb


def read_color(message):
    while True:
        color = input(message).upper()
        if color in COLOR_DICT:
            return color
        print(f"ERROR! '{color}' is not a valid color.")


def read_positive_integer(message):
    while True:
        int_raw = input(message)

        try:
            int_parsed = int(int_raw)
            if int_parsed > 0:
                return int_parsed
        except ValueError:
            pass

        print(f"ERROR! '{int_raw}' is not a valid positive integer.")


def turn_off_led():
    for led_pin in RGB_LED:
        led_pin.duty_u16(0)


while True:
    print()
    number_of_colors = read_positive_integer("How many colors do you want to display? ")

    colors = []
    for i in range(1, number_of_colors + 1):
        print()
        colors.append(read_color(f"Please choose color {i} of {number_of_colors} (one of {', '.join(sorted(COLOR_DICT.keys()))}): "))

    print()
    print("Sequence complete!")
    print(' => '.join(colors))

    print()
    for i in range(5, 0, -1):
        print(f"Executing sequence in {i}s...")
        sleep(1)

    print()
    for c in colors:
        print(f"Displaying color {c}...")
        rgb_values = COLOR_DICT[c]
        analog_values = convert_rgb_to_analog(rgb_values, GAMMA)
        for led_pin, analog_value in zip(RGB_LED, analog_values):
            led_pin.duty_u16(analog_value)
        sleep(1)

    turn_off_led()
