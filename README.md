# Sound Box + NFC

## Install

![NFC Board](documentation/nfc-board.jpg)

```bash
sudo apt-get install python3-dev python3-rpi.gpio python3-pip mpg123 mpv
pip3 install RPi.GPIO
pip3 install spidev
pip3 install serial
```

edit `/boot/config.txt` and uncomment `dtparam=i2s=on`
