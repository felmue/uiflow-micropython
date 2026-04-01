Atomic Audio-3.5 Base
=====================

.. sku: A166

.. include:: ../refs/base.audio35.ref

The following products are supported:

    |Atomic Audio-3.5 Base|

Below is the detailed support for Atomic Audio-3.5 Base on the host:

.. table::
    :widths: auto
    :align: center

    +-----------------+------------------------+
    |Controller       | Atomic Audio-3.5 Base  |
    +=================+========================+
    | Atom Echo       | |O|                    |
    +-----------------+------------------------+
    | Atom Lite       | |S|                    |
    +-----------------+------------------------+
    | Atom Matrix     | |S|                    |
    +-----------------+------------------------+
    | AtomS3          | |S|                    |
    +-----------------+------------------------+
    | AtomS3 Lite     | |S|                    |
    +-----------------+------------------------+
    | AtomS3R         | |S|                    |
    +-----------------+------------------------+
    | AtomS3R-CAM     | |S|                    |
    +-----------------+------------------------+
    | AtomS3R-Ext     | |S|                    |
    +-----------------+------------------------+

.. |S| unicode:: U+2705
.. |O| unicode:: U+2B55

.. note::
    Atomic Audio-3.5 Base uses the same Audio CODEC and pin connections as Atomic Echo Base. For detailed usage instructions, please refer to the `Atomic Echo Base <echo.html>`_ documentation.


UiFlow2 Example
---------------

Record and play WAV file
^^^^^^^^^^^^^^^^^^^^^^^^

Open the |atoms3r_aduio_record_play_example.m5f2| project in UiFlow2.

This example initializes Atomic Audio-3.5 Base, records stereo audio to ``/flash/res/audio/test.wav`` for 5 seconds after pressing BtnA, and then plays the recorded WAV file.

UiFlow2 Code Block:

    |atoms3r_aduio_record_play_example.png|

Example output:

    None

MicroPython Example
-------------------

Record and play WAV file
^^^^^^^^^^^^^^^^^^^^^^^^

This example initializes Atomic Audio-3.5 Base, records stereo audio to ``/flash/res/audio/test.wav`` for 5 seconds after pressing BtnA, and then plays the recorded WAV file.

MicroPython Code Block:

    .. literalinclude:: ../../../examples/base/audio35/atoms3r_aduio_record_play_example.py
        :language: python
        :linenos:

Example output:

    None

**API**
-------

class AtomicAudio35Base
^^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: base.audio35.AtomicAudio35Base
    :members:
    :member-order: bysource
    :no-index:

``AtomicAudio35Base`` is an alias for ``AtomicEchoBase``. Please refer to the `AtomicEchoBase <echo.html#base.echo.AtomicEchoBase>`_ class for detailed documentation.
