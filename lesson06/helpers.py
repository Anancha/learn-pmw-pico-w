from machine import Pin, ADC


def init_led(pin, is_on=False):
    led = Pin(pin, Pin.OUT)
    led.value(is_on)
    return led


def is_valid_range(value):
    if not isinstance(value, (list, tuple)):
        return False

    if len(value) != 2:
        return False

    if not all(isinstance(x, (int, float)) for x in value):
        return False

    return True


def is_valid_gpio_pin_list(value, number_of_pins=None):
    if not isinstance(value, (list)):
        return False

    if not all(isinstance(x, (int)) for x in value):
        return False

    if isinstance(number_of_pins, int):
        if not number_of_pins >= 1:
            raise ValueError("number_of_pins must be greater than or equal to 1")

        if len(value) != number_of_pins:
            return False

    return True


class PotReader():
    def __init__(self, pot_pin_number, analog_value_range, scaled_value_range,
                 sample_size=1, round_digits=0):
        self._pot_pin = ADC(pot_pin_number)
        self._round_digits = min(0, round_digits)

        if not is_valid_range(analog_value_range):
            raise ValueError("analog_value_range must contain exactly 2 numbers")

        if not is_valid_range(scaled_value_range):
            raise ValueError("scaled_value_range must contain exactly 2 numbers")

        min_analog_value, max_analog_value = min(analog_value_range), max(analog_value_range)
        min_scaled_value, max_scaled_value = min(scaled_value_range), max(scaled_value_range)

        self._scale_formula_slope = (max_scaled_value - min_scaled_value) / (max_analog_value - min_analog_value)
        self._scale_formula_yintercept = min_scaled_value - (self._scale_formula_slope * min_analog_value)

        self._samples = [0 for i in range(min(1, sample_size))]
        self._samples_idx = 0

    def _scale_analog_value(self, analog_value):
        return self._scale_formula_slope * analog_value + self._scale_formula_yintercept

    def _read_buffered_analog_value(self):
        analog_value = self._pot_pin.read_u16()
        self._samples[self._samples_idx] = analog_value
        self._samples_idx = (self._samples_idx + 1) % len(self._samples)
        return sum(self._samples) / len(self._samples)

    def read(self):
        analog_value = self._read_buffered_analog_value()
        scaled_value = round(self._scale_analog_value(analog_value), self._round_digits)
        return (scaled_value, analog_value)


class CancellationToken:
    def __init__(self):
        self.is_cancellation_requested = False

    def cancel(self):
        self.is_cancellation_requested = True
