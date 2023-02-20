# Lesson: https://youtu.be/eGdrtikKc5U
from machine import Pin
import utime

LED = Pin(15, Pin.OUT)

DIT = 0.1             # Duration of a dit (short pulse) in seconds
DAH = DIT * 3         # Duration of a dah (long pulse) in seconds
CHAR_PAUSE = DIT * 3  # Duration of a pause between characters in seconds
WORD_PAUSE = DIT * 7  # Duration of a pause between words in seconds

MSG = "SOS"

# Encode a character into a sequence of dits and dahs
def encodeChar(c):
    if c == "S":
        return "..."  
    if c == "O":
       return "---" 
    raise ValueError('Support for character "' + c + '" is not implemented yet.')

# Write a character encoded as a sequence of dits and dahs
def writeEncodedChar(encodedChar):
    for pulse in encodedChar:
        print(pulse, end = '')
        LED.on()
        utime.sleep(DIT if pulse == "." else DAH)
        LED.off()
        utime.sleep(CHAR_PAUSE)

# Main program
while True:
    for c in MSG:
        writeEncodedChar(encodeChar(c))
    print()
    utime.sleep(WORD_PAUSE)
