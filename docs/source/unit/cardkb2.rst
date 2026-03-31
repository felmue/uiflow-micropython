CardKB2 Unit
============

.. include:: ../refs/unit.cardkb2.ref

This is the driver library of CardKB2 Unit, which is used to obtain key input data.

Support the following products:

    |CardKB2 Unit|    

UiFlow2 Example
---------------

CardKB2 I2C Mode
^^^^^^^^^^^^^^^^^^^

Open the |cardkb2_i2c_core2_example.m5f2| project in UiFlow2.

This example display the keyboard input on the screen and serial.

UiFlow2 Code Block:

    |i2c_example.png|

Example output:

    input key char

CardKB2 UART Mode
^^^^^^^^^^^^^^^^^^^

Open the |cardkb2_uart_core2_example.m5f2| project in UiFlow2.

This example display the keyboard input on the screen and serial.

UiFlow2 Code Block:

    |uart_example.png|

Example output:

    input key char and state


CardKB2 ESP-NOW Mode
^^^^^^^^^^^^^^^^^^^^^

Open the |cardkb2_espnow_core2_example.m5f2| project in UiFlow2.

This example display the keyboard input on the screen and serial.

UiFlow2 Code Block:

    |espnow_example.png|

Example output:

    input key char and state


MicroPython Example
-------------------

CardKB2 I2C Mode
^^^^^^^^^^^^^^^^^^^^

This example display the keyboard input on the screen and serial.

MicroPython Code Block:

    .. literalinclude:: ../../../examples/unit/cardkb2/cardkb2_i2c_core2_example.py
        :linenos:

Example output:

    input key char


CardKB2 UART Mode
^^^^^^^^^^^^^^^^^^^^

This example display the keyboard input on the screen and serial.

MicroPython Code Block:

    .. literalinclude:: ../../../examples/unit/cardkb2/cardkb2_uart_core2_example.py
        :linenos:

Example output:

    input key char and state


CardKB2 ESP-NOW Mode
^^^^^^^^^^^^^^^^^^^^

This example display the keyboard input on the screen and serial.

MicroPython Code Block:

    .. literalinclude:: ../../../examples/unit/cardkb2/cardkb2_espnow_core2_example.py
        :linenos:

Example output:

    input key char and state


**API**
-------

Class CardKB2Unit
^^^^^^^^^^^^^^^^^^

.. autoclass:: unit.cardkb.CardKBUnit
    :members:

.. autoclass:: unit.cardkb.CardKBBase
    :members:

.. autoclass:: unit.cardkb.CardKBI2C
    :members:

.. autoclass:: unit.cardkb.CardKBUART
    :members:

.. autoclass:: unit.cardkb.CardKBESPNOW
    :members: