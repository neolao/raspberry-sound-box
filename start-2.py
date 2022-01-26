import RPi.GPIO as GPIO
from pirc522 import RFID
import subprocess
from json import load as loadJson
from pathlib import Path
import time
import os
import signal
import glob
import http.server
import socketserver
import threading

LED = 16

pn532 = None
lastUidString = ''
process = None
recordProcess = None
recordStep = 0
context = None
recordCardUid = '70cddb2a'
stopCardUid = '4a14b71e'

def findFile(uid, extension = "json"):
    for name in glob.glob("data/" + uid + ".*." + extension):
        return name

    filePath = "./data/" + uid + "." + extension
    if Path(filePath).is_file():
        return filePath

    return None

class ServerHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(_self):
        _self.protocol_version = "HTTP/1.1"
        _self.send_response(200)
        _self.end_headers()
        _self.wfile.write("Sound Box".encode("utf-8"))

    def do_POST(_self):
        content_len = int(_self.headers.get("Content-Length"), 0)
        raw_body = _self.rfile.read(content_len)

        data = raw_body.decode('utf-8')
        print(data)
        handleUidString(data)

        _self.protocol_version = "HTTP/1.1"
        _self.send_response(200)
        _self.end_headers()
        _self.wfile.write("ok")



def handleUidString(uidString):
    global lastUidString
    global process
    global recordProcess
    global recordStep
    global context

    print('UID', uidString)
    GPIO.output(LED, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(LED, GPIO.LOW)

    # Check the recorder card
    if uidString == recordCardUid and recordStep == 0:
        subprocess.run(["mpg123", "sounds/veuillez-me-montrer-la-carte-a-enregistrer.mp3"])
        recordStep = 1
        return

    if recordStep == 1:
        subprocess.run(["mpg123", "sounds/l-enregistrement-demarre-dans-3-2-1.mp3"])
        recordProcess = subprocess.Popen(["/usr/bin/arecord", "-D", "hw:1,0", "-f", "S32_LE", "-r", "16000", "-c", "2", "data/" + uidString + ".wav"], stdout=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=os.setsid, shell=False)
        recordStep = 2
        return

    if recordStep == 2:
        recordProcess.terminate()
        recordProcess = None
        recordStep = 0
        subprocess.run(["mpg123", "sounds/enregistre.mp3"])
        time.sleep(2)
        return

    # Stop process
    if uidString == stopCardUid:
        print("STOP")
        if process is not None:
            process.terminate()
        time.sleep(2)
        return

    if uidString == lastUidString and process is not None and process.poll() is None:
        return

    #print('Found card with UID:', uidString, [hex(i) for i in uid])

    # Check if a command exists
    commandFilePath = findFile(uidString, "json")
    if commandFilePath is not None and Path(commandFilePath).is_file():
        with open(commandFilePath) as dataString:
            data = loadJson(dataString)
            print(data)
            action = data["action"]

            if action == "command":
               if "stopPreviousCommand" in data and data["stopPreviousCommand"] is False:
                    subprocess.Popen(data["command"], stdout=subprocess.PIPE, shell=False)
               else:
                    lastUidString = uidString
                    if process is not None:
                        process.terminate()
                    if context is not None and "contexts" in data is not None and context in data["contexts"]:
                        print("Execute command with context", context)
                        process = subprocess.Popen(data["contexts"][context], stdout=subprocess.PIPE, shell=False)
                    else:
                        print("Execute command")
                        process = subprocess.Popen(data["command"], stdout=subprocess.PIPE, shell=False)

            elif action == "setContext":
                context = data["context"]
                print("Set context:", context)

            time.sleep(2);
        return

    # Check recorded WAV file
    #wavFilePath = "./data/" + uidString + ".wav"
    wavFilePath = findFile(uidString, "wav")
    if wavFilePath is not None and Path(wavFilePath).is_file():
        lastUidString = uidString
        if process is not None:
            process.terminate()
        process = subprocess.Popen(["/usr/bin/aplay", wavFilePath], stdout=subprocess.PIPE, shell=False)
        time.sleep(2);
        return

    # Check MP3 file
    #mp3FilePath = "./data/" + uidString + ".mp3"
    mp3FilePath = findFile(uidString, "mp3")
    if mp3FilePath is not None and Path(mp3FilePath).is_file():
        lastUidString = uidString
        if process is not None:
            process.terminate()
        process = subprocess.Popen(["/usr/bin/mpg123", mp3FilePath], stdout=subprocess.PIPE, shell=False)
        time.sleep(2);
        return

    # Otherwise, it is an unknown tag
    print("Unknown tag:", uidString)
    subprocess.run(["mpg123", "sounds/je-ne-connais-pas-cette-carte.mp3"])
    f = open("data/last-unknown-card.txt", "w")
    f.write(uidString)
    f.close()
    time.sleep(2);

def listenNFC(pn532):
    while True:

        time.sleep(1)

        # Check if a card is available to read
        rc522.wait_for_tag()
        (error, tag_type) = rc522.request()
        if error:
          print("error request")

        if not error :
          (error, uid) = rc522.anticoll()
          if error:
            print("error anticoll")

        # Try again if no card is available.
        if error :
          continue

        uidString = ''.join(format(x, '02x') for x in uid)

        handleUidString(uidString)




if __name__ == '__main__':
    try:
        # Load config file
        with open("./data/config.json") as dataString:
            data = loadJson(dataString)
            print(data)
            recordCardUid = data["record-card-uid"]
            stopCardUid = data["stop-card-uid"]
 

        # Configure GPIO
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)

        # Confgure LED
        GPIO.setup(LED, GPIO.OUT)
        GPIO.output(LED, GPIO.LOW)

        # Configure NFC reader
        rc522 = RFID()

        # Ready message
        print('Waiting for RFID/NFC card...')
        subprocess.run(["mpg123", "sounds/je-suis-prete.mp3"])

        # Endless loop for the NFC reader
        nfc_thread = threading.Thread(target=listenNFC, args=(pn532,))
        nfc_thread.daemon = True
        nfc_thread.start()

        # Run web server
        with socketserver.TCPServer(("", 8080), ServerHandler) as httpd:
            print("serving at port", 8080)
            #server_thread = threading.Thread(target=httpd.serve_forever)
            #server_thread.daemon = True
            #server_thread.start()
            httpd.serve_forever()

    except Exception as e:
        print(e)
    finally:
        GPIO.cleanup()
