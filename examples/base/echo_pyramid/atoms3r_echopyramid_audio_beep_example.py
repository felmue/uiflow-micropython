# SPDX-FileCopyrightText: 2026 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT

import os, sys, io
import M5
from M5 import *
from hardware import Pin
from hardware import I2C
from base import AtomicEchoPyramidBase
import random


label_title = None
label_tip1 = None
label_freq = None
label_tip2 = None
i2c1 = None
base_echopyramid = None
beep = None
freq = None


def btna_was_eclicked_event(state):
    global label_title, label_tip1, label_freq, label_tip2, i2c1, base_echopyramid, beep, freq
    beep = True


def setup():
    global label_title, label_tip1, label_freq, label_tip2, i2c1, base_echopyramid, beep, freq

    M5.begin()
    Widgets.fillScreen(0x000000)
    label_title = Widgets.Label(
        "Audio Play", 13, 2, 1.0, 0x0EE9EE, 0x000000, Widgets.FONTS.DejaVu18
    )
    label_tip1 = Widgets.Label(
        "press display", 1, 83, 1.0, 0xFFFFFF, 0x000000, Widgets.FONTS.DejaVu18
    )
    label_freq = Widgets.Label(
        "Freq: -- Hz", 15, 41, 1.0, 0xFFFFFF, 0x000000, Widgets.FONTS.DejaVu18
    )
    label_tip2 = Widgets.Label("beep", 39, 103, 1.0, 0xFFFFFF, 0x000000, Widgets.FONTS.DejaVu18)

    BtnA.setCallback(type=BtnA.CB_TYPE.WAS_CLICKED, cb=btna_was_eclicked_event)

    i2c1 = I2C(1, scl=Pin(39), sda=Pin(38), freq=100000)
    base_echopyramid = AtomicEchoPyramidBase(
        i2c1, i2s_port=1, dev_addr=0x1A, sample_rate=16000, i2s_sck=6, i2s_ws=8, i2s_di=5, i2s_do=7
    )
    base_echopyramid.set_volume(50)


def loop():
    global label_title, label_tip1, label_freq, label_tip2, i2c1, base_echopyramid, beep, freq
    M5.update()
    if beep:
        beep = False
        freq = random.randint(500, 3500)
        if freq >= 1000:
            label_freq.setCursor(x=0, y=41)
            label_freq.setText(str((str("Freq:") + str((str(freq) + str("Hz"))))))
        else:
            label_freq.setCursor(x=9, y=41)
            label_freq.setText(str((str("Freq:") + str((str(freq) + str("Hz"))))))
        base_echopyramid.tone(freq, 200)


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
