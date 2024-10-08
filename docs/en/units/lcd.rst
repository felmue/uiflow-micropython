LCD Unit
========

.. include:: ../refs/unit.lcd.ref


Unit LCD is a 1.14 inch color LCD expansion screen unit. It adopts ST7789V2
drive scheme, the resolution is 135*240, and it supports
RGB666 display (262,144 colors). The internal integration of ESP32-PICO control
core (built-in firmware, display development is more convenient), support
through I2C (addr: 0x3E) communication interface for control and firmware
upgrades. The back of the screen is integrated with a magnetic design,
which can easily adsorb the metal surface for fixing. The LCD screen extension
is suitable for embedding in various instruments or control devices that need
to display simple content as a display panel.


Support the following products:

    |LCDUnit|


Micropython example::
    from unit import LCDUnit
    from hardware import *
    i2c0 = I2C(0, scl=Pin(33), sda=Pin(32), freq=100000)
    display = LCDUnit(i2c).display
    
    display.clear(0xffffff) # Clear screen

.. only:: builder_html

class LCDUnit
-------------

Constructors
------------

.. class:: LCDUnit(port, address, freq)

    Initialize the Unit LCD

    :param tuple port: The port to which the Unit LCDUnit is connected. port[0]: scl pin, port[1]: sda pin.
    :param int|list|tuple address: I2C address of the Unit LCDUnit, default is 0x3D.
    :param int freq: I2C frequency of the Unit LCDUnit.

    UIFLOW2:

        |init.svg|


Methods
-------





