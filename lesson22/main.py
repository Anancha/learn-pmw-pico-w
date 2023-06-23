import sys
import utime as time
import dht
from machine import Pin
from lcd1602 import LCD

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

        # Setup the LCD display
        self._lcd = LCD(pin_e=3, pin_rs=2, pins_db=[7,6,5,4])

        # Add degree symbol to LCD custom character map at position 0
        # The LCD has 8 custom characters, from 0 to 7
        # The following tool can be used to create custom characters
        # https://maxpromer.github.io/LCD-Character-Creator/
        self._lcd.createChar(chr(176), 0, [
            0b01110,
            0b01110,
            0b01110,
            0b00000,
            0b00000,
            0b00000,
            0b00000,
            0b00000
        ])

    def _on_btn_cf_deg_toggle_interrupt(self, pin):
        # This code is executed each time the Celsius/Fahrenheit button is pushed.
        # We ignore interrupt requests that occur within the debounce period.
        if (time.ticks_ms() >= self._btn_temp_unit_toggle_ignore_irqs_until):
            self._is_celsius = not self._is_celsius
            self._btn_temp_unit_toggle_ignore_irqs_until = time.ticks_ms() + self._button_debounce_ms
            self._should_update_display = True
            self._serial_print(f"Temperature unit changed to {'Celsius' if self._is_celsius else 'Fahrenheit'}")

    def _read_sensor(self):
        try:
            self._sensor.measure()
            self._sensor_error = None
        except OSError as ex:
            self._sensor_error = ex
            self._should_update_display = True
            self._serial_print(f"SENSOR ERROR: {ex}")
            return

        temp = self._sensor.temperature()
        humidity = self._sensor.humidity()
        self._serial_print(f"SENSOR READ: Temperature={temp}  Humidity={humidity}")

        # No need to update the display unless something has changed
        if temp != self._temp_celsius or humidity != self._humidity:
            self._temp_celsius = temp
            self._humidity = humidity
            self._should_update_display = True

    def _refresh_display(self):
        unit = "C" if self._is_celsius else "F"
        unit_value = int(round(self._temp_celsius if self._is_celsius else (self._temp_celsius * 9 / 5) + 32))

        if self._sensor_error:
            self._lcd_print(0, 0, "SENSOR ERROR!")
            self._lcd_print(0, 1, str(self._sensor_error))
        else:
            self._lcd_print(0, 0, f"Temp: {unit_value}{chr(176)}{unit}")
            self._lcd_print(0, 1, f"Humidity: {self._humidity}%")

        self._should_update_display = False

    def _lcd_print(self, col, row, msg):
        while len(msg) < self._lcd.numcols:
            msg += " "
        
        if len(msg) > self._lcd.numcols:
            msg = msg[:self._lcd.numcols]
        
        self._lcd.write(col, row, msg)

    def _serial_print(self, msg):
        sys.stdout.write(f'{msg}\n')

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
