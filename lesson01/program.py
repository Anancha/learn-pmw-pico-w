# Lesson: https://youtu.be/SL4_oU9t8Ss

from machine import Pin
import utime

led = Pin("LED", Pin.OUT)

while True:
    led.toggle()
    #led.on()
    #utime.sleep(0.25)
    #led.off()
    utime.sleep(0.014)