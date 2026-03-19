
.. py:currentmodule:: module

Servo2 Module
=============

.. include:: ../refs/module.servo2.ref

Servo2 is an updated servo driver module in the M5Stack stackable module series. It uses a PCA9685 16-channel PWM controller to drive up to 16 servos simultaneously. Power input is 6–12 V DC, with two SY8368AQQC chips for step-down regulation.

Support the following products:

    |Servo2Module|

UiFlow2 Example
---------------

Servo angle control
^^^^^^^^^^^^^^^^^^^

Open the |m5core_module_servo2_example.m5f2| project in UiFlow2.

This example initializes the Servo2 module on the I2C bus, drives two servo channels, and shows the current angle on screen. Button A sets both servos to 0°, Button B to 45°, and Button C to 90°; one channel is released after setup.

UiFlow2 Code Block:

    |m5core_module_servo2_example.png|

Example output:

    None

MicroPython Example
-------------------

Servo angle control
^^^^^^^^^^^^^^^^^^^

This example initializes the Servo2 module on the I2C bus, drives two servo channels, and shows the current angle on screen. Button A sets both servos to 0°, Button B to 45°, and Button C to 90°; one channel is released after setup.

MicroPython Code Block:

    .. literalinclude:: ../../../examples/module/servo2/m5core_module_servo2_example.py
        :language: python
        :linenos:

Example output:

    None

**API**
-------

Servo2Module
^^^^^^^^^^^^

.. class:: Servo2Module(address=0x40, freq=50, min_us=400, max_us=2350, degrees=180)

    Create a Servo2 module instance on the I2C bus.

    :param int address: I2C address of the PCA9685 (default 0x40).
    :param int freq: PWM frequency in Hz (default 50).
    :param int min_us: Minimum pulse width in microseconds (default 400).
    :param int max_us: Maximum pulse width in microseconds (default 2350).
    :param int degrees: Maximum angle in degrees (default 180).

    UiFlow2 Code Block:

        |init.png|

    MicroPython Code Block:

        .. code-block:: python

            from module import Servo2Module

            servo2 = Servo2Module(address=0x40, freq=50, min_us=400, max_us=2350, degrees=180)

    .. py:method:: Servo2Module.position(index, degrees=None, radians=None, us=None, duty=None)

        Set the servo position for the given channel.

        :param int index: Channel index (0-15).
        :param float degrees: Angle in degrees (optional).
        :param float radians: Angle in radians (optional).
        :param int us: Pulse width in microseconds (optional).
        :param float duty: Duty cycle in percent (optional). Exactly one of *degrees*, *radians*, *us*, or *duty* may be given.

        UiFlow2 Code Block:

            |set_degrees.png|

            |set_duty.png|

            |set_pulse_width.png|

            |set_radians.png|

        MicroPython Code Block:

            .. code-block:: python

                servo2.position(0, degrees=90)
                servo2.position(0, duty=50)
                servo2.position(0, us=1500)
                servo2.position(0, radians=1.57)

    .. py:method:: Servo2Module.release(index)

        Release the servo (stop driving the channel).

        :param int index: Channel index (0–15).

        UiFlow2 Code Block:

            |release.png|

        MicroPython Code Block:

            .. code-block:: python

                servo2.release(0)

    .. py:method:: Servo2Module.deinit()

        Release the module. No-op for Servo2Module; provided for compatibility.

        MicroPython Code Block:

            .. code-block:: python

                servo2.deinit()
