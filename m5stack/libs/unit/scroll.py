# SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT

from .unit_helper import UnitError
import struct


class ScrollUnit:
    _ENCODER_COUNTER_VALUE_REG = 0x10
    _ENCODER_BUTTON_STATUS_REG = 0x20
    _ENCODER_RGB_LED_REG = 0x30
    _ENCODER_RESET_REG = 0x40
    _ENCODER_INCREMENTS_REG = 0x50
    _ENCODER_BL_REG = 0xFC
    _ENCODER_FW_REG = 0xFE

    def __init__(self, i2c, address: int | list | tuple = 0x40) -> None:
        self._i2c = i2c
        self._address = address
        self._buffer = memoryview(bytearray(4))
        if self._address not in self._i2c.scan():
            raise UnitError("Scroll Unit maybe not connect")
        self.reset_rotary_value()
        self._last_value = self._get_rotary_value()
        self._zero_value = self._last_value
        self._start_value = 0

    def get_rotary_status(self):
        val = self._get_rotary_value()
        if val != self._last_value:
            return True
        return False

    def get_rotary_value(self):
        self._last_value = self._get_rotary_value()
        return self._start_value + self._last_value - self._zero_value

    def get_rotary_increments(self):
        buf = self._read_reg_bytes(self._ENCODER_INCREMENTS_REG, 4)
        return struct.unpack("<h", buf)[0]

    def _get_rotary_value(self):
        buf = self._read_reg_bytes(self._ENCODER_COUNTER_VALUE_REG, 4)
        return struct.unpack("<h", buf)[0]

    def set_rotary_value(self, value: int) -> None:
        self._start_value = value

    def reset_rotary_value(self):
        self._write_reg_bytes(self._ENCODER_RESET_REG, b"\x01")
        self._zero_value = 0
        self._last_value = 0
        self._start_value = 0

    def get_button_status(self) -> bool:
        buf = self._read_reg_bytes(self._ENCODER_BUTTON_STATUS_REG, 2)
        return not bool(buf[0])

    def set_color(self, index: int = 0, rgb: int = 0) -> None:
        buf = self._buffer[1:4]
        buf = rgb.to_bytes(3, "big")
        self._write_reg_bytes(self._ENCODER_RGB_LED_REG + 1, buf)

    def fill_color(self, rgb: int = 0) -> None:
        self.set_color(0, rgb)

    def get_bootloader_version(self) -> str:
        return str(self._read_reg_bytes(self._ENCODER_BL_REG, 1)[0])

    def get_firmware_version(self) -> str:
        return str(self._read_reg_bytes(self._ENCODER_FW_REG, 1)[0])

    def _read_reg_bytes(self, reg: int = 0, length: int = 0) -> bytearray:
        buf = self._buffer[0:1]
        buf[0] = reg
        self._i2c.writeto(self._address, buf)
        buf = self._buffer[0:length]
        self._i2c.readfrom_into(self._address, buf)
        return buf

    def _write_reg_bytes(self, reg, data):
        buf = self._buffer[0 : 1 + len(data)]
        buf[0] = reg
        buf[1:] = bytes(data)
        self._i2c.writeto(self._address, buf)
