#!/bin/bash

if [ $(tty) == "/dev/tty1" ]; then
  cd ~/raspberry-sound-box
  python3 start.py
fi
