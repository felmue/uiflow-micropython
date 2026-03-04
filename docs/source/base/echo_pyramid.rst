.. py:currentmodule:: base.echo_pyramid

Atomic Echo Pyramid Base
========================

.. sku: A167

.. include:: ../refs/base.echo_pyramid.ref

The following products are supported:

    |Atomic Echo Pyramid Base|

Below is the detailed support for Atomic Echo Pyramid Base on the host:

.. table::
    :widths: auto
    :align: center

    +-----------------+---------------------------+
    |Controller       | Atomic Echo Pyramid Base  |
    +=================+===========================+
    | Atom Echo       | |O|                       |
    +-----------------+---------------------------+
    | Atom Lite       | |S|                       |
    +-----------------+---------------------------+
    | Atom Matrix     | |S|                       |
    +-----------------+---------------------------+
    | AtomS3          | |S|                       |
    +-----------------+---------------------------+
    | AtomS3 Lite     | |S|                       |
    +-----------------+---------------------------+
    | AtomS3R         | |S|                       |
    +-----------------+---------------------------+
    | AtomS3R-CAM     | |S|                       |
    +-----------------+---------------------------+
    | AtomS3R-Ext     | |S|                       |
    +-----------------+---------------------------+

.. |S| unicode:: U+2705
.. |O| unicode:: U+2B55


The ``AtomicEchoPyramidBase`` class controls the Echo Pyramid base for Atom Series, providing audio playback/recording, touch input, and dual RGB LED strips.

.. note::

    Power must be supplied to both the EchoPyramid base and the Atom controller.

UiFlow2 Example
---------------

LED Strip Effects
^^^^^^^^^^^^^^^^^

Open the |atoms3r_echopyramid_led_strip_example.m5f2| project in UiFlow2.

This example demonstrates breathing and flowing effects on both RGB strips.

UiFlow2 Code Block:

    |led_strip_example.png|

Example output:

    None


Touch Control
^^^^^^^^^^^^^

Open the |atoms3r_echopyramid_touch_example.m5f2| project in UiFlow2.

This example uses the capacitive touch pads to light different LED segments.

UiFlow2 Code Block:

    |touch_example.png|

Example output:

    None


Audio Record And Playback
^^^^^^^^^^^^^^^^^^^^^^^^^

Open the |atoms3r_echopyramid_audio_example.m5f2| project in UiFlow2.

This example records a short WAV clip and then plays it back.

UiFlow2 Code Block:

    |audio_example.png|

Example output:

    None


Audio Beep
^^^^^^^^^^

Open the |atoms3r_echopyramid_audio_beep_example.m5f2| project in UiFlow2.

This example plays a random beep tone on each touch.

UiFlow2 Code Block:

    |audio_beep_example.png|

Example output:

    None


USB Voltage
^^^^^^^^^^^

Open the |atoms3r_echopyramid_usb_voltage_example.m5f2| project in UiFlow2.

This example reads USB input voltage (mV) from the base and displays it.

UiFlow2 Code Block:

    |usb_voltage_example.png|

Example output:

    None


MicroPython Example
-------------------

LED Strip Effects
^^^^^^^^^^^^^^^^^

This example demonstrates breathing and flowing effects on both RGB strips.

MicroPython Code Block:

    .. literalinclude:: ../../../examples/base/echo_pyramid/atoms3r_echopyramid_led_strip_example.py
        :language: python
        :linenos:

Example output:

    None


Touch Control
^^^^^^^^^^^^^

This example uses the capacitive touch pads to light different LED segments.

MicroPython Code Block:

    .. literalinclude:: ../../../examples/base/echo_pyramid/atoms3r_echopyramid_touch_example.py
        :language: python
        :linenos:

Example output:

    None


Audio Record And Playback
^^^^^^^^^^^^^^^^^^^^^^^^^

This example records a short WAV clip and then plays it back.

MicroPython Code Block:

    .. literalinclude:: ../../../examples/base/echo_pyramid/atoms3r_echopyramid_audio_example.py
        :language: python
        :linenos:

Example output:

    None


Audio Beep
^^^^^^^^^^

This example plays a random beep tone on each touch.

MicroPython Code Block:

    .. literalinclude:: ../../../examples/base/echo_pyramid/atoms3r_echopyramid_audio_beep_example.py
        :language: python
        :linenos:

Example output:

    None


USB Voltage
^^^^^^^^^^^

This example reads USB input voltage (mV) from the base and displays it.

MicroPython Code Block:

    .. literalinclude:: ../../../examples/base/echo_pyramid/atoms3r_echopyramid_usb_voltage_example.py
        :language: python
        :linenos:

Example output:

    None


API
---

AtomicEchoPyramidBase
^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: base.echo_pyramid.AtomicEchoPyramidBase
    :members:
    :member-order: bysource
