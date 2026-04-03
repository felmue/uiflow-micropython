.. py:currentmodule:: touch

Touch
======

.. include:: ../refs/hardware.touch.ref

The ``Touch`` class provides methods for reading touch coordinates, the number of touch points, and detailed touch information on M5Stack devices with touch screens.

UiFlow2 Example
---------------

Getting Touch Coordinates
^^^^^^^^^^^^^^^^^^^^^^^^^

Open the |cores3_touch_example.m5f2| project in UiFlow2.

This example demonstrates how to obtain the X and Y coordinates of a touch event and display them on the screen.

UiFlow2 Code Block:

    |cores3_touch_example.png|

Example output:

    Screen displays the current X and Y coordinates of the touch event.

MicroPython Example
-------------------

Getting Touch Coordinates
^^^^^^^^^^^^^^^^^^^^^^^^^

This example demonstrates how to obtain the X and Y coordinates of a touch event and display them on the screen.

MicroPython Code Block:

    .. literalinclude:: ../../../examples/hardware/touch/cores3_touch_example.py
        :language: python
        :linenos:

Example output:

    Screen displays the current X and Y coordinates of the touch event.

API
-------

Touch
^^^^^^^

.. class:: M5.Touch()

    .. py:method:: getX()

        Get the current X coordinate of the touch.

        :returns: int - The X coordinate.

        UiFlow2 Code Block:

            |getX.png|

        MicroPython Code Block:

            .. code-block:: python

                x = M5.Touch.getX()

    .. py:method:: getY()

        Get the current Y coordinate of the touch.

        :returns: int - The Y coordinate.

        UiFlow2 Code Block:

            |getY.png|

        MicroPython Code Block:

            .. code-block:: python

                y = M5.Touch.getY()

    .. py:method:: getCount()

        Get the number of current touch points.

        :returns: int - Number of active touches (0 if no touch).

        UiFlow2 Code Block:

            |getCount.png|

        MicroPython Code Block:

            .. code-block:: python

                count = M5.Touch.getCount()

    .. py:method:: getDetail(index=0)

        Get detailed information about a specific touch point.

        :param int index: Index of the touch point (default is 0).
        :returns: tuple - A tuple of 11 elements containing detailed touch status:

            - ``[0] deltaX`` (int): The X-axis difference since the last measurement.
            - ``[1] deltaY`` (int): The Y-axis difference since the last measurement.
            - ``[2] distanceX`` (int): The total X-axis distance moved since touched.
            - ``[3] distanceY`` (int): The total Y-axis distance moved since touched.
            - ``[4] isPressed`` (bool): True if currently being pressed.
            - ``[5] wasPressed`` (bool): True if just transitioned to pressed state.
            - ``[6] wasClicked`` (bool): True if just clicked.
            - ``[7] isReleased`` (bool): True if currently released.
            - ``[8] wasReleased`` (bool): True if just transitioned to released state.
            - ``[9] isHolding`` (bool): True if currently being held.
            - ``[10] wasHold`` (bool): True if it was held.

        MicroPython Code Block:

            .. code-block:: python

                detail = M5.Touch.getDetail(0)

    .. py:method:: getTouchPointRaw(index=0)

        Get the raw touch point coordinates.

        :param int index: Index of the touch point (default is 0).
        :returns: tuple - A tuple of 4 elements containing raw touch point data:

            - ``[0] x`` (int): The raw X coordinate.
            - ``[1] y`` (int): The raw Y coordinate.
            - ``[2] size`` (int): The size or pressure of the touch point.
            - ``[3] id`` (int): The unique identifier for tracking the touch point.

        UiFlow2 Code Block:

            |getTouchPointRaw.png|

            |getTouchPointRaw2.png|

        MicroPython Code Block:

            .. code-block:: python

                raw = M5.Touch.getTouchPointRaw(0)
