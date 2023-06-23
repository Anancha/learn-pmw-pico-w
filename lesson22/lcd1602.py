# Adaptation of http://wiki.sunfounder.cc/images/8/87/LCD1602_for_Raspberry_Pi.zip

import utime as time
from machine import Pin

class LCD:
    # commands
    LCD_CLEARDISPLAY         = 0x01
    LCD_RETURNHOME           = 0x02
    LCD_ENTRYMODESET         = 0x04
    LCD_DISPLAYCONTROL       = 0x08
    LCD_CURSORSHIFT          = 0x10
    LCD_FUNCTIONSET          = 0x20
    LCD_SETCGRAMADDR         = 0x40
    LCD_SETDDRAMADDR         = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT           = 0x00
    LCD_ENTRYLEFT            = 0x02
    LCD_ENTRYSHIFTINCREMENT  = 0x01
    LCD_ENTRYSHIFTDECREMENT  = 0x00

    # flags for display on/off control
    LCD_DISPLAYON            = 0x04
    LCD_DISPLAYOFF           = 0x00
    LCD_CURSORON             = 0x02
    LCD_CURSOROFF            = 0x00
    LCD_BLINKON              = 0x01
    LCD_BLINKOFF             = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE          = 0x08
    LCD_CURSORMOVE           = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE          = 0x08
    LCD_CURSORMOVE           = 0x00
    LCD_MOVERIGHT            = 0x04
    LCD_MOVELEFT             = 0x00

    # flags for function set
    LCD_8BITMODE             = 0x10
    LCD_4BITMODE             = 0x00
    LCD_2LINE                = 0x08
    LCD_1LINE                = 0x00
    LCD_5x10DOTS             = 0x04
    LCD_5x8DOTS              = 0x00

    def __init__(self, pin_rs=27, pin_e=22, pins_db=[25, 24, 23, 18]):
        self.pin_rs = Pin(pin_rs, Pin.OUT)
        self.pin_e = Pin(pin_e, Pin.OUT)
        self.pins_db = [Pin(pin, Pin.OUT) for pin in pins_db]
        
        self.numcols = 16
        self.numrows = 2

        self.custom_char_map = { }

        self.write4bits(0x33) # initialization
        self.write4bits(0x32) # initialization
        self.write4bits(0x28) # 2 line 5x7 matrix
        self.write4bits(0x0C) # turn cursor off 0x0E to enable cursor
        self.write4bits(0x06) # shift cursor right

        self.displaycontrol = self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF

        self.displayfunction = self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_5x8DOTS
        self.displayfunction |= self.LCD_2LINE

        """ Initialize to default text direction (for romance languages) """
        self.displaymode =  self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode) #  set the entry mode

        self.clear()

    def home(self):
        self.write4bits(self.LCD_RETURNHOME) # set cursor position to zero
        time.sleep_us(3000) # this command takes a long time!
    
    def clear(self):
        self.write4bits(self.LCD_CLEARDISPLAY) # command to clear display
        time.sleep_us(3000)    # 3000 microsecond sleep, clearing the display takes a long time

    def setCursor(self, col, row):
        self.row_offsets = [ 0x00, 0x40, 0x14, 0x54 ]

        if ( row > self.numrows ): 
            row = self.numrows - 1 # we count rows starting w/0

        self.write4bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))

    def noDisplay(self): 
        # Turn the display off (quickly)
        self.displaycontrol &= ~self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def display(self):
        # Turn the display on (quickly)
        self.displaycontrol |= self.LCD_DISPLAYON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def noCursor(self):
        # Turns the underline cursor on/off
        self.displaycontrol &= ~self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def cursor(self):
        # Cursor On
        self.displaycontrol |= self.LCD_CURSORON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def noBlink(self):
        # Turn on and off the blinking cursor
        self.displaycontrol &= ~self.LCD_BLINKON
        self.write4bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def DisplayLeft(self):
        # These commands scroll the display without changing the RAM
        self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT)

    def scrollDisplayRight(self):
        # These commands scroll the display without changing the RAM
        self.write4bits(self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT);

    def leftToRight(self):
        # This is for text that flows Left to Right
        self.displaymode |= self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode);

    def rightToLeft(self):
        # This is for text that flows Right to Left
        self.displaymode &= ~self.LCD_ENTRYLEFT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def autoscroll(self):
        # This will 'right justify' text from the cursor
        self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def noAutoscroll(self): 
        # This will 'left justify' text from the cursor
        self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.write4bits(self.LCD_ENTRYMODESET | self.displaymode)

    def zfill(self, binary_string, length):
        if len(binary_string) >= length:
            return binary_string
        else:
            padding_length = length - len(binary_string)
            padding = '0' * padding_length
            return padding + binary_string

    def write4bits(self, bits, char_mode=False):
        # Send command to LCD
        time.sleep_us(1000) # 1000 microsecond sleep
        bits=self.zfill(bin(bits)[2:], 8)
        self.pin_rs.value(char_mode)

        for pin in self.pins_db:
            pin.value(False)

        for i in range(4):
            if bits[i] == "1":
                self.pins_db[i].value(True)

        self.pulseEnable()

        for pin in self.pins_db:
            pin.value(False)

        for i in range(4,8):
            if bits[i] == "1":
                self.pins_db[i-4].value(True)

        self.pulseEnable()

    def pulseEnable(self):
        self.pin_e.value(False)
        time.sleep_us(1)        # 1 microsecond pause - enable pulse must be > 450ns 
        self.pin_e.value(True)
        time.sleep_us(1)        # 1 microsecond pause - enable pulse must be > 450ns 
        self.pin_e.value(False)
        time.sleep_us(1)        # commands need > 37us to settle

    def createChar(self, char, location, bitmap):
        if location < 0 or location > 7:
            raise(ValueError("Custom character location must be between 0 and 7."))
        
        if len(bitmap) != 8:
            raise(ValueError("Character bitmap must have exactly 8 bytes, each byte representing a 5 pixels row."))
        
        # Send command to write char to CGRAM
        self.write4bits(self.LCD_SETCGRAMADDR |  (location << 3))

        # Write character to CGRAM
        for byte in bitmap:
            self.write4bits(byte, True)

        # Add custom char to map
        self.custom_char_map[char] = location

    def writeChar(self, char):
        charcode = self.custom_char_map[char] if char in self.custom_char_map else ord(char)
        self.write4bits(charcode,True)

    def write(self, col, row, str):
        # Make sure col and row are within bounds
        col = min(max(col, 0), self.numcols-1)
        row = min(max(row, 0), self.numrows-1)

        # Move cursor to desired position
        self.setCursor(col, row)

        # Write string
        for chr in str:
            self.writeChar(chr)

    def message(self, text):
        # Send string to LCD. Newline wraps to second line
        for chr in text:
            if chr == '\n':
                self.write4bits(0xC0) # next line
            else:
                self.writeChar(chr)
