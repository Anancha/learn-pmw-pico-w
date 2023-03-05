# Lesson: https://youtu.be/mS4YcJ0FcOU
import _thread
import utime
from helpers import *


class LedPattern:
    def __init__(self, led_pin_numbers, frequency_range):
        if not is_valid_gpio_pin_list(led_pin_numbers):
            raise ValueError("led_pin_numbers must be a list of integers")
        self.led_pins = [init_led(pin) for pin in led_pin_numbers]

        self.min_frequency, self.max_frequency = min(frequency_range), max(frequency_range)
        self.frequency = self.min_frequency

    def set_frequency_from_ratio(self, ratio):
        ratio = max(0, min(1, ratio))  # Make sure ratio is a value between 0 and 1
        self.frequency = self.min_frequency + (ratio * (self.max_frequency - self.min_frequency))

    def _calculate_delay_per_led(self):
        pattern_cycle_time = 1.0 / self.frequency  # time for one full pattern cycle based on frequency
        num_leds = len(self.led_pins)
        num_on_off_transitions = 2  # each LED is turned on and off twice per pattern cycle
        time_per_on_off_transition = pattern_cycle_time / (num_leds * num_on_off_transitions)
        return time_per_on_off_transition

    def execute_pattern(self, cancellation_token=CancellationToken()):
        while not cancellation_token.is_cancellation_requested:
            # Turn each led on then off in one direction
            for i in range(len(self.led_pins)):
                self.led_pins[i].on()
                utime.sleep(self._calculate_delay_per_led())
                self.led_pins[i].off()

            # Turn each led on then off in the other direction
            for i in reversed(range(len(self.led_pins))):
                self.led_pins[i].on()
                utime.sleep(self._calculate_delay_per_led())
                self.led_pins[i].off()


class LEDIndicator:
    def __init__(self, safe_level_led_pin_number, warning_level_led_pin_number,
                 critical_level_led_pin_number, warning_level_threshold,
                 critical_level_threshold):
        if not isinstance(safe_level_led_pin_number, (int)):
            raise ValueError('safe_level_led_pin_number must be an integer')

        if not isinstance(warning_level_led_pin_number, (int)):
            raise ValueError('warning_level_led_pin_number must be an integer')

        if not isinstance(critical_level_led_pin_number, (int)):
            raise ValueError('critical_level_led_pin_number must be an integer')

        if not isinstance(warning_level_threshold, (int, float)):
            raise ValueError("warning_level_threshold must be a numeric value")

        if not isinstance(critical_level_threshold, (int, float)):
            raise ValueError("critical_level_threshold must be a numeric value")

        if warning_level_threshold >= critical_level_threshold:
            raise ValueError("warning_level_threshold must be less than critical_level_threshold")

        self._safe_level_led = init_led(safe_level_led_pin_number)
        self._warning_level_led = init_led(warning_level_led_pin_number)
        self._critical_level_led = init_led(critical_level_led_pin_number)
        self._warning_level_threshold = warning_level_threshold
        self._critical_level_threshold = critical_level_threshold

    def update_leds(self, level):
        if level < self._warning_level_threshold:
            self._safe_level_led.on()
            self._warning_level_led.off()
            self._critical_level_led.off()
        elif level < self._critical_level_threshold:
            self._safe_level_led.off()
            self._warning_level_led.on()
            self._critical_level_led.off()
        else:
            self._safe_level_led.off()
            self._warning_level_led.off()
            self._critical_level_led.on()


led_pattern = LedPattern(led_pin_numbers=[1, 2, 3, 4, 5], frequency_range=(1, 5))

pot_reader = PotReader(pot_pin_number=26, analog_value_range=(300, 65535),
                       scaled_value_range=(0, 100), sample_size=100)

led_indicator = LEDIndicator(safe_level_led_pin_number=6, warning_level_led_pin_number=7,
                                  critical_level_led_pin_number=8, warning_level_threshold=80,
                                  critical_level_threshold=95)

# Run the led patter on a second thread
_thread.start_new_thread(led_pattern.execute_pattern, (CancellationToken(),))

while True:
    (convertedValue, rawValue) = pot_reader.read()
    led_pattern.set_frequency_from_ratio(convertedValue/100.0)
    led_indicator.update_leds(convertedValue)
    print("Analog value: %s | Converted value: %s" % (rawValue, convertedValue))
