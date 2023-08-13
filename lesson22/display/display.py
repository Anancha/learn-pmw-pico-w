from display.displayline import DisplayLine
from lcd1602 import LCD1602


class Display:
    def __init__(self, lcd1602: LCD1602, autoscroll_speed_ms: int = 2000):
        self._lcd = lcd1602
        self._lines = [DisplayLine(16, autoscroll_speed_ms), DisplayLine(16, autoscroll_speed_ms)]

    def update_sensor_values(self, temp: int, temp_unit: str, humidity_percent: int):
        self._lines[0].set_text(f"Temp: {int(temp)}{chr(176)}{temp_unit}")
        self._lines[1].set_text(f"Humidity: {humidity_percent}%")

    def update_sensor_error(self, error: Exception):
        self._lines[0].set_text("SENSOR ERROR!")
        self._lines[1].set_text(str(error))

    def refresh(self):
        for idx, line in enumerate(self._lines):
            if line.should_refresh():
                self._lcd.write_text(0, idx, line.get_text())
