# SPDX-FileCopyrightText: 2026 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT
import os, sys, io
import M5
from M5 import *
from hardware import Pin
from hardware import I2C
from base import AtomicEchoPyramidBase
import time


label_title = None
label_mode = None
label_tip1 = None
label_tipe = None
i2c1 = None
base_echopyramid = None


mode = None
MODE_BRATH = None
MODE_FLOW = None
index = None
brightness = None
i = None
direction = None


# Describe this function...
def init(mode):
    global \
        MODE_BRATH, \
        MODE_FLOW, \
        index, \
        brightness, \
        i, \
        direction, \
        label_title, \
        label_mode, \
        label_tip1, \
        label_tipe, \
        i2c1, \
        base_echopyramid
    if mode == MODE_BRATH:
        print("mode: brathe")
        label_mode.setText(str("braeth"))
        label_mode.setCursor(x=32, y=40)
        for i in range(14):
            base_echopyramid.set_rgb_color(1, i, 0x33CCFF)
            base_echopyramid.set_rgb_color(2, i, 0x33CCFF)

        brightness = 0
        direction = True
    elif mode == MODE_FLOW:
        print("mode: flow")
        label_mode.setText(str("flow"))
        label_mode.setCursor(x=46, y=40)
        for i in range(14):
            base_echopyramid.set_rgb_color(1, i, 0x000000)
            base_echopyramid.set_rgb_color(2, i, 0x000000)

        base_echopyramid.set_rgb_brightness(1, 30, False)
        base_echopyramid.set_rgb_brightness(2, 30, False)


def btna_was_clicked_event(state):
    global \
        label_title, \
        label_mode, \
        label_tip1, \
        label_tipe, \
        i2c1, \
        base_echopyramid, \
        mode, \
        MODE_BRATH, \
        MODE_FLOW, \
        index, \
        brightness, \
        direction, \
        i
    mode = (mode if isinstance(mode, (int, float)) else 0) + 1
    mode = mode % 2
    init(mode)


def setup():
    global \
        label_title, \
        label_mode, \
        label_tip1, \
        label_tipe, \
        i2c1, \
        base_echopyramid, \
        mode, \
        MODE_BRATH, \
        MODE_FLOW, \
        index, \
        brightness, \
        direction, \
        i

    M5.begin()
    Widgets.fillScreen(0x000000)
    label_title = Widgets.Label(
        "EchoPyramid", 1, 1, 1.0, 0x11CFE8, 0x000000, Widgets.FONTS.DejaVu18
    )
    label_mode = Widgets.Label("breath", 32, 36, 1.0, 0xD41194, 0x000000, Widgets.FONTS.DejaVu18)
    label_tip1 = Widgets.Label(
        "press display", 18, 88, 1.0, 0xFFFFFF, 0x000000, Widgets.FONTS.DejaVu12
    )
    label_tipe = Widgets.Label(
        "change mode", 16, 106, 1.0, 0xFFFFFF, 0x000000, Widgets.FONTS.DejaVu12
    )

    BtnA.setCallback(type=BtnA.CB_TYPE.WAS_CLICKED, cb=btna_was_clicked_event)

    i2c1 = I2C(1, scl=Pin(39), sda=Pin(38), freq=100000)
    base_echopyramid = AtomicEchoPyramidBase(
        i2c1, i2s_port=1, dev_addr=0x1A, sample_rate=16000, i2s_sck=6, i2s_ws=8, i2s_di=5, i2s_do=7
    )
    index = 0
    MODE_BRATH = 0
    MODE_FLOW = 1
    mode = MODE_BRATH
    brightness = 0
    init(mode)


def loop():
    global \
        label_title, \
        label_mode, \
        label_tip1, \
        label_tipe, \
        i2c1, \
        base_echopyramid, \
        mode, \
        MODE_BRATH, \
        MODE_FLOW, \
        index, \
        brightness, \
        direction, \
        i
    M5.update()
    if mode == MODE_BRATH:
        base_echopyramid.set_rgb_brightness(1, brightness, False)
        base_echopyramid.set_rgb_brightness(2, brightness, False)
        if direction:
            brightness = (brightness if isinstance(brightness, (int, float)) else 0) + 1
            if brightness > 50:
                direction = False
        else:
            brightness = (brightness if isinstance(brightness, (int, float)) else 0) + -1
            if brightness < 0:
                direction = True
        print((str("brightness: ") + str(brightness)))
        time.sleep_ms(50)
    elif mode == MODE_FLOW:
        if index > 0:
            base_echopyramid.set_rgb_color(1, index - 1, 0x000000)
            base_echopyramid.set_rgb_color(2, index - 1, 0x000000)
        if index == 14:
            index = 0
        base_echopyramid.set_rgb_color(1, index, 0x3333FF)
        base_echopyramid.set_rgb_color(2, index, 0x3333FF)
        index = (index if isinstance(index, (int, float)) else 0) + 1
        print((str("index： ") + str(index)))
        time.sleep_ms(50)


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
