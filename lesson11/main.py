# Lesson: https://youtu.be/MCo5nXAKyUU
import math
import utime
from machine import PWM, Pin, ADC

# initialize analog input pin (potentiometer)
pot = ADC(26)

# initialize analog output pin (led)
led_pin = PWM(Pin(13))
led_pin.freq(1000)
led_pin.duty_u16(0)

# keep only the first 8 bits of the 16 bits analog input value
# discarding the lower bits helps to reduce the noise in our readings
# this still gives us a range of 0 to 255, which means 0.012941 volts per step,
# which is more than enough for our purposes
adc_bits = 16
analog_in_significant_bits = 8
analog_in_discard_bits = adc_bits - analog_in_significant_bits

# define min/max values for analog input and output
(analog_in_min, analog_in_max) = (0, 2 ** analog_in_significant_bits - 1)
(analog_out_min, analog_out_max) = (0, 2 ** adc_bits - 1)

last_readings = [analog_in_min for i in range(5)]
next_reading_index = 0

while True:
    # replace the oldest reading with the newest reading from our potentiometer
    last_readings[next_reading_index] = pot.read_u16() >> analog_in_discard_bits
    next_reading_index = (next_reading_index + 1) % len(last_readings)
    
    # calculate average of all past readings. using a moving average helps to
    # mitigate the effects of sporadic spikes in our readings
    analog_in = int(round(sum(last_readings)/len(last_readings)))
    
    analog_out = analog_out_min + (analog_out_max - analog_out_min) * (math.exp((analog_in - analog_in_min) / (analog_in_max - analog_in_min)) - 1) / (math.e - 1)
    analog_out = int(round(analog_out))
        
    # set analog output
    led_pin.duty_u16(int(round(analog_out)))  
    
    # print analog input and output values
    print("Analog in: %s | Analog out: %s" % (analog_in, analog_out))

    utime.sleep(0.1)