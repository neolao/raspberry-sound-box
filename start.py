import RPi.GPIO as GPIO
import os
import subprocess

from pn532 import *


if __name__ == '__main__':
    try:
        pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        #pn532 = PN532_I2C(debug=False, reset=20, req=16)
        #pn532 = PN532_UART(debug=False, reset=20)

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        print('Waiting for RFID/NFC card...')
        lastUidString = ''
        process = None
        while True:
            # Check if a card is available to read
            #print('.')
            uid = pn532.read_passive_target(timeout=0.5)

            # Try again if no card is available.
            if uid is None:
                continue

            #print('Found card with UID:', [hex(i) for i in uid])
            uidString = ''.join(format(x, '02x') for x in uid)
            if uidString == lastUidString and process.poll() is None:
                continue

            lastUidString = uidString
            print('Found card with UID:', uidString, [hex(i) for i in uid])
            if process is not None:
                process.terminate()

            process = subprocess.Popen(["/usr/bin/aplay", "/home/pi/test.wav"], stdout=subprocess.PIPE, shell=False)
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
