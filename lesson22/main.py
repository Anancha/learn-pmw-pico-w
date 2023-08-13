import sys
import utime as time
import dht
from display import Display
from machine import Pin

# https://github.com/jobinpa/mycropython_1602_lcd_library
from lcd1602 import LCD1602

BTN_TEMP_UNIT_TOGGLE_PIN = 15
SENSOR_PIN = 16

LCD_RS_PIN = 2
LCD_E_PIN = 3
LCD_DB_7_TO_4_PINS = [7, 6, 5, 4]
LCD_RW_PIN = 1


class Program:
    def __init__(
        self,
        btn_temp_unit_toggle_pin,
        sensor_pin,
        is_celsius=True,
        button_debounce_ms=100,
        sensor_read_interval_ms=2000,
    ):
        # When false, the unit is Fahrenheit.
        self._is_celsius = is_celsius

        # Setup the button used to switch between Celsius and Fahrenheit.
        # Use an interrupt to detect when the button is pushed instead of polling
        # the button state in the main loop.
        self._btn_temp_unit_toggle = Pin(btn_temp_unit_toggle_pin, Pin.IN, Pin.PULL_UP)
        self._btn_temp_unit_toggle.irq(trigger=Pin.IRQ_RISING, handler=self._on_btn_cf_deg_toggle_interrupt)
        self._btn_temp_unit_toggle_last_event_on = 0  # Timestamp

        # Setup button software debounce. We ignore button events
        # occurring within the debounce period.
        self._button_debounce_ms = button_debounce_ms

        # Setup the DHT11 sensor. We use the DHT11 sensor module from Elegoo.
        # This module has a different pinout and comes with a pull-up resistor
        # integrated on the module board. No need to activate PIN's internal pull-up.
        # Datasheet: https://download.elegoo.com/?t=Mega_2560_The_Most_Complete_Starter_Kit
        self._sensor = dht.DHT11(Pin(sensor_pin, Pin.IN))
        self._sensor_last_read_on = 0  # Timestamp
        self._sensor_read_interval_ms = sensor_read_interval_ms
        self._sensor_error = None

        # Initialize temperature and humidity to 0
        self._temp_celsius = 0
        self._humidity = 0

        # Indicates whether the display should be updated
        self._should_update_display = False

        # Not running until run() is called
        self._is_running = False

        # Setup the LCD display
        lcd = LCD1602.begin_4bit(rs=LCD_RS_PIN, e=LCD_E_PIN, db_7_to_4=LCD_DB_7_TO_4_PINS, rw=LCD_RW_PIN)

        # Add and map degree symbol to LCD custom character map at position 0
        # The LCD has 8 custom characters, from 0 to 7
        # The following tool can be used to create custom characters
        # https://maxpromer.github.io/LCD-Character-Creator/
        lcd.create_character(0, [0b01110, 0b01110, 0b01110, 0b00000, 0b00000, 0b00000, 0b00000, 0b00000])
        lcd.map_character(chr(176), 0)

        self._lcd = Display(lcd)

    def _on_btn_cf_deg_toggle_interrupt(self, pin):
        # This code is executed each time the Celsius/Fahrenheit button is pushed.
        # We ignore interrupt requests that occur within the debounce period.
        current_time = time.ticks_ms()
        elapsed = abs(time.ticks_diff(current_time, self._btn_temp_unit_toggle_last_event_on))
        if elapsed > self._button_debounce_ms:
            self._is_celsius = not self._is_celsius
            self._btn_temp_unit_toggle_last_event_on = current_time
            self._should_update_display = True
            self._serial_print(f"Temperature unit changed to {'Celsius' if self._is_celsius else 'Fahrenheit'}")

    def _read_sensor(self):
        try:
            self._sensor.measure()
            self._sensor_error = None
        except OSError as ex:
            if self._sensor_error is None:
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

    def _update_display(self):
        if self._sensor_error:
            self._lcd.update_sensor_error(self._sensor_error)
        else:
            unit = "C" if self._is_celsius else "F"
            unit_value = int(round(self._temp_celsius if self._is_celsius else (self._temp_celsius * 9 / 5) + 32))
            self._lcd.update_sensor_values(unit_value, unit, self._humidity)

        self._should_update_display = False

    def _serial_print(self, msg):
        sys.stdout.write(f"{time.ticks_ms()} {msg}\n")

    def run(self):
        if self._is_running:
            return

        self._is_running = True
        self._should_update_display = True

        try:
            while self._is_running:
                current = time.ticks_ms()
                elapsed_since_last_sensor_read = abs(time.ticks_diff(current, self._sensor_last_read_on))
                if elapsed_since_last_sensor_read >= self._sensor_read_interval_ms:
                    self._read_sensor()
                    self._sensor_last_read_on = current

                if self._should_update_display:
                    self._update_display()
                self._lcd.refresh()

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
