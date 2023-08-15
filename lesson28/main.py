import network
import utime as time
from umachine import Pin

# Custom modules
from tinyhttpserver import TinyHttpServer
from httphandlers import RequestHandler
from lcd1602 import LCD1602  # https://github.com/jobinpa/mycropython_1602_lcd_library
import secrets

# LCD pins
LCD_RS_PIN = 2
LCD_E_PIN = 3
LCD_DB_7_TO_4_PINS = [7, 6, 5, 4]
LCD_RW_PIN = 1

# LED pins
RED_LED = 18
GREEN_LED = 19
BLUE_LED = 20

def get_wifi_status(wifi: network.WLAN) -> str:
    status = wifi.status()
    if status == network.STAT_IDLE:
        return "IDLE"
    elif status == network.STAT_CONNECTING:
        return "CONNECTING"
    elif status == network.STAT_WRONG_PASSWORD:
        return "WRONG_PASSWORD"
    elif status == network.STAT_NO_AP_FOUND:
        return "NO_AP_FOUND"
    elif status == network.STAT_CONNECT_FAIL:
        return "CONNECT_FAIL"
    elif status == network.STAT_GOT_IP:
        return "GOT_IP"
    else:
        return "UNKNOWN"

def main():
    error = None

    # Setup LEDs
    red_led = Pin(RED_LED, mode=Pin.OUT, value=0)
    green_led = Pin(GREEN_LED, mode=Pin.OUT, value=0)
    blue_led = Pin(BLUE_LED, mode=Pin.OUT, value=0)

    # Setup LCD
    lcd = LCD1602.begin_4bit(rs=LCD_RS_PIN, e=LCD_E_PIN, db_7_to_4=LCD_DB_7_TO_4_PINS, rw=LCD_RW_PIN)

    # Declare some variables
    wifi = None
    http_server = None

    try:
        # Connect to Wi-Fi
        print("Enabling WiFi..")
        lcd.clear()
        lcd.write_text(0, 0, "Enabling WiFi")

        wifi = network.WLAN(network.STA_IF)
        wifi.active(True)
        wifi.connect(secrets.WIFI_SSID, secrets.WIFI_PASSWORD)
        
        while not wifi.isconnected():
            print("Enabling WiFi..", get_wifi_status(wifi))
            lcd.write_text(0, 1, "{:<{}}".format(get_wifi_status(wifi), 16))
            time.sleep(1)

        wifi_info = wifi.ifconfig()
        
        print("WiFi connected!. IP address is ", wifi_info[0])
        lcd.clear()
        lcd.write_text(0, 0, "WiFi connected!")
        lcd.write_text(0, 1, str(wifi_info[0]))

        # Start HTTP server
        request_handler = RequestHandler(red_led, green_led, blue_led)
        http_server = TinyHttpServer(wifi_info[0], 80, request_handler)
        http_server.start()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        error = e
    finally:
        # Turn off all LEDs
        red_led.off()
        green_led.off()
        blue_led.off()

        # Shutdown HTTP server
        if http_server is not None:
            http_server.stop()
            http_server = None

        # Disconnect Wi-Fi
        if wifi is not None:
            print("Disabling WiFi...")
            lcd.clear()
            lcd.write_text(0, 0, "Disabling WiFi")

            wifi.disconnect()
            while wifi.isconnected():
                time.sleep(1)
            wifi.active(False)

        print("Program ended") if error is None else print("Program ended with error: ", error)
        lcd.clear()
        lcd.write_text(0, 0, "Program ended")
        if error is not None:
            lcd.write_text(0, 1, str(error))


if __name__ == "__main__":
    main()
