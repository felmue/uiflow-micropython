# SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT
"""
@File    :   heart.py
@Time    :   2024/5/7
@Author  :   TONG YIHAN
@E-mail  :   icyqwq@gmail.com
@License :   (C)Copyright 2015-2024, M5STACK
"""

# Import necessary libraries
from machine import I2C
from cdriver import max30102
import struct
import _thread, time


class HeartHat:
    """! HEART RATE HAT is a blood oxygen heart rate sensor.

    @en max30102 is a complete pulse oximetry and heart-rate sensor system solution designed for the demanding requirements of wearable devices.
    @cn max30102是一种完整的脉搏血氧饱和度和心率传感器系统解决方案，专为可穿戴设备的严格要求而设计。

    @color #0FE6D7
    @link https://docs.m5stack.com/en/hat/hat_heart_rate
    @image https://static-cdn.m5stack.com/resource/docs/products/hat/hat_heart_rate/hat_heart_rate_01.webp
    @category hat

    @example
        from hat import HeartHat
        from hardware import I2C
        i2c = I2C(1, scl=26, sda=0)
        heart = HeartHat(i2c)
        heart.start()
        heart.get_heart_rate();heart.get_spo2()


    @attr MODE_HR_ONLY Detect heart rate only.
    @attr MODE_SPO2_HR Detect heart rate and SpO2.
    """

    MODE_HR_ONLY = 0x02
    MODE_SPO2_HR = 0x03

    LED_CURRENT_0MA = 0x00
    LED_CURRENT_4_4MA = 0x01
    LED_CURRENT_7_6MA = 0x02
    LED_CURRENT_11MA = 0x03
    LED_CURRENT_14_2MA = 0x04
    LED_CURRENT_17_4MA = 0x05
    LED_CURRENT_20_8MA = 0x06
    LED_CURRENT_24MA = 0x07
    LED_CURRENT_27_1MA = 0x08
    LED_CURRENT_30_6MA = 0x09
    LED_CURRENT_33_8MA = 0x0A
    LED_CURRENT_37MA = 0x0B
    LED_CURRENT_40_2MA = 0x0C
    LED_CURRENT_43_6MA = 0x0D
    LED_CURRENT_46_8MA = 0x0E
    LED_CURRENT_50MA = 0x0F

    PULSE_WIDTH_200US_ADC_13 = 0x00
    PULSE_WIDTH_400US_ADC_14 = 0x01
    PULSE_WIDTH_800US_ADC_15 = 0x02
    PULSE_WIDTH_1600US_ADC_16 = 0x03

    SAMPLING_RATE_50HZ = 0x00
    SAMPLING_RATE_100HZ = 0x01
    SAMPLING_RATE_167HZ = 0x02
    SAMPLING_RATE_200HZ = 0x03
    SAMPLING_RATE_400HZ = 0x04
    SAMPLING_RATE_600HZ = 0x05
    SAMPLING_RATE_800HZ = 0x06
    SAMPLING_RATE_1000HZ = 0x07

    def __init__(self, i2c: I2C, address: int | list | tuple = 0x57) -> None:
        """! Initialize the HeartHat.

        @param i2c I2C port to use.
        @param address I2C address of the HeartHat.
        """
        self.i2c = i2c
        self.addr = address
        self._available()
        max30102.init(i2c, address)
        self._task_running = False

    def _thread_task(self) -> None:
        while self._task_running:
            max30102.update()
            time.sleep_ms(5)

    def _available(self) -> None:
        """! Check if HeartHat is available on the I2C bus.

        Raises:
            Exception: If the HeartHat is not found.
        """
        if self.addr not in self.i2c.scan():
            raise Exception("HeartHat not found on I2C bus.")

    def stop(self) -> None:
        """! Stop the HeartHat.

        @en %1 Stop the HeartHat update.
        @cn %1 停止HeartHat更新。

        """
        self._task_running = False

    def start(self) -> None:
        """! Start the HeartHat.

        @en %1 Start the HeartHat update.
        @cn %1 启动HeartHat更新。

        """
        self._task_running = True
        _thread.start_new_thread(self._thread_task, ())

    def deinit(self) -> None:
        """! Deinitialize the HeartHat.

        @en %1 Deinitialize the HeartHat.
        @cn %1 释放HeartHat。

        """
        self.stop()
        time.sleep_ms(50)
        max30102.deinit()

    def get_heart_rate(self) -> int:
        """! Get the heart rate.

        @en %1 Get the heart rate.
        @cn %1 获取心率。

        @return Heart rate.
        """
        return max30102.get_heart_rate()

    def get_spo2(self) -> int:
        """! Get the SpO2.

        @en %1 Get the SpO2.
        @cn %1 获取血氧饱和度。

        @return SpO2.
        """
        return max30102.get_spo2()

    def get_ir(self) -> int:
        """! Get the IR value.

        @en %1 Get the IR value.
        @cn %1 获取红外值。

        @return IR value.
        """
        return max30102.get_ir()

    def get_red(self) -> int:
        """! Get the red value.

        @en %1 Get the red value.
        @cn %1 获取红光值。

        @return Red value.
        """
        return max30102.get_red()

    def set_mode(self, mode: int) -> None:
        """! Set the mode of the HeartHat.

        @en %1 Set the mode of the HeartHat to %2.
        @cn %1 将HeartHat的模式设置为%2。

        @param mode [field_dropdown] The detect mode of the HeartHat.
            @options {
                    [Only heart rate, HeartHat.MODE_HR_ONLY],
                    [Heart rate and SpO2, HeartHat.MODE_SPO2_HR]
            }
        """
        max30102.set_mode(mode)

    def set_led_current(self, red_current: int, ir_current) -> None:
        """! Set the LED current of the HeartHat.

        @en %1 Set the LED current of the HeartHat to %2.
        @cn %1 将HeartHat的LED电流设置为%2。

        @param red_current [field_dropdown] The Red current of the HeartHat.
            @options {
                    [0mA, HeartHat.LED_CURRENT_0MA],
                    [4.4mA, HeartHat.LED_CURRENT_4_4MA],
                    [7.6mA, HeartHat.LED_CURRENT_7_6MA],
                    [11mA, HeartHat.LED_CURRENT_11MA],
                    [14.2mA, HeartHat.LED_CURRENT_14_2MA],
                    [17.4mA, HeartHat.LED_CURRENT_17_4MA],
                    [20.8mA, HeartHat.LED_CURRENT_20_8MA],
                    [24mA, HeartHat.LED_CURRENT_24MA],
                    [27.1mA, HeartHat.LED_CURRENT_27_1MA],
                    [30.6mA, HeartHat.LED_CURRENT_30_6MA],
                    [33.8mA, HeartHat.LED_CURRENT_33_8MA],
                    [37mA, HeartHat.LED_CURRENT_37MA],
                    [40.2mA, HeartHat.LED_CURRENT_40_2MA],
                    [43.6mA, HeartHat.LED_CURRENT_43_6MA],
                    [46.8mA, HeartHat.LED_CURRENT_46_8MA],
                    [50mA, HeartHat.LED_CURRENT_50MA]
            }
        @param ir_current [field_dropdown] The IR current of the HeartHat.
            @options {
                    [0mA, HeartHat.LED_CURRENT_0MA],
                    [4.4mA, HeartHat.LED_CURRENT_4_4MA],
                    [7.6mA, HeartHat.LED_CURRENT_7_6MA],
                    [11mA, HeartHat.LED_CURRENT_11MA],
                    [14.2mA, HeartHat.LED_CURRENT_14_2MA],
                    [17.4mA, HeartHat.LED_CURRENT_17_4MA],
                    [20.8mA, HeartHat.LED_CURRENT_20_8MA],
                    [24mA, HeartHat.LED_CURRENT_24MA],
                    [27.1mA, HeartHat.LED_CURRENT_27_1MA],
                    [30.6mA, HeartHat.LED_CURRENT_30_6MA],
                    [33.8mA, HeartHat.LED_CURRENT_33_8MA],
                    [37mA, HeartHat.LED_CURRENT_37MA],
                    [40.2mA, HeartHat.LED_CURRENT_40_2MA],
                    [43.6mA, HeartHat.LED_CURRENT_43_6MA],
                    [46.8mA, HeartHat.LED_CURRENT_46_8MA],
                    [50mA, HeartHat.LED_CURRENT_50MA]
            }
        """
        max30102.set_led_current(red_current, ir_current)

    def set_pulse_width(self, pulse_width: int) -> None:
        """! Set the pulse width of the HeartHat.

        @en %1 Set the pulse width of the HeartHat to %2.
        @cn %1 将HeartHat的脉冲宽度设置为%2。

        @param pulse_width [field_dropdown] The pulse width of the HeartHat.
            @options {
                    [200us, HeartHat.PULSE_WIDTH_200US_ADC_13],
                    [400us, HeartHat.PULSE_WIDTH_400US_ADC_14],
                    [800us, HeartHat.PULSE_WIDTH_800US_ADC_15],
                    [1600us, HeartHat.PULSE_WIDTH_1600US_ADC_16]
            }
        """
        max30102.set_pulse_width(pulse_width)

    def set_sampling_rate(self, sampling_rate: int) -> None:
        """! Set the sampling rate of the HeartHat.

        @en %1 Set the sampling rate of the HeartHat to %2.
        @cn %1 将HeartHat的采样率设置为%2。

        @param sampling_rate [field_dropdown] The sampling rate of the HeartHat.
            @options {
                    [50Hz, HeartHat.SAMPLING_RATE_50HZ],
                    [100Hz, HeartHat.SAMPLING_RATE_100HZ],
                    [167Hz, HeartHat.SAMPLING_RATE_167HZ],
                    [200Hz, HeartHat.SAMPLING_RATE_200HZ],
                    [400Hz, HeartHat.SAMPLING_RATE_400HZ],
                    [600Hz, HeartHat.SAMPLING_RATE_600HZ],
                    [800Hz, HeartHat.SAMPLING_RATE_800HZ],
                    [1000Hz, HeartHat.SAMPLING_RATE_1000HZ]
            }
        """
        max30102.set_sampling_rate(sampling_rate)
