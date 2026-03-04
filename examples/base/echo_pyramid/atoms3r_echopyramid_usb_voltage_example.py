# SPDX-FileCopyrightText: 2026 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT

import time
import M5
from M5 import *
from base import AtomicEchoPyramidBase
from hardware import Pin
from hardware import I2C


label_title = None
label_voltage = None
label_unit = None
label_value = None
i2c1 = None
base_echopyramid = None
last_time = None
voltage = None


def setup():
    global \
        label_title, \
        label_voltage, \
        label_unit, \
        label_value, \
        i2c1, \
        base_echopyramid, \
        last_time, \
        voltage

    M5.begin()
    Widgets.fillScreen(0x000000)
    label_title = Widgets.Label(
        "EchoPyramid", 1, 1, 1.0, 0x12C4E6, 0x000000, Widgets.FONTS.DejaVu18
    )
    label_voltage = Widgets.Label(
        "USB Volatge", 5, 31, 1.0, 0xFFFFFF, 0x000000, Widgets.FONTS.DejaVu18
    )
    label_unit = Widgets.Label("mV", 47, 105, 1.0, 0xFFFFFF, 0x000000, Widgets.FONTS.DejaVu18)
    label_value = Widgets.Label("5000", 31, 66, 1.0, 0xFFFFFF, 0x000000, Widgets.FONTS.DejaVu24)

    i2c1 = I2C(1, scl=Pin(39), sda=Pin(38), freq=100000)
    base_echopyramid = AtomicEchoPyramidBase(
        i2c1, i2s_port=1, dev_addr=0x1A, sample_rate=16000, i2s_sck=6, i2s_ws=8, i2s_di=5, i2s_do=7
    )


def loop():
    global \
        label_title, \
        label_voltage, \
        label_unit, \
        label_value, \
        i2c1, \
        base_echopyramid, \
        last_time, \
        voltage
    M5.update()
    if (time.ticks_diff((time.ticks_ms()), last_time)) >= 200:
        last_time = time.ticks_ms()
        voltage = base_echopyramid.get_input_voltage()
        if voltage >= 5000:
            label_value.setColor(0x33CC00, 0x000000)
        else:
            label_value.setColor(0xFF0000, 0x000000)
        label_value.setText(str(voltage))


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
