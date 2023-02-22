# Lesson: https://youtu.be/P1dzHNgAtvg
from machine import Pin
import utime

LED01_RED = Pin(1, Pin.OUT)
LED02_BLUE = Pin(2, Pin.OUT)
LED03_GREEN = Pin(3, Pin.OUT)
LED04_ORANGE = Pin(4, Pin.OUT)
LED05_RED = Pin(5, Pin.OUT)
LED06_BLUE = Pin(6, Pin.OUT)
LED07_GREEN = Pin(7, Pin.OUT)
LED08_ORANGE = Pin(8, Pin.OUT)
LED09_RED = Pin(9, Pin.OUT)
LED10_BLUE = Pin(10, Pin.OUT)
LED11_GREEN = Pin(11, Pin.OUT)
LED12_ORANGE = Pin(12, Pin.OUT)

ALL_LEDS = [
    LED01_RED, LED02_BLUE, LED03_GREEN, LED04_ORANGE,
    LED05_RED, LED06_BLUE, LED07_GREEN, LED08_ORANGE,
    LED09_RED, LED10_BLUE, LED11_GREEN, LED12_ORANGE
]

ALL_RED_LEDS = [LED01_RED, LED05_RED, LED09_RED]
ALL_BLUE_LEDS = [LED02_BLUE, LED06_BLUE, LED10_BLUE]
ALL_GREEN_LEDS = [LED03_GREEN, LED07_GREEN, LED11_GREEN]
ALL_ORANGE_LEDS = [LED04_ORANGE, LED08_ORANGE, LED12_ORANGE]

def pattern1():
    # Turn each led on then off from left to right
    for i in range(0, len(ALL_LEDS)):
        ALL_LEDS[i].on()
        utime.sleep(0.05)
        ALL_LEDS[i].off()

    # Turn each led on then off from right to left
    for i in reversed(range(0, len(ALL_LEDS))):
        ALL_LEDS[i].on()
        utime.sleep(0.05)
        ALL_LEDS[i].off()

def pattern2():
    # Turn each led on starting from left
    for i in range(0, len(ALL_LEDS)):
        ALL_LEDS[i].on()
        utime.sleep(0.05)

    # Turn each led off starting from left
    for i in range(0, len(ALL_LEDS)):
        ALL_LEDS[i].off()
        utime.sleep(0.05)

    # Turn each led on starting from right
    for i in reversed(range(0, len(ALL_LEDS))):
        ALL_LEDS[i].on()
        utime.sleep(0.05)

    # Turn each led off starting from right
    for i in reversed(range(0, len(ALL_LEDS))):
        ALL_LEDS[i].off()
        utime.sleep(0.05)


def pattern3():
    groups = [ALL_RED_LEDS, ALL_BLUE_LEDS, ALL_GREEN_LEDS, ALL_ORANGE_LEDS]

    # For each group (color) of leds
    for g in groups:
        # Turn all leds in the group on
        for i in range(0, len(g)):
            g[i].on()

        utime.sleep(0.15)

        # Turn all leds in the group off
        for i in range(0, len(g)):
            g[i].off()

# Main program
while True:
    for i in range(0, 4):
        pattern3()
        
    for i in range(0, 2):
        pattern1()

    for i in range(0, 4):
        pattern3()

    pattern2()
