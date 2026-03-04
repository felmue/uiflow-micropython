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


label0 = None
label1 = None
label2 = None
i2c1 = None
base_echopyramid = None
tp = None
tp_index = None
last_tp_time = None
strip_enable = None
time_diff = None
i = None


def setup():
    global \
        label0, \
        label1, \
        label2, \
        i2c1, \
        base_echopyramid, \
        tp, \
        last_tp_time, \
        strip_enable, \
        time_diff, \
        tp_index, \
        i

    M5.begin()
    Widgets.fillScreen(0x000000)
    label0 = Widgets.Label("EchoPyramid", 1, 2, 1.0, 0x12C7DE, 0x000000, Widgets.FONTS.DejaVu18)
    label1 = Widgets.Label("Touch", 36, 47, 1.0, 0xFFFFFF, 0x000000, Widgets.FONTS.DejaVu18)
    label2 = Widgets.Label("Control", 29, 75, 1.0, 0xFFFFFF, 0x000000, Widgets.FONTS.DejaVu18)

    i2c1 = I2C(1, scl=Pin(39), sda=Pin(38), freq=100000)
    base_echopyramid = AtomicEchoPyramidBase(
        i2c1, i2s_port=1, dev_addr=0x1A, sample_rate=16000, i2s_sck=6, i2s_ws=8, i2s_di=5, i2s_do=7
    )
    base_echopyramid.set_rgb_color(1, 2, 56789)
    last_tp_time = [0, 0, 0, 0]
    strip_enable = [False, False, False, False]


def loop():
    global \
        label0, \
        label1, \
        label2, \
        i2c1, \
        base_echopyramid, \
        tp, \
        last_tp_time, \
        strip_enable, \
        time_diff, \
        tp_index, \
        i
    M5.update()
    tp = base_echopyramid.get_touch()
    print((str("TP: ") + str(tp)))
    for tp_index in range(1, 5):
        if tp[int(tp_index - 1)]:
            if tp_index == 1:
                for i in range(7):
                    base_echopyramid.set_rgb_color(1, 7 + i, 0x00CCCC)

            elif tp_index == 2:
                for i in range(7):
                    base_echopyramid.set_rgb_color(1, i, 0x00CCCC)

            elif tp_index == 3:
                for i in range(7):
                    base_echopyramid.set_rgb_color(2, i, 0x00CCCC)

            elif tp_index == 4:
                for i in range(7):
                    base_echopyramid.set_rgb_color(2, 7 + i, 0x00CCCC)

            last_tp_time[int(tp_index - 1)] = time.ticks_ms()
            strip_enable[int(tp_index - 1)] = True
        else:
            time_diff = time.ticks_diff((time.ticks_ms()), (last_tp_time[int(tp_index - 1)]))
            if time_diff > 500 and strip_enable[int(tp_index - 1)]:
                strip_enable[int(tp_index - 1)] = False
                if tp_index == 1:
                    for i in range(7):
                        base_echopyramid.set_rgb_color(1, 7 + i, 0x000000)

                elif tp_index == 2:
                    for i in range(7):
                        base_echopyramid.set_rgb_color(1, i, 0x000000)

                elif tp_index == 3:
                    for i in range(7):
                        base_echopyramid.set_rgb_color(2, i, 0x000000)

                elif tp_index == 4:
                    for i in range(7):
                        base_echopyramid.set_rgb_color(2, 7 + i, 0x000000)


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
