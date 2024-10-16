import ustruct
import math
import time


class PCA9685:
    def __init__(self, i2c, address=0x40):
        self.i2c = i2c
        self.address = address
        self.reset()

    def _write(self, address, value):
        self.i2c.writeto_mem(self.address, address, bytearray([value]))

    def _read(self, address):
        return self.i2c.readfrom_mem(self.address, address, 1)[0]

    def reset(self):
        """
        note:
            en: Reset the Servo Driver.
            cn: 重置舵机驱动器。
        """
        self._write(0x00, 0x00)  # Mode1

    def freq(self, freq=None):
        """
        note:
            en: Set the PWM frequency.
            cn: 设置PWM频率。

        params:
            freq:
              note: The PWM frequency in Hz.
        """
        if freq is None:
            return int(25000000.0 / 4096 / (self._read(0xFE) - 0.5))
        prescale = int(25000000.0 / 4096.0 / freq + 0.5)
        old_mode = self._read(0x00)  # Mode 1
        self._write(0x00, (old_mode & 0x7F) | 0x10)  # Mode 1, sleep
        self._write(0xFE, prescale)  # Prescale
        self._write(0x00, old_mode)  # Mode 1
        time.sleep_us(5)
        self._write(0x00, old_mode | 0xA1)  # Mode 1, autoincrement on

    def pwm(self, index, on=None, off=None):
        """
        note:
            en: Set the PWM value.
            cn: 设置PWM值。

        params:
            index:
              note: The channel index.
            on:
              note: The ON time.
            off:
              note: The OFF time.

        """

        if on is None or off is None:
            data = self.i2c.readfrom_mem(self.address, 0x06 + 4 * index, 4)
            return ustruct.unpack("<HH", data)
        data = ustruct.pack("<HH", on, off)
        self.i2c.writeto_mem(self.address, 0x06 + 4 * index, data)

    def duty(self, index, value=None, invert=False):
        """
        note:
            en: Set the PWM duty cycle.
            cn: 设置PWM占空比。

        params:
            index:
              note: The channel index.
            value:
              note: The PWM value.
            invert:
              note: Invert the PWM value.
        """
        if value is None:
            pwm = self.pwm(index)
            if pwm == (0, 4096):
                value = 0
            elif pwm == (4096, 0):
                value = 4095
            value = pwm[1]
            if invert:
                value = 4095 - value
            return value
        if not 0 <= value <= 4095:
            raise ValueError("Out of range")
        if invert:
            value = 4095 - value
        if value == 0:
            self.pwm(index, 0, 4096)
        elif value == 4095:
            self.pwm(index, 4096, 0)
        else:
            self.pwm(index, 0, value)


class Servos:
    def __init__(self, i2c, address=0x40, freq=50, min_us=400, max_us=2350, degrees=180):
        """
        note:
            en: Create a Servo instance.
            cn: 创建一个舵机实例。

        params:
            i2c:
              note: The I2C bus.
            address:
              note: The I2C address.
            freq:
              note: The PWM frequency in Hz.
            min_us:
              note: The minimum pulse width in microseconds.
            max_us:
              note: The maximum pulse width in microseconds.
            degrees:
              note: The maximum angle in degrees.

        """
        self.period = 1000000 / freq
        self.min_duty = self._us2duty(min_us)
        self.max_duty = self._us2duty(max_us)
        self.degrees = degrees
        self.freq = freq
        self.pca9685 = PCA9685(i2c, address)
        self.pca9685.freq(freq)

    def _us2duty(self, value):
        return int(4095 * value / self.period)

    def position(self, index, degrees=None, radians=None, us=None, duty=None):
        """
        note:
            en: Set the servo position.
            cn: 设置舵机位置。

        params:
            index:
              note: The channel index.
            degrees:
              note: The angle in degrees.
            radians:
              note: The angle in radians.
            us:
              note: The pulse width in microseconds.
            duty:
              note: The duty cycle in percent.
        """
        span = self.max_duty - self.min_duty
        if degrees is not None:
            duty = self.min_duty + span * degrees / self.degrees
        elif radians is not None:
            duty = self.min_duty + span * radians / math.radians(self.degrees)
        elif us is not None:
            duty = self._us2duty(us)
        elif duty is not None:
            duty = self.min_duty + span * duty / 100
        else:
            return self.pca9685.duty(index)
        duty = min(self.max_duty, max(self.min_duty, int(duty)))
        self.pca9685.duty(index, duty)

    def release(self, index):
        """
        note:
            en: Release the servo.
            cn: 释放舵机。

        params:
            index:
              note: The channel index.
        """
        self.pca9685.duty(index, 0)


"""
if __name__ == "__main__":

    import i2c_bus
    i2c = i2c_bus.get(i2c_bus.PORTA)
    servo = Servos(i2c)
"""
