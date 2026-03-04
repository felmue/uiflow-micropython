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
label_state = None
label_tip1 = None
label_tip2 = None
i2c1 = None
base_echopyramid = None
record = None
playing = None
record_file_path = None
record_time_ms = None
play_start_time = None
RECORD_DURATION = None


def btna_was_clicked_event(state):
    global \
        label_title, \
        label_state, \
        label_tip1, \
        label_tip2, \
        i2c1, \
        base_echopyramid, \
        record, \
        playing, \
        RECORD_DURATION, \
        record_file_path, \
        record_time_ms, \
        play_start_time
    if not playing:
        record = True


def setup():
    global \
        label_title, \
        label_state, \
        label_tip1, \
        label_tip2, \
        i2c1, \
        base_echopyramid, \
        record, \
        playing, \
        RECORD_DURATION, \
        record_file_path, \
        record_time_ms, \
        play_start_time

    M5.begin()
    Widgets.fillScreen(0x000000)
    label_title = Widgets.Label("Audio", 36, 0, 1.0, 0x2293CB, 0x000000, Widgets.FONTS.DejaVu18)
    label_state = Widgets.Label("Idle", 46, 28, 1.0, 0xDED413, 0x000000, Widgets.FONTS.DejaVu18)
    label_tip1 = Widgets.Label(
        "press display", 1, 83, 1.0, 0xFFFFFF, 0x000000, Widgets.FONTS.DejaVu18
    )
    label_tip2 = Widgets.Label(
        "start record", 8, 103, 1.0, 0xFFFFFF, 0x000000, Widgets.FONTS.DejaVu18
    )

    BtnA.setCallback(type=BtnA.CB_TYPE.WAS_CLICKED, cb=btna_was_clicked_event)

    i2c1 = I2C(1, scl=Pin(39), sda=Pin(38), freq=100000)
    base_echopyramid = AtomicEchoPyramidBase(
        i2c1, i2s_port=1, dev_addr=0x1A, sample_rate=16000, i2s_sck=6, i2s_ws=8, i2s_di=5, i2s_do=7
    )
    RECORD_DURATION = 0
    record_file_path = "test.wav"
    record_time_ms = 5000
    base_echopyramid.set_volume(60)


def loop():
    global \
        label_title, \
        label_state, \
        label_tip1, \
        label_tip2, \
        i2c1, \
        base_echopyramid, \
        record, \
        playing, \
        RECORD_DURATION, \
        record_file_path, \
        record_time_ms, \
        play_start_time
    M5.update()
    if record:
        record = False
        print("start record")
        label_tip1.setVisible(False)
        label_tip2.setVisible(False)
        label_state.setText(str("Recording..."))
        label_state.setCursor(x=6, y=28)
        label_state.setColor(0xFF0000, 0x000000)
        base_echopyramid.record_wav_file(
            "/flash/res/audio/test.wav",
            rate=16000,
            bits=16,
            channel=AtomicEchoPyramidBase.STEREO,
            duration=record_time_ms,
        )
        print("start play")
        label_state.setText(str("Playing..."))
        label_state.setCursor(x=21, y=28)
        label_state.setColor(0x33CC00, 0x000000)
        base_echopyramid.play_wav_file("/flash/res/audio/" + str(record_file_path))
        playing = True
        play_start_time = time.ticks_ms()
    if playing:
        if (time.ticks_diff((time.ticks_ms()), play_start_time)) > record_time_ms:
            playing = False
            print("play finished")
            label_state.setText(str("Idle"))
            label_state.setCursor(x=46, y=28)
            label_state.setColor(0xFFFF00, 0x000000)
            label_tip1.setVisible(True)
            label_tip2.setVisible(True)


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
