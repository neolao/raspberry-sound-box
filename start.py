import RPi.GPIO as GPIO
import subprocess
from json import load as loadJson
from pathlib import Path
from pn532 import *
import time
import os
import signal

if __name__ == '__main__':
    try:
        #pn532 = PN532_SPI(debug=False, reset=20, cs=4)
        pn532 = PN532_SPI(debug=False, reset=16, cs=4)
        #pn532 = PN532_I2C(debug=False, reset=20, req=16)
        #pn532 = PN532_UART(debug=False, reset=20)

        ic, ver, rev, support = pn532.get_firmware_version()
        print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

        # Configure PN532 to communicate with MiFare cards
        pn532.SAM_configuration()

        print('Waiting for RFID/NFC card...')
        lastUidString = ''
        process = None
        recordProcess = None
        while True:
            # Check if a card is available to read
            #print('.')
            uid = pn532.read_passive_target(timeout=0.5)

            # Try again if no card is available.
            if uid is None:
                continue

            uidString = ''.join(format(x, '02x') for x in uid)
            if uidString == lastUidString and process.poll() is None:
                continue

            # Check the recorder card
            if uidString == "70cddb2a":
                if recordProcess is not None:
                    recordProcess.terminate()
                    subprocess.run(["mpg123", "sounds/enregistre.mp3"])
                    recordProcess = None
                    time.sleep(1)
                    subprocess.run(["aplay", "record.wav"])
                    time.sleep(1)
                else:
                    subprocess.run(["mpg123", "sounds/pret-a-enregistrer.mp3"])
                    recordProcess = subprocess.Popen(["/usr/bin/arecord", "-D", "hw:1,0", "-f", "S32_LE", "-r", "16000", "-c", "2", "record.wav"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=os.setsid, shell=False)
                continue

            # Check if a command exists
            commandFilePath = "./data/" + uidString + ".json"
            if not Path(commandFilePath).is_file():
                print("Unknown tag:", uidString)
                subprocess.run(["mpg123", "sounds/je-ne-connais-pas-cette-carte.mp3"])
                continue

            #print('Found card with UID:', uidString, [hex(i) for i in uid])
            lastUidString = uidString
            if process is not None:
                process.terminate()

            with open(commandFilePath) as commandString:
                command = loadJson(commandString)
                process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=False)
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
