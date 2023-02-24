# Lesson: https://youtu.be/ODWwErH_iGA
from machine import Pin, ADC
import utime

# Setup LED pins (GPIO 1 to 12)
leds =  []
for i in range(1, 13):
    led = Pin(i, Pin.OUT)
    led.off()
    leds.append(led)

# Setup potentiometer pin
POT = ADC(28)

# Setup min and max for analog and converted values
AMIN, AMAX, CMIN, CMAX = 640, 65535, 0, 100

# Calculate conversion formula's slope and y-intercept
SLOPE = (CMAX-CMIN) / (AMAX-AMIN)
YINTERCEPT = CMIN - (SLOPE * AMIN)

# Turn on LEDs based on converted value
# When value is 0, no LEDs are on
# When value is 100, all LEDs are on
def lightLeds(convertedValue):
    numLeds = round(convertedValue / CMAX * len(leds))
    for i in range(len(leds)):
        leds[i].value(i + 1 <= numLeds)
    
# Main program
while True:
    rawValue = POT.read_u16()
    convertedValue = CMAX - (SLOPE * rawValue + YINTERCEPT)
    lightLeds(convertedValue)
    print("Analog value: %s | Converted value: %s" % (rawValue, convertedValue))
    utime.sleep(0.5)

