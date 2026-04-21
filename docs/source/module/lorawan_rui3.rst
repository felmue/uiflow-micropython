LoRaWAN-EU868 Module
=====================

.. include:: ../refs/module.lorawan_rui3.ref

The Module LoRaWAN868 is a LoRaWAN programmable data transfer unit based on the STM32WLE5 chip. The module supports long-range communication, low-power operation, and high sensitivity characteristics, making it suitable for IoT communication needs in a variety of complex environments.

Support the following products:

|Modlue-LoraWAN 868|

Micropython LoRaWAN-EU868 P2P Mode TX Example:

    .. literalinclude:: ../../../examples/module/lorawan_rui3/module_lorawan868_p2p_tx_core_example.py
        :language: python
        :linenos:

Micropython LoRaWAN-EU868 P2P Mode RX Example:

    .. literalinclude:: ../../../examples/module/lorawan_rui3/module_lorawan868_p2p_rx_cores3_example.py
        :language: python
        :linenos:

UIFLOW2 LoRaWAN-EU868 P2P Mode TX Example:

    |p2p_tx_example.png|

    |module_lorawan868_p2p_tx_core_example.m5f2|

UIFLOW2 LoRaWAN-EU868 P2P Mode RX Example:

    |p2p_rx_example.png|

    |module_lorawan868_p2p_rx_cores3_example.m5f2|

**API**
-------

LoRaWANModule_RUI3
^^^^^^^^^^^^^^^^^^^^^^

.. autoclass:: module.lorawan_rui3.LoRaWANModule_RUI3
    :members:
    :inherited-members:
    :member-order: bysource
    :show-inheritance: