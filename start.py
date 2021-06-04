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
        subprocess.run(["mpg123", "sounds/je-suis-prete.mp3"])
        lastUidString = ''
        process = None
        recordProcess = None
        recordStep = 0
        while True:
            # Check if a card is available to read
            #print('.')
            uid = pn532.read_passive_target(timeout=0.5)

            # Try again if no card is available.
            if uid is None:
                continue

            uidString = ''.join(format(x, '02x') for x in uid)

            # Check the recorder card
            if uidString == "70cddb2a" and recordStep == 0:
                subprocess.run(["mpg123", "sounds/veuillez-me-montrer-la-carte-a-enregistrer.mp3"])
                recordStep = 1
                continue

            if recordStep == 1:
                subprocess.run(["mpg123", "sounds/l-enregistrement-demarre-dans-3-2-1.mp3"])
                recordProcess = subprocess.Popen(["/usr/bin/arecord", "-D", "hw:1,0", "-f", "S32_LE", "-r", "16000", "-c", "2", "data/" + uidString + ".wav"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=os.setsid, shell=False)
                recordStep = 2
                continue

            if recordStep == 2:
                recordProcess.terminate()
                recordProcess = None
                recordStep = 0
                subprocess.run(["mpg123", "sounds/enregistre.mp3"])
                time.sleep(2)
                continue

            # Stop process
            if uidString == "4a14b71e":
                print("STOP")
                if process is not None:
                    process.terminate()
                time.sleep(2)
                continue

            if uidString == lastUidString and process.poll() is None:
                continue

            print('Found card with UID:', uidString, [hex(i) for i in uid])

            # Check if a command exists
            commandFilePath = "./data/" + uidString + ".json"
            if Path(commandFilePath).is_file():
                with open(commandFilePath) as commandDataString:
                    commandData = loadJson(commandDataString)
                    print(commandData)
                    if commandData["stopPreviousCommand"] is False:
                        subprocess.Popen(commandData["command"], stdout=subprocess.PIPE, shell=False)
                    else:
                        lastUidString = uidString
                        if process is not None:
                            process.terminate()
                        processs = subprocess.Popen(commandData["command"], stdout=subprocess.PIPE, shell=False)

                    time.sleep(2);
                continue

            # Check recorded WAV file
            wavFilePath = "./data/" + uidString + ".wav"
            if Path(wavFilePath).is_file():
                lastUidString = uidString
                if process is not None:
                    process.terminate()
                process = subprocess.Popen(["/usr/bin/aplay", wavFilePath], stdout=subprocess.PIPE, shell=False)
                time.sleep(2);
                continue

            # Check MP3 file
            mp3FilePath = "./data/" + uidString + ".mp3"
            if Path(mp3FilePath).is_file():
                lastUidString = uidString
                if process is not None:
                    process.terminate()
                process = subprocess.Popen(["/usr/bin/mpg123", mp3FilePath], stdout=subprocess.PIPE, shell=False)
                time.sleep(2);
                continue

            # Otherwise, it is an unknown tag
            print("Unknown tag:", uidString)
            subprocess.run(["mpg123", "sounds/je-ne-connais-pas-cette-carte.mp3"])
            time.sleep(2);
    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
