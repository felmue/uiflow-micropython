# SPDX-FileCopyrightText: 2024 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT

package(
    "driver",
    (
        "__init__.py",
        "fpc1020a/fpc1020a/__init__.py",
        "fpc1020a/fpc1020a/api.py",
        "fpc1020a/fpc1020a/types.py",
        "ir/__init__.py",
        "ir/nec.py",
        "ir/receiver.py",
        "ir/transmitter.py",
        "mfrc522/__init__.py",
        "mfrc522/cmd.py",
        "mfrc522/firmware.py",
        "mfrc522/reg.py",
        "neopixel/__init__.py",
        "neopixel/sk6812.py",
        "neopixel/ws2812.py",
        "rotary/__init__.py",
        "rotary/rotary_irq_esp.py",
        "rotary/rotary.py",
        "ads1100.py",
        "asr650x.py",
        "bh1750.py",
        "bh1750fvi.py",
        "bmp280.py",
        "button.py",
        "checksum.py",
        "dht12.py",
        "mcp4725.py",
        "mlx90614.py",
        "pca9554.py",
        "pcf8563.py",
        "qmp6988.py",
        "scd40.py",
        "sgp30.py",
        "sh1107.py",
        "sht4x.py",
        "sht30.py",
        "tcs3472.py",
        "timer_thread.py",
        "vl53l0x.py",
        "modbus/master/__init__.py",
        "modbus/master/uConst.py",
        "modbus/master/uFunctions.py",
        "modbus/master/uSerial.py",
        "paj7620.py",
        "mlx90640.py",
        "timezone.py",
        "vl53l1x.py",
        "simcom/__init__.py",
        "simcom/common.py",
        "simcom/sim7080.py",
        "sht20.py",
    ),
    base_path="..",
    opt=0,
)
