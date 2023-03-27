# Lesson: https://youtu.be/mS4YcJ0FcOU
from time import sleep
from machine import PWM
from helpers import *

pot_reader = PotReader(pot_pin_number=26, analog_value_range=(176, 65231),
                       scaled_value_range=(0, 3.3), sample_size=100, round_digits=3)

analogOut = PWM(Pin(15))
analogOut.freq(1000)
analogOut.duty_u16(0)

while True:
    (convertedValue, rawValue) = pot_reader.read()
    analogOutValue = max(0, int(convertedValue * 65535.0 / 3.3))
    print("Analog in: %s | Converted value: %sv | Analog out: %s" % (rawValue, convertedValue, analogOutValue))
    analogOut.duty_u16(analogOutValue)