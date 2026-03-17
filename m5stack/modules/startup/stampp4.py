# SPDX-FileCopyrightText: 2026 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT

# StampP4 startup script
import time
import network
import machine
import binascii
import M5Things
from startup import Startup


# StampP4 startup menu
class StampP4_Startup:
    def __init__(self) -> None:
        pass

    def show_mac(self) -> None:
        mac = binascii.hexlify(machine.unique_id()).decode("utf-8").upper()
        print("Mac: " + mac[0:6] + "_" + mac[6:])

    def startup(
        self,
        net_mode: str = "WIFI",
        ssid: str = "",
        pswd: str = "",
        protocol: str = "",
        ip: str = "",
        netmask: str = "",
        gateway: str = "",
        dns: str = "",
        timeout: int = 1,
    ) -> None:
        self.show_mac()

        self._net_if = Startup(network_type=net_mode)  # type: ignore

        if self._net_if.connect_network(
            ssid=ssid,
            pswd=pswd,
            protocol=protocol,
            ip=ip,
            netmask=netmask,
            gateway=gateway,
            dns=dns,
        ):
            print("Connecting to " + ssid + ".", end="")
            start = time.ticks_ms()
            success = False
            while time.ticks_diff(time.ticks_ms(), start) < timeout * 1000:
                status: int = self._net_if.connect_status()
                if status == network.STAT_GOT_IP:
                    pair_code = M5Things.paircode()
                    if pair_code != "":
                        print("")
                        print("Local IP: " + self._net_if.local_ip())
                        print("=======================")
                        print("Pair Code: " + pair_code)
                        print("=======================")
                        success = True
                        break
                    else:
                        print(".", end="")
                else:
                    print(".", end="")
                time.sleep(1)
            if not success:
                print("\nNetwork connection timeout!")
                print(
                    f"[NET] WIFI: {self._net_if.wifi_status_str(status)} | "
                    f"MQTT: {self._net_if.m5things_status_str(M5Things.status())}"
                )
