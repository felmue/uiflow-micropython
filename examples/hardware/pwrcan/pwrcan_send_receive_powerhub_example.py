# SPDX-FileCopyrightText: 2026 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT

import os, sys, io
import M5
from M5 import *
from hardware import PWRCAN


pwrcan = None


def setup():
    global pwrcan

    M5.begin()
    Power.setExtPortBusConfig(direction=1, output_enable=1, voltage=12000, current_limit=232)
    pwrcan = PWRCAN(id=0, port=(40, 39), mode=PWRCAN.NORMAL, baudrate=25000)


def loop():
    global pwrcan
    M5.update()
    if BtnA.wasPressed():
        pwrcan.send("uiflow2", 0, timeout=0, rtr=False, extframe=False)
    if pwrcan.any(0):
        print(pwrcan.recv(0, timeout=5000))


if __name__ == "__main__":
    try:
        setup()
        while True:
            loop()
    except (Exception, KeyboardInterrupt) as e:
        try:
            from utility import print_error_msg

            print_error_msg(e)
        except ImportError:
            print("please update to latest firmware")
