import sys
import utime as time
import dht
from machine import Pin

BTN_TEMP_UNIT_TOGGLE_PIN = 15
SENSOR_PIN = 16


class Program:
    def __init__(self, btn_temp_unit_toggle_pin, sensor_pin, is_celsius=True,
                 button_debounce_ms=50, sensor_read_interval_ms=2000):
        # When false, the unit is Fahrenheit.
        self._is_celsius = is_celsius

        # Setup the button used to switch between Celsius and Fahrenheit.
        # Use an interrupt to detect when the button is pushed instead of polling
        # the button state in the main loop.
        self._btn_temp_unit_toggle = Pin(btn_temp_unit_toggle_pin, Pin.IN, Pin.PULL_UP)
        self._btn_temp_unit_toggle.irq(trigger=Pin.IRQ_RISING, handler=self._on_btn_cf_deg_toggle_interrupt)
        self._btn_temp_unit_toggle_ignore_irqs_until = 0  # Timestamp

        # Setup button software debounce. We ignore interrupt request occurring
        # within the debounce period.
        self._button_debounce_ms = button_debounce_ms

        # Setup the DHT11 sensor. We use the DHT11 sensor module from Elegoo.
        # This module has a different pinout and comes with a pull-up resistor
        # integrated on the module board. No need to activate PIN's internal pull-up.
        # Datasheet: https://download.elegoo.com/?t=Mega_2560_The_Most_Complete_Starter_Kit
        self._sensor = dht.DHT11(Pin(sensor_pin, Pin.IN))
        self._sensor_next_read_not_before = 0  # Timestamp
        self._sensor_read_interval_ms = sensor_read_interval_ms
        self._sensor_error = None

        # Initialize temperature and humidity to 0
        self._temp_celsius = 0
        self._humidity = 0

        # Indicates whehter the display should be updated
        self._should_update_display = False

        # Not running until run() is called
        self._is_running = False

    def _on_btn_cf_deg_toggle_interrupt(self, pin):
        # This code is executed each time the Celsius/Fahrenheit button is pushed.
        # We ignore interrupt requests that occur within the debounce period.
        if (time.ticks_ms() >= self._btn_temp_unit_toggle_ignore_irqs_until):
            self._is_celsius = not self._is_celsius
            self._btn_temp_unit_toggle_ignore_irqs_until = time.ticks_ms() + self._button_debounce_ms
            self._should_update_display = True

    def _read_sensor(self):
        try:
            self._sensor.measure()
            self._sensor_error = None
        except OSError as ex:
            self._sensor_error = f"Failed to read sensor. {ex}"
            self._should_update_display = True
            return

        temp = self._sensor.temperature()
        humidity = self._sensor.humidity()

        # No need to update the display unless something has changed
        if temp != self._temp_celsius or humidity != self._humidity:
            self._temp_celsius = temp
            self._humidity = humidity
            self._should_update_display = True

    def _refresh_display(self):
        unit = "C" if self._is_celsius else "F"
        unit_value = int(round(self._temp_celsius if self._is_celsius else (self._temp_celsius * 9 / 5) + 32))

        if self._sensor_error:
            self._serial_print(self._sensor_error)
        else:
            self._serial_print(f"Temperature: {unit_value}{chr(176)}{unit}  Humidity: {self._humidity}%")

        self._should_update_display = False

    def _serial_print(self, msg):
        # 20230621: As @keithlohmeyer pointed out, msg:80 fills the remainder
        # of the 80 characters with blank spaces. There is no need to print a 
        # blank line to clear the previous message.
        ##sys.stdout.write("\r                                                                                ")
        sys.stdout.write(f"\r{msg:80}")

    def run(self):
        if self._is_running:
            return

        self._is_running = True
        self._should_update_display = True

        try:
            while self._is_running:
                if time.ticks_ms() >= self._sensor_next_read_not_before:
                    self._read_sensor()
                    self._sensor_next_read_not_before = time.ticks_ms() + self._sensor_read_interval_ms

                if self._should_update_display:
                    self._refresh_display()

                time.sleep(0.01)
        finally:
            self._serial_print("Program stopped by user")

    def stop(self):
        self._is_running = False


if __name__ == "__main__":
    program = Program(BTN_TEMP_UNIT_TOGGLE_PIN, SENSOR_PIN)
    try:
        program.run()
    except KeyboardInterrupt:
        # Code to handle keyboard interrupt
        program.stop()
