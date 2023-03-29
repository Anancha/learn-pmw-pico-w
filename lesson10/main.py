# Lesson: https://youtu.be/mS4YcJ0FcOU
from time import sleep
from machine import PWM
from helpers import *

pot_reader = PotReader(pot_pin_number=26, analog_value_range=(192, 65535),
                       scaled_value_range=(0, 3.3), sample_size=100, round_digits=3)

analogOut1 = PWM(Pin(13))
analogOut1.freq(1000)
analogOut1.duty_u16(0)

analogOut2 = PWM(Pin(15))
analogOut2.freq(1000)
analogOut2.duty_u16(0)

while True:
    (convertedValue, rawValue) = pot_reader.read()
    
    analogOut1Value = max(0, int(convertedValue * 65535.0 / 3.3))
    analogOut1.duty_u16(analogOut1Value)
    
    analogOut2Value = max(0, int((3.3 - convertedValue) * 65535.0 / 3.3))
    analogOut2.duty_u16(analogOut2Value)
    
    print("Analog in: %s | Converted value: %sv | Analog out 1: %s | Analog out 2: %s" % (rawValue, convertedValue, analogOut1Value, analogOut2Value))