IR
===

.. include:: ../refs/hardware.ir.ref

IR is used to control the infrared receiving/transmitting tube built into the host device.

The specific support of the host for IR is as follows:

.. table::
    :widths: auto
    :align: center

    +-------------------+-----------------+-------------+
    | Controller        | IR Transmitter  | IR Receiver |
    +===================+=================+=============+
    | Atom Lite         | |S|             |             |
    +-------------------+-----------------+-------------+
    | Atom Matrix       | |S|             |             |
    +-------------------+-----------------+-------------+
    | Atom U            | |S|             |             |
    +-------------------+-----------------+-------------+
    | AtomS3 Lite       | |S|             |             |
    +-------------------+-----------------+-------------+
    | AtomS3U           | |S|             |             |
    +-------------------+-----------------+-------------+
    | StickC            | |S|             |             |
    +-------------------+-----------------+-------------+
    | StickC-Plus       | |S|             |             |
    +-------------------+-----------------+-------------+
    | StickC-Plus2      | |S|             |             |
    +-------------------+-----------------+-------------+
    | Cardputer         | |S|             |             |
    +-------------------+-----------------+-------------+
    | Capsule           | |S|             |             |
    +-------------------+-----------------+-------------+
    | StickS3           | |S|             | |S|         |
    +-------------------+-----------------+-------------+

.. |S| unicode:: U+2714

UiFlow2 Example 
---------------

IR Transmission
^^^^^^^^^^^^^^^

Open the |sticks3_ir_tx_example.m5f2| project in UiFlow2.

This example demonstrates infrared (IR) transmission functionality. When button A is pressed, it sends IR data with a specified address and data value. 
The example displays the address and data being transmitted.

UiFlow2 Code Block:

    |sticks3_ir_tx_example.png|

Example output:

    None

IR Reception
^^^^^^^^^^^^

Open the |sticks3_ir_rx_example.m5f2| project in UiFlow2.

This example demonstrates infrared (IR) reception functionality using NEC decode protocol. 
When IR data is received, it displays the address and data values on the screen.

UiFlow2 Code Block:

    |sticks3_ir_rx_example.png|

Example output:

    None

MicroPython Example 
-------------------

IR Transmission
^^^^^^^^^^^^^^^

This example demonstrates infrared (IR) transmission functionality. When button A is pressed, it sends IR data with a specified address and data value. 
The example displays the address and data being transmitted.

MicroPython Code Block:

    .. literalinclude:: ../../../examples/controllers/sticks3/sticks3_ir_tx_example.py
        :language: python
        :linenos:

Example output:

    None

IR Reception
^^^^^^^^^^^^

This example demonstrates infrared (IR) reception functionality using NEC decode protocol. 
When IR data is received, it displays the address and data values on the screen.

MicroPython Code Block:

    .. literalinclude:: ../../../examples/controllers/sticks3/sticks3_ir_rx_example.py
        :language: python
        :linenos:

Example output:

    None

class IR
--------

Constructors
------------

.. class:: IR()

    Initializes the IR unit with the appropriate pins based on the M5Stack board type.

    UiFlow2:

        |init.png|

Methods
-------

.. method:: IR.tx(cmd, data)

    Transmits an IR signal with the specified command and data using the NEC protocol.

    :param  cmd: The command code to be transmitted.
    :param  data: The data associated with the command.

    UiFlow2:

        |tx.png|

.. method:: IR.rx_cb(cb)

    Registers a callback for infrared reception. When an NEC-format IR signal is received, the callback is invoked with two arguments: ``(data, addr)``.

    Only supported on boards with an IR receiver (e.g. StickS3).

    :param cb: Callback function with signature ``cb(data, addr)``. ``data`` and ``addr`` are 8-bit values (0–255).

    UiFlow2:

        |rx_cb.png|
