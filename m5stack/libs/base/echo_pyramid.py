# SPDX-FileCopyrightText: 2026 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT

"""
Echo Pyramid base driver for AtomS3R + Echo Pyramid.
Uses ES8311 (DAC), ES7210 (ADC), Si5351 (clock), AW87559 (amplifier).
"""
from micropython import const
import driver.es8311 as es8311
import driver.es7210 as es7210
import m5audio2
import machine
import time
import M5


# I2C addresses
SI5351_ADDR = const(0x60)
AW87559_ADDR = const(0x5B)
ES8311_ADDR = const(0x18)
ES7210_ADDR = const(0x40)
CUSTOM_DEVICE_ADDR = const(0x1A)  # STM32 RGB/touch controller

# STM32 register addresses
REG_DEVICE_ADDR = const(0xFF)
REG_FIRMWARE_VERSION = const(0xFE)
REG_TOUCH1_STATUS = const(0x00)
REG_TOUCH2_STATUS = const(0x01)
REG_TOUCH3_STATUS = const(0x02)
REG_TOUCH4_STATUS = const(0x03)
REG_STRIP1_BRIGHTNESS = const(0x10)
REG_STRIP2_BRIGHTNESS = const(0x11)
REG_STRIP1_I1_COLOR = const(0x20)  # 4 bytes per LED (B, G, R, dummy)
REG_STRIP2_I1_COLOR = const(0x60)
REG_INPUT_VOLTAGE_L = const(0xB0)
REG_INPUT_VOLTAGE_H = const(0xB1)


def _si5351_init(i2c):
    """Initialize Si5351 clock generator. I2C Address: 0x60."""
    w_buffer = bytearray(10)
    # Disable all outputs
    i2c.writeto_mem(SI5351_ADDR, 3, b"\xff")
    time.sleep(0.01)
    # Power down output drivers
    w_buffer[0:3] = bytes([0x80, 0x80, 0x80])
    i2c.writeto_mem(SI5351_ADDR, 16, w_buffer[:3])
    # Crystal Internal Load Capacitance
    i2c.writeto_mem(SI5351_ADDR, 183, b"\xC0")
    # Multisynth NA Parameters
    w_buffer[0:8] = bytes([0xFF, 0xFD, 0x00, 0x09, 0x26, 0xF7, 0x4F, 0x72])
    i2c.writeto_mem(SI5351_ADDR, 26, w_buffer[:8])
    # Multisynth1 Parameters
    w_buffer[0:8] = bytes([0x00, 0x01, 0x00, 0x2F, 0x00, 0x00, 0x00, 0x00])
    i2c.writeto_mem(SI5351_ADDR, 50, w_buffer[:8])
    # CLK1 Control
    i2c.writeto_mem(SI5351_ADDR, 17, bytes([(3 << 2) | (1 << 6)]))
    # PLL Reset
    i2c.writeto_mem(SI5351_ADDR, 177, b"\xA0")
    # Enable all outputs
    i2c.writeto_mem(SI5351_ADDR, 3, b"\x00")


def _aw87559_init(i2c, dev_addr: int = CUSTOM_DEVICE_ADDR):
    """Initialize AW87559 audio amplifier. I2C Address: 0x5B.

    :param i2c: I2C object
    :param dev_addr: Custom device address. Default 0x1A.
    """
    try:
        # Optional: STM32 at 0x1A can reset AW87559 via reg 0xA0
        i2c.writeto_mem(dev_addr, 0xA0, b"\x01")
        time.sleep_ms(10)
        i2c.writeto_mem(AW87559_ADDR, 0x01, b"\x78")  # Enable PA
    except OSError:
        pass  # AW87559 may not be present


def _aw87559_set_speaker(i2c, enable: bool):
    """Enable or disable AW87559 speaker output."""
    try:
        i2c.writeto_mem(AW87559_ADDR, 0x01, b"\x78" if enable else b"\x30")
    except OSError:
        pass


class AtomicEchoPyramidBase:
    """Echo Pyramid base for AtomS3R + Echo Pyramid.

    :param i2c: I2C bus.
    :param int dev_addr: STM32 I2C address. Default 0x1A.
    :param int es8311_addr: ES8311 I2C address. Default 0x18.
    :param int i2s_port: I2S port number. Default 1.
    :param int sample_rate: Sample rate. Default 24000.
    :param int i2s_sck: I2S BCLK pin. Default 6.
    :param int i2s_ws: I2S WS pin. Default 8.
    :param int i2s_di: I2S DIN (mic) pin. Default 5.
    :param int i2s_do: I2S DOUT (spk) pin. Default 7.

    UiFlow2 Code Block:

        |init.png|

    MicroPython Code Block:

        .. code-block:: python

            from hardware import I2C, Pin
            from base import AtomicEchoPyramidBase

            i2c = I2C(1, scl=Pin(39), sda=Pin(38), freq=100000)
            echo_pyramid = AtomicEchoPyramidBase(i2c, dev_addr=0x1A, i2s_sck=6, i2s_ws=8, i2s_di=5, i2s_do=7)
            echo_pyramid.speaker.tone(2000, 500)
    """

    _instance = None

    MONO = 1
    """Mono."""

    STEREO = 2
    """Stereo."""

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(
        self,
        i2c,
        dev_addr: int = CUSTOM_DEVICE_ADDR, # default address is 0x1A
        es8311_addr: int = ES8311_ADDR,
        i2s_port: int = 1,
        sample_rate: int = 24000,
        i2s_sck: int = 6,
        i2s_ws: int = 8,
        i2s_di: int = 5,
        i2s_do: int = 7,
    ) -> None:
        # Store I2C and device address for later use (always update)
        self._i2c = i2c
        self.dev_addr = dev_addr
        
        # Check I2C device presence (always check on each run)
        if self.dev_addr not in self._i2c.scan():
            raise OSError("STM32 not found on I2C bus, please check Echo Pyramid is connected correctly")

        # Clear all RGB color to black
        self._i2c.writeto_mem(self.dev_addr, REG_STRIP1_I1_COLOR, bytes([0, 0, 0, 0] * 14))
        self._i2c.writeto_mem(self.dev_addr, REG_STRIP2_I1_COLOR, bytes([0, 0, 0, 0] * 14))

        if self._initialized:
            return

        # Si5351 clock generator
        _si5351_init(i2c)
        time.sleep_ms(50)

        # AW87559 amplifier
        _aw87559_init(i2c, dev_addr)

        # ES8311 DAC (output)
        self._es8311 = es8311.ES8311(i2c, es8311_addr)
        self.es_clk = es8311.es8311_clock_config_t()
        self.es_clk.mclk_inverted = False
        self.es_clk.sclk_inverted = False
        self.es_clk.mclk_from_mclk_pin = False
        self.es_clk.mclk_frequency = 0
        self.es_clk.sample_frequency = sample_rate
        self._es8311.init(
            self.es_clk, es8311.ES8311.ES8311_RESOLUTION_32, es8311.ES8311.ES8311_RESOLUTION_32
        )
        self._es8311.voice_volume_set(80)
        self._es8311.microphone_config(False)

        # ES7210 ADC (microphone input)
        try:
            self._es7210 = es7210.ES7210(i2c, address=ES7210_ADDR)
            self._es7210.init(
                sample_rate=sample_rate,
                master_mode=False,  # Slave mode: receive BCLK/WS from ESP32 I2S
                mic_select=es7210.INPUT_MIC1 | es7210.INPUT_MIC2,
            )
        except OSError:
            self._es7210 = None

        M5.Speaker.end()
        M5.Mic.end()

        self.spk = m5audio2.Player(
            i2s_port,
            sck=machine.Pin(i2s_sck),
            ws=machine.Pin(i2s_ws),
            sd=machine.Pin(i2s_do),
            rate=sample_rate,
            bits=16,
            channel=2,
        )

        self.mic = m5audio2.Recorder(
            i2s_port,
            sck=machine.Pin(i2s_sck),
            ws=machine.Pin(i2s_ws),
            sd=machine.Pin(i2s_di),
            rate=sample_rate,
            bits=16,
            channel=2,
        )

        self.speaker = self.spk  # Alias for echo_pyramid.py compatibility
        self._initialized = True

        # Set all rgb color to black
        self._i2c.writeto_mem(self.dev_addr, REG_STRIP1_I1_COLOR, bytes([0, 0, 0, 0] * 14))
        self._i2c.writeto_mem(self.dev_addr, REG_STRIP2_I1_COLOR, bytes([0, 0, 0, 0] * 14))

    def get_touch(self) -> tuple:
        """Get touch status.

        :return: (tp1, tp2, tp3, tp4), True=pressed False=released.

        UiFlow2 Code Block:

            |get_touch.png|

        MicroPython Code Block:

            .. code-block:: python

                tp1, tp2, tp3, tp4 = echo_pyramid.get_touch()
        """
        try:
            data = self._i2c.readfrom_mem(self.dev_addr, REG_TOUCH1_STATUS, 4)
            return (
                bool(data[0] & 0x01),
                bool(data[1] & 0x01),
                bool(data[2] & 0x01),
                bool(data[3] & 0x01),
            )
        except OSError:
            return (False, False, False, False)

    def set_rgb_brightness(self, strip: int, brightness: int, save: bool = False) -> None:
        """Set RGB strip brightness.

        :param int strip: Strip index (1 or 2).
        :param int brightness: Brightness 0~100.
        :param bool save: Save to flash.

        UiFlow2 Code Block:

            |set_rgb_brightness.png|

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.set_rgb_brightness(1, 50, False)
        """
        if strip not in (1, 2):
            return
        brightness = max(0, min(100, brightness))
        reg = REG_STRIP1_BRIGHTNESS if strip == 1 else REG_STRIP2_BRIGHTNESS
        try:
            self._i2c.writeto_mem(self.dev_addr, reg, bytes([brightness]))
            if save:
                self._i2c.writeto_mem(self.dev_addr, 0xF0, bytes([strip]))
        except OSError:
            pass

    def get_rgb_brightness(self, strip: int) -> int:
        """Get RGB strip brightness.

        :param int strip: Strip index (1 or 2).
        :return: Brightness 0~100, or 0 on error/invalid strip.

        UiFlow2 Code Block:

            |get_rgb_brightness.png|

        MicroPython Code Block:

            .. code-block:: python

                brightness = echo_pyramid.get_rgb_brightness(1)
        """
        if strip not in (1, 2):
            return 0
        reg = REG_STRIP1_BRIGHTNESS if strip == 1 else REG_STRIP2_BRIGHTNESS
        try:
            return self._i2c.readfrom_mem(self.dev_addr, reg, 1)[0]
        except OSError:
            return 0

    def set_rgb_color(self, strip: int, index: int, color: int) -> None:
        """Set single RGB LED color.

        :param int strip: Strip index (1 or 2).
        :param int index: LED index 0~13.
        :param int color: 24-bit color (R << 16 | G << 8 | B).

        UiFlow2 Code Block:

            |set_rgb_color.png|

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.set_rgb_color(1, 0, 0x33CCFF)
        """
        if not (1 <= strip <= 2 and 0 <= index <= 13):
            return
        base = REG_STRIP1_I1_COLOR if strip == 1 else REG_STRIP2_I1_COLOR
        reg_addr = base + (index << 2)
        try:
            self._i2c.writeto_mem(
                self.dev_addr,
                reg_addr,
                bytes((color & 0xFF, (color >> 8) & 0xFF, (color >> 16) & 0xFF)),
            )
        except OSError:
            pass

    def get_rgb_color(self, strip: int, index: int) -> int:
        """Get single RGB LED color.

        :param int strip: Strip index (1 or 2).
        :param int index: LED index 0~13.
        :return: 24-bit color (R << 16 | G << 8 | B), or 0 on error.

        UiFlow2 Code Block:

            |get_rgb_color.png|

        MicroPython Code Block:

            .. code-block:: python

                color = echo_pyramid.get_rgb_color(1, 0)
        """
        if not (1 <= strip <= 2 and 0 <= index <= 13):
            return 0
        base = REG_STRIP1_I1_COLOR if strip == 1 else REG_STRIP2_I1_COLOR
        reg_addr = base + (index << 2)
        try:
            data = self._i2c.readfrom_mem(self.dev_addr, reg_addr, 3)
            return (data[2] << 16) | (data[1] << 8) | data[0]
        except OSError:
            return 0

    def set_addr(self, new_addr: int) -> None:
        """Set STM32 I2C address. Takes effect after a short delay.

        :param int new_addr: New address 0x08~0x77.

        UiFlow2 Code Block:

            |set_addr.png|

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.set_addr(0x1B)
        """
        new_addr = max(0x08, min(0x77, new_addr))
        try:
            self._i2c.writeto_mem(self.dev_addr, REG_DEVICE_ADDR, bytearray([new_addr]))
            self.dev_addr = new_addr
            time.sleep_ms(20)
        except OSError:
            pass

    def get_addr(self) -> int:
        """Get current STM32 I2C address.

        :return: I2C address, or 0 on error.

        UiFlow2 Code Block:

            |get_addr.png|

        MicroPython Code Block:

            .. code-block:: python

                addr = echo_pyramid.get_addr()
        """
        try:
            return self._i2c.readfrom_mem(self.dev_addr, REG_DEVICE_ADDR, 1)[0]
        except OSError:
            return 0

    def get_firmware_version(self) -> int:
        """Get STM32 firmware version.

        :return: Version number, or 0 on error.

        UiFlow2 Code Block:

            |get_firmware_version.png|

        MicroPython Code Block:

            .. code-block:: python

                ver = echo_pyramid.get_firmware_version()
        """
        try:
            return self._i2c.readfrom_mem(self.dev_addr, REG_FIRMWARE_VERSION, 1)[0]
        except OSError:
            return 0

    def get_input_voltage(self) -> int:
        """Get input voltage (from STM32 ADC).

        :return: Voltage in mV, or 0 on error.

        UiFlow2 Code Block:

            |get_input_voltage.png|

        MicroPython Code Block:

            .. code-block:: python

                mv = echo_pyramid.get_input_voltage()
        """
        try:
            data = self._i2c.readfrom_mem(self.dev_addr, REG_INPUT_VOLTAGE_L, 2)
            return (data[1] << 8) | data[0]
        except OSError:
            return 0

    def set_mute(self, mute: bool) -> None:
        """Mute or unmute speaker (AW87559).

        :param bool mute: True to mute, False to unmute.

        UiFlow2 Code Block:

            |set_mute.png|

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.set_mute(True)
        """
        _aw87559_set_speaker(self._i2c, not mute)

    def change_sample_rate(self, sample_rate: int) -> None:
        """Change audio sample rate. Affects playback and recording.

        :param int sample_rate: Sample rate in Hz (e.g. 16000, 24000).

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.change_sample_rate(24000)
        """
        self.es_clk.sample_frequency = sample_rate
        self._es8311.clock_config(self.es_clk, es8311.ES8311.ES8311_RESOLUTION_32)
        if self._es7210 is not None:
            self._es7210.config_sample(sample_rate)

    def play_wav_file(self, file: str) -> None:
        """Play a WAV file from storage.

        :param str file: WAV file path.

        UiFlow2 Code Block:

            |play_wav_file.png|

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.play_wav_file("/flash/res/audio/test.wav")
        """
        if self.mic.is_running():
            self.mic.deinit()
        self.set_mute(False)
        self.spk.play_wav_file(file)

    def tone(self, freq: int, duration: int) -> None:
        """Play a beep tone.

        :param int freq: Frequency in Hz.
        :param int duration: Duration in milliseconds.

        UiFlow2 Code Block:

            |tone.png|

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.tone(1000, 200)
        """
        if self.mic.is_running():
            self.mic.deinit()
        self.set_mute(False)
        self.spk.tone(freq, duration)

    def play_wav(self, buf: bytes, duration: int = -1) -> None:
        """Play WAV data from buffer.

        :param bytes buf: WAV data.
        :param int duration: Duration in ms, or -1 for full buffer.

        UiFlow2 Code Block:

            |play_wav.png|

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.play_wav(wav_bytes, duration=1000)
        """
        if self.mic.is_running():
            self.mic.deinit()
        self.set_mute(False)
        self.spk.play_wav(buf, duration=duration)

    def play_raw(
        self, buf: bytes, rate: int = 16000, bits: int = 16, channel: int = 2, duration: int = -1
    ) -> None:
        """Play raw PCM data.

        :param bytes buf: Raw PCM data.
        :param int rate: Sample rate in Hz.
        :param int bits: Bit depth (e.g. 16).
        :param int channel: Number of channels (1 or 2).
        :param int duration: Duration in ms, or -1 for full buffer.

        UiFlow2 Code Block:

            |play_raw.png|

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.play_raw(pcm_bytes, rate=16000, bits=16, channel=2)
        """
        if self.mic.is_running():
            self.mic.deinit()
        self.set_mute(False)
        self.spk.play_raw(buf, rate=rate, bits=bits, channel=channel, duration=duration)

    def pause(self) -> None:
        """Pause playback.

        UiFlow2 Code Block:

            |pause.png|

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.pause()
        """
        self.spk.pause()

    def resume(self) -> None:
        """Resume playback.

        UiFlow2 Code Block:

            |resume.png|

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.resume()
        """
        self.spk.resume()

    def stop(self) -> None:
        """Stop playback.

        UiFlow2 Code Block:

            |stop.png|

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.stop()
        """
        self.spk.stop()

    def get_volume(self) -> int:
        """Get speaker volume.

        :return: Current volume value.

        UiFlow2 Code Block:

            |get_volume.png|

        MicroPython Code Block:

            .. code-block:: python

                volume = echo_pyramid.get_volume()
        """
        return self._es8311.voice_volume_get()

    def set_volume(self, volume: int) -> None:
        """Set speaker volume.

        :param int volume: Volume value.

        UiFlow2 Code Block:

            |set_volume.png|

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.set_volume(60)
        """
        self._es8311.voice_volume_set(volume)

    def record_wav_file(
        self,
        path: str,
        rate: int = 16000,
        bits: int = 16,
        channel: int = 2,
        duration: int = 3000,
    ) -> None:
        """Record audio to a WAV file.

        :param str path: Output file path.
        :param int rate: Sample rate in Hz.
        :param int bits: Bit depth.
        :param int channel: Channel mode. Use ``MONO`` or ``STEREO``.
        :param int duration: Duration in milliseconds.

        UiFlow2 Code Block:

            |record_wav_file.png|

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.record_wav_file("/flash/res/audio/test.wav", rate=16000, bits=16, channel=echo_pyramid.STEREO, duration=3000)
        """
        self.spk.deinit()
        self.set_mute(True)
        self.change_sample_rate(rate)
        self.mic.record_wav_file(path, rate=rate, bits=bits, channel=channel, duration=duration)

    def record(
        self,
        rate: int = 16000,
        bits: int = 16,
        channel: int = 2,
        duration: int = 3000,
    ):
        """Record audio to PCM buffer.

        :param int rate: Sample rate in Hz.
        :param int bits: Bit depth.
        :param int channel: Number of channels.
        :param int duration: Duration in milliseconds.
        :return: Record result (implementation-dependent).

        UiFlow2 Code Block:

            |record.png|

        MicroPython Code Block:

            .. code-block:: python

                buf = echo_pyramid.record(rate=16000, bits=16, channel=2, duration=3000)
        """
        self.spk.deinit()
        self.set_mute(True)
        self.change_sample_rate(rate)
        return self.mic.record(rate=rate, bits=bits, channel=channel, duration=duration)

    @property
    def pcm_buffer(self) -> bytes:
        """PCM buffer from the microphone (read-only). Available after recording.

        UiFlow2 Code Block:

            |pcm_buffer.png|

        MicroPython Code Block:

            .. code-block:: python

                data = echo_pyramid.pcm_buffer
        """
        return self.mic.pcm_buffer

    def deinit(self) -> None:
        """Deinitialize speaker and microphone, and mute output.

        MicroPython Code Block:

            .. code-block:: python

                echo_pyramid.deinit()
        """
        self.spk.deinit()
        self.mic.deinit(True)
        self.set_mute(True)
