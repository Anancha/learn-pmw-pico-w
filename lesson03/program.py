# Lesson: https://youtu.be/C_xiDka0Nm0
from machine import Pin
import utime

LED_BIT1 = Pin(12, Pin.OUT)
LED_BIT2 = Pin(13, Pin.OUT)
LED_BIT3 = Pin(14, Pin.OUT)
LED_BIT4 = Pin(15, Pin.OUT)

BIT1_MASK = 0b0001
BIT2_MASK = 0b0010
BIT3_MASK = 0b0100
BIT4_MASK = 0b1000

DELAY = 1

def setLed(led, isOn):
    if (isOn):
        led.on()
    else:
        led.off()
    
# Main program
while True:
    for x in range(0, 16):
        setLed(LED_BIT1, x & BIT1_MASK)
        setLed(LED_BIT2, x & BIT2_MASK)
        setLed(LED_BIT3, x & BIT3_MASK)
        setLed(LED_BIT4, x & BIT4_MASK)
        utime.sleep(DELAY)
