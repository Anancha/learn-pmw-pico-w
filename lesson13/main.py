import time
from machine import ADC, Pin, PWM

# Each tuples has 3 values representing the 3 RGB color channels
# First value is for RED, second value is for BLUE and third value is for GREEN
POT_PINS = (26, 27, 28)
POT_MIN_VALUES = (160, 160, 160)
POT_MAX_VALUES = (65535, 65535, 65535)
LED_PINS = (11, 12, 13)


class RGBLedProgram:
    def __init__(self, pot_pins, led_pins, pot_min_values=(0, 0, 0),
                 pot_max_values=(65535, 65535, 65535), gamma=2.8):
        # Setup potentiometer pins
        self._pot_pins = tuple(ADC(pin) for pin in pot_pins)
        self._pot_min_values = pot_min_values
        self._pot_max_values = pot_max_values

        # Setup led pins
        self._leds_pins = tuple(PWM(Pin(pin)) for pin in led_pins)
        for pin in self._leds_pins:
            pin.freq(1000)
            pin.duty_u16(0)

        # Setup gamma correction factor
        # Based on https://cdn-learn.adafruit.com/downloads/pdf/led-tricks-gamma-correction.pdf
        self._gamma = gamma

        # Scale analog in values to RGB values (0-255) using a linear function.
        # We calculate the slope and y-intercept of the function for each potentiometer,
        # as each potentiometer may have his own min/max values.
        self._analog_to_rgb_slopes, self._analog_to_rgb_intercepts = zip(*(
            self._calculate_scaling_slope_and_intercept(minval, maxval, 0, 255)
            for minval, maxval in zip(self._pot_min_values, self._pot_max_values)))

        # Initialize RGB values to OFF.
        self._rgb = (0, 0, 0)

        # Not running until run() is called
        self._is_running = False

    def _calculate_scaling_slope_and_intercept(self, raw_min, raw_max, scaled_min, scaled_max):
        slope = (scaled_max - scaled_min) / (raw_max - raw_min)
        intercept = scaled_min - (slope * raw_min)
        return (slope, intercept)

    def _convert_rgb_to_analog(self, rgb):
        # Normalize rgb values so they are between 0 and 1
        # We do this by dividing each RGB value by 255, which is the max value
        # that can be represented by 8 bits.
        result = tuple(x / 0xFF for x in rgb)

        # Apply gamma correction
        # Based on https://cdn-learn.adafruit.com/downloads/pdf/led-tricks-gamma-correction.pdf
        result = tuple(x ** self._gamma for x in result)

        # Convert to 16-bits analog values
        result = tuple(int(round(x * 65535)) for x in result)
        return result

    def _read_pot_values(self):
        # Read values from potentiometers
        # Make sure values are within allowed min/max values
        pot_vals = tuple(min(max(pot.read_u16(), minval), maxval) for pot, minval, maxval in
                         zip(self._pot_pins, self._pot_min_values, self._pot_max_values))

        # Scale pot analog values to RGB values (0-255) using a linear function
        new_rgb_vals = tuple(slope * analog_val + intercept for analog_val, slope, intercept in
                             zip(pot_vals, self._analog_to_rgb_slopes, self._analog_to_rgb_intercepts))

        # Analog reads may be noisy. To prevent the RGB LED from flickering,
        # we apply the following smoothing algorithm:
        #  1. Calculate the difference between current and previous RGB values
        #  2. Add 15% of the differences to the previous RGB values
        # Note: Because of this smoothing algorithm, the RGB values may not be integers.
        # This is OK. The get_rgb() method will round the values before returning them.
        rgb_deltas = tuple(new - previous for new, previous in zip(new_rgb_vals, self._rgb))
        self._rgb = tuple(previous + delta * 0.15 for previous, delta in
                                 zip(self._rgb, rgb_deltas))

        return self.get_rgb()

    def _set_led_color(self, rgb):
        analog_values = self._convert_rgb_to_analog(rgb)
        for led_pin, analog_value in zip(self._leds_pins, analog_values):
            led_pin.duty_u16(analog_value)

    def get_rgb(self):
        # Because of the smoothing algorithm, the RGB values may not be integers.
        # Round and rconvet to int before returning.
        return tuple(int(round(x)) for x in self._rgb)

    def run(self):
        if self._is_running:
            return

        self._is_running = True

        try:
            while self._is_running:
                rgb = self._read_pot_values()
                self._set_led_color(rgb)
                print(f"\rRGB={self.get_rgb()}", end=' ')
                time.sleep(0.01)
        finally:
            # Program has been stopped by user
            self._set_led_color((0, 0, 0))

    def stop(self):
        self._is_running = False


if __name__ == "__main__":
    program = RGBLedProgram(POT_PINS, LED_PINS, pot_min_values=POT_MIN_VALUES,
                            pot_max_values=POT_MAX_VALUES)
    try:
        program.run()
    except KeyboardInterrupt:
        # Code to handle keyboard interrupt
        program.stop()
        print("Program stopped by user")
