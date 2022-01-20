import RPi.GPIO as GPIO
from pirc522 import RFID
import time
import subprocess

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# Confgure LED
LED = 16
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.LOW)

rc522 = RFID() #On instancie la lib

print('En attente d\'un badge (pour quitter, Ctrl + c): ')

while True :
    rc522.wait_for_tag()
    (error, tag_type) = rc522.request()

    if not error :
        (error, uid) = rc522.anticoll()

        if not error :
            uidString = ''.join(format(x, '02x') for x in uid)
            print('UID: ', uidString)

            GPIO.output(LED, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(LED, GPIO.LOW)

            # subprocess.run(["mpg123", "data/au-feu-les-pompiers.mp3"])
            time.sleep(1)

