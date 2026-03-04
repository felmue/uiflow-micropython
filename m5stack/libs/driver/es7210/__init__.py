# SPDX-FileCopyrightText: 2025 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT

from . import reg
import time
from collections import namedtuple

_coeff_div = namedtuple(
    "_coeff_div",
    [
        "mclk",
        "lrck",
        "adc_div",
        "dll",
        "doubler",
        "osr",
        "mclk_src",
        "lrck_h",
        "lrck_l",
    ],
)

# Clock coefficient table from esp_codec_dev es7210.c
# (mclk, lrck, adc_div, dll, doubler, osr, mclk_src, lrck_h, lrck_l)
coeff_div = (
    _coeff_div(12288000, 8000, 0x03, 0x01, 0x00, 0x20, 0x00, 0x06, 0x00),
    _coeff_div(16384000, 8000, 0x04, 0x01, 0x00, 0x20, 0x00, 0x08, 0x00),
    _coeff_div(19200000, 8000, 0x1E, 0x00, 0x01, 0x28, 0x00, 0x09, 0x60),
    _coeff_div(4096000, 8000, 0x01, 0x01, 0x00, 0x20, 0x00, 0x02, 0x00),
    _coeff_div(11289600, 11025, 0x02, 0x01, 0x00, 0x20, 0x00, 0x01, 0x00),
    _coeff_div(12288000, 12000, 0x02, 0x01, 0x00, 0x20, 0x00, 0x04, 0x00),
    _coeff_div(19200000, 12000, 0x14, 0x00, 0x01, 0x28, 0x00, 0x06, 0x40),
    _coeff_div(4096000, 16000, 0x01, 0x01, 0x01, 0x20, 0x00, 0x01, 0x00),
    _coeff_div(19200000, 16000, 0x0A, 0x00, 0x00, 0x1E, 0x00, 0x04, 0x80),
    _coeff_div(16384000, 16000, 0x02, 0x01, 0x00, 0x20, 0x00, 0x04, 0x00),
    _coeff_div(12288000, 16000, 0x03, 0x01, 0x01, 0x20, 0x00, 0x03, 0x00),
    _coeff_div(11289600, 22050, 0x01, 0x01, 0x00, 0x20, 0x00, 0x02, 0x00),
    _coeff_div(12288000, 24000, 0x01, 0x01, 0x00, 0x20, 0x00, 0x02, 0x00),
    _coeff_div(19200000, 24000, 0x0A, 0x00, 0x01, 0x28, 0x00, 0x03, 0x20),
    _coeff_div(8192000, 32000, 0x01, 0x01, 0x01, 0x20, 0x00, 0x01, 0x00),
    _coeff_div(12288000, 32000, 0x03, 0x00, 0x00, 0x20, 0x00, 0x01, 0x80),
    _coeff_div(16384000, 32000, 0x01, 0x01, 0x00, 0x20, 0x00, 0x02, 0x00),
    _coeff_div(19200000, 32000, 0x05, 0x00, 0x00, 0x1E, 0x00, 0x02, 0x58),
    _coeff_div(11289600, 44100, 0x01, 0x01, 0x01, 0x20, 0x00, 0x01, 0x00),
    _coeff_div(12288000, 48000, 0x01, 0x01, 0x01, 0x20, 0x00, 0x01, 0x00),
    _coeff_div(19200000, 48000, 0x05, 0x00, 0x01, 0x28, 0x00, 0x01, 0x90),
    _coeff_div(16384000, 64000, 0x01, 0x01, 0x00, 0x20, 0x01, 0x01, 0x00),
    _coeff_div(19200000, 64000, 0x05, 0x00, 0x01, 0x1E, 0x00, 0x01, 0x2C),
    _coeff_div(11289600, 88200, 0x01, 0x01, 0x01, 0x20, 0x01, 0x00, 0x80),
    _coeff_div(12288000, 96000, 0x01, 0x01, 0x01, 0x20, 0x01, 0x00, 0x80),
    _coeff_div(19200000, 96000, 0x05, 0x00, 0x01, 0x28, 0x01, 0x00, 0xC8),
)

INPUT_MIC1 = 0x01
INPUT_MIC2 = 0x02
INPUT_MIC3 = 0x04
INPUT_MIC4 = 0x08


def get_coeff(mclk: int, lrck: int):
    for i in range(len(coeff_div)):
        if coeff_div[i].lrck == lrck and coeff_div[i].mclk == mclk:
            return i
    return -1


class ES7210:
    """ES7210 dual-channel ADC for microphone input."""

    def __init__(self, i2c, address: int = reg.ES7210_ADDR_00):
        self._i2c = i2c
        self._address = address
        self._master_mode = True
        self._mclk_div = 256
        self._mic_select = INPUT_MIC1 | INPUT_MIC2
        self._gain = 10  # 30dB default

    def _write_reg(self, reg_addr: int, value: int):
        self._i2c.writeto_mem(self._address, reg_addr, bytes([value]))

    def _read_reg(self, reg_addr: int) -> int:
        return self._i2c.readfrom_mem(self._address, reg_addr, 1)[0]

    def _update_reg_bit(self, reg_addr: int, update_bits: int, data: int):
        regv = self._read_reg(reg_addr)
        regv = (regv & (~update_bits)) | (update_bits & data)
        self._write_reg(reg_addr, regv)

    def init(
        self,
        sample_rate: int = 16000,
        master_mode: bool = True,
        mic_select: int = None,
        mclk_div: int = 256,
    ):
        """Initialize ES7210 ADC.

        :param sample_rate: Sample rate in Hz (default 16000)
        :param master_mode: True for master mode (default True)
        :param mic_select: Mic selection INPUT_MIC1|INPUT_MIC2|INPUT_MIC3|INPUT_MIC4
        :param mclk_div: MCLK/LRCK ratio (default 256)
        """
        self._master_mode = master_mode
        self._mclk_div = mclk_div if mclk_div else 256
        if mic_select is not None:
            self._mic_select = mic_select
        else:
            self._mic_select = INPUT_MIC1 | INPUT_MIC2

        self._write_reg(reg.ES7210_RESET_REG00, 0xFF)
        time.sleep(0.01)
        self._write_reg(reg.ES7210_RESET_REG00, 0x41)
        self._write_reg(reg.ES7210_CLOCK_OFF_REG01, 0x3F)
        self._write_reg(reg.ES7210_TIME_CONTROL0_REG09, 0x30)
        self._write_reg(reg.ES7210_TIME_CONTROL1_REG0A, 0x30)
        self._write_reg(reg.ES7210_ADC12_HPF2_REG23, 0x2A)
        self._write_reg(reg.ES7210_ADC12_HPF1_REG22, 0x0A)
        self._write_reg(reg.ES7210_ADC34_HPF2_REG20, 0x0A)
        self._write_reg(reg.ES7210_ADC34_HPF1_REG21, 0x2A)

        if master_mode:
            self._update_reg_bit(reg.ES7210_MODE_CONFIG_REG08, 0x01, 0x01)
            self._update_reg_bit(reg.ES7210_MASTER_CLK_REG03, 0x80, 0x00)
        else:
            self._update_reg_bit(reg.ES7210_MODE_CONFIG_REG08, 0x01, 0x00)

        self._write_reg(reg.ES7210_ANALOG_REG40, 0x43)
        self._write_reg(reg.ES7210_MIC12_BIAS_REG41, 0x70)
        self._write_reg(reg.ES7210_MIC34_BIAS_REG42, 0x70)
        self._write_reg(reg.ES7210_OSR_REG07, 0x20)
        self._write_reg(reg.ES7210_MAINCLK_REG02, 0xC1)

        self._mic_select_config()
        self.set_gain(30.0)
        self.config_sample(sample_rate)
        self._set_bits(16)
        self._config_fmt()
        self.enable(True)

    def _mic_select_config(self):
        for i in range(4):
            self._update_reg_bit(reg.ES7210_MIC1_GAIN_REG43 + i, 0x10, 0x00)
        self._write_reg(reg.ES7210_MIC12_POWER_REG4B, 0xFF)
        self._write_reg(reg.ES7210_MIC34_POWER_REG4C, 0xFF)

        if self._mic_select & INPUT_MIC1:
            self._update_reg_bit(reg.ES7210_CLOCK_OFF_REG01, 0x0B, 0x00)
            self._write_reg(reg.ES7210_MIC12_POWER_REG4B, 0x00)
            self._update_reg_bit(reg.ES7210_MIC1_GAIN_REG43, 0x10, 0x10)
            self._update_reg_bit(reg.ES7210_MIC1_GAIN_REG43, 0x0F, self._gain)
        if self._mic_select & INPUT_MIC2:
            self._update_reg_bit(reg.ES7210_CLOCK_OFF_REG01, 0x0B, 0x00)
            self._write_reg(reg.ES7210_MIC12_POWER_REG4B, 0x00)
            self._update_reg_bit(reg.ES7210_MIC2_GAIN_REG44, 0x10, 0x10)
            self._update_reg_bit(reg.ES7210_MIC2_GAIN_REG44, 0x0F, self._gain)
        if self._mic_select & INPUT_MIC3:
            self._update_reg_bit(reg.ES7210_CLOCK_OFF_REG01, 0x15, 0x00)
            self._write_reg(reg.ES7210_MIC34_POWER_REG4C, 0x00)
            self._update_reg_bit(reg.ES7210_MIC3_GAIN_REG45, 0x10, 0x10)
            self._update_reg_bit(reg.ES7210_MIC3_GAIN_REG45, 0x0F, self._gain)
        if self._mic_select & INPUT_MIC4:
            self._update_reg_bit(reg.ES7210_CLOCK_OFF_REG01, 0x15, 0x00)
            self._write_reg(reg.ES7210_MIC34_POWER_REG4C, 0x00)
            self._update_reg_bit(reg.ES7210_MIC4_GAIN_REG46, 0x10, 0x10)
            self._update_reg_bit(reg.ES7210_MIC4_GAIN_REG46, 0x0F, self._gain)

        mic_count = bin(self._mic_select).count("1")
        if mic_count >= 3:
            self._write_reg(reg.ES7210_SDP_INTERFACE2_REG12, 0x02)  # TDM mode
        else:
            self._write_reg(reg.ES7210_SDP_INTERFACE2_REG12, 0x00)

    def config_sample(self, sample_rate: int):
        """Configure sample rate."""
        if not self._master_mode:
            return
        mclk_fre = sample_rate * self._mclk_div
        coeff = get_coeff(mclk_fre, sample_rate)
        if coeff < 0:
            print(
                "Unable to configure sample rate {}Hz with {}Hz MCLK".format(sample_rate, mclk_fre)
            )
            return
        c = coeff_div[coeff]
        regv = self._read_reg(reg.ES7210_MAINCLK_REG02) & 0x00
        regv |= c.adc_div
        regv |= c.doubler << 6
        regv |= c.dll << 7
        self._write_reg(reg.ES7210_MAINCLK_REG02, regv)
        self._write_reg(reg.ES7210_OSR_REG07, c.osr)
        self._write_reg(reg.ES7210_LRCK_DIVH_REG04, c.lrck_h)
        self._write_reg(reg.ES7210_LRCK_DIVL_REG05, c.lrck_l)

    def _set_bits(self, bits: int):
        adc_iface = self._read_reg(reg.ES7210_SDP_INTERFACE1_REG11) & 0x1F
        if bits == 16:
            adc_iface |= 0x60
        elif bits == 24:
            adc_iface |= 0x00
        elif bits == 32:
            adc_iface |= 0x80
        else:
            adc_iface |= 0x60
        self._write_reg(reg.ES7210_SDP_INTERFACE1_REG11, adc_iface)

    def _config_fmt(self):
        adc_iface = self._read_reg(reg.ES7210_SDP_INTERFACE1_REG11) & 0xFC
        adc_iface |= 0x00  # I2S format
        self._write_reg(reg.ES7210_SDP_INTERFACE1_REG11, adc_iface)

    def _get_gain_db(self, db: float) -> int:
        db += 0.5
        if db < 3:
            return 0
        if db < 33:
            return min(int(db / 3), 10)
        if db < 34.5:
            return 11
        if db < 36:
            return 12
        if db < 37:
            return 13
        return 14

    def set_gain(self, db: float):
        """Set microphone gain in dB (0-37.5)."""
        self._gain = self._get_gain_db(db)
        if self._mic_select & INPUT_MIC1:
            self._update_reg_bit(reg.ES7210_MIC1_GAIN_REG43, 0x0F, self._gain)
        if self._mic_select & INPUT_MIC2:
            self._update_reg_bit(reg.ES7210_MIC2_GAIN_REG44, 0x0F, self._gain)
        if self._mic_select & INPUT_MIC3:
            self._update_reg_bit(reg.ES7210_MIC3_GAIN_REG45, 0x0F, self._gain)
        if self._mic_select & INPUT_MIC4:
            self._update_reg_bit(reg.ES7210_MIC4_GAIN_REG46, 0x0F, self._gain)

    def set_mute(self, mute: bool):
        """Mute or unmute ADC output."""
        if mute:
            self._update_reg_bit(0x14, 0x03, 0x03)
            self._update_reg_bit(0x15, 0x03, 0x03)
        else:
            self._update_reg_bit(0x14, 0x03, 0x00)
            self._update_reg_bit(0x15, 0x03, 0x00)

    def enable(self, enable: bool):
        """Enable or disable ES7210 ADC."""
        if enable:
            off_reg = self._read_reg(reg.ES7210_CLOCK_OFF_REG01)
            self._write_reg(reg.ES7210_CLOCK_OFF_REG01, off_reg & 0x3F)
            self._write_reg(reg.ES7210_POWER_DOWN_REG06, 0x00)
            self._write_reg(reg.ES7210_ANALOG_REG40, 0x43)
            self._write_reg(reg.ES7210_MIC1_POWER_REG47, 0x08)
            self._write_reg(reg.ES7210_MIC2_POWER_REG48, 0x08)
            self._write_reg(reg.ES7210_MIC3_POWER_REG49, 0x08)
            self._write_reg(reg.ES7210_MIC4_POWER_REG4A, 0x08)
            self._mic_select_config()
            self._write_reg(reg.ES7210_ANALOG_REG40, 0x43)
            self._write_reg(reg.ES7210_RESET_REG00, 0x71)
            self._write_reg(reg.ES7210_RESET_REG00, 0x41)
        else:
            self._write_reg(reg.ES7210_MIC1_POWER_REG47, 0xFF)
            self._write_reg(reg.ES7210_MIC2_POWER_REG48, 0xFF)
            self._write_reg(reg.ES7210_MIC3_POWER_REG49, 0xFF)
            self._write_reg(reg.ES7210_MIC4_POWER_REG4A, 0xFF)
            self._write_reg(reg.ES7210_MIC12_POWER_REG4B, 0xFF)
            self._write_reg(reg.ES7210_MIC34_POWER_REG4C, 0xFF)
            self._write_reg(reg.ES7210_ANALOG_REG40, 0xC0)
            self._write_reg(reg.ES7210_CLOCK_OFF_REG01, 0x7F)
            self._write_reg(reg.ES7210_POWER_DOWN_REG06, 0x07)
