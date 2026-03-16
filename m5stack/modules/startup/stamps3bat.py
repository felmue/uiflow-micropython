# SPDX-FileCopyrightText: 2026 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: MIT

# StampS3Bat startup script
import time
import network
import machine
import binascii
import M5Things
from startup import Startup
from hardware import RGB


# StampS3Bat startup menu
class StampS3Bat_Startup(Startup):
    COLOR_YELLOW = 0xFFFF00  # WiFi not connected
    COLOR_BLUE = 0x0000FF  # WiFi connected, server not connected
    COLOR_GREEN = 0x00FF00  # WiFi connected, server connected

    def __init__(self) -> None:
        self.rgb = RGB()
        self.rgb.set_brightness(64)
        self.rgb.fill_color(self.COLOR_YELLOW)
        super().__init__()

    def show_mac(self) -> None:
        mac = binascii.hexlify(machine.unique_id()).decode("utf-8").upper()
        print("Mac: " + mac[0:6] + "_" + mac[6:])

    def show_error(self, ssid: str, error: str) -> None:
        print("SSID: " + ssid + "\r\nNotice: " + error)

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
        timeout: int = 60,
    ) -> None:
        self.show_mac()

        if super().connect_network(
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
                status: int = self.connect_status()
                if status == network.STAT_GOT_IP:
                    pair_code = M5Things.paircode()
                    if pair_code != "":
                        print("")
                        print("Local IP: " + super().local_ip())
                        print("=======================")
                        print("Pair Code: " + pair_code)
                        print("=======================")
                        self.rgb.fill_color(self.COLOR_GREEN)
                        success = True
                        break
                    else:
                        print(".", end="")
                else:
                    print(".", end="")
                time.sleep(1)
            if not success:
                print(
                    f"[NET] WIFI: {self.wifi_status_str(status)} | "
                    f"MQTT: {self.m5things_status_str(M5Things.status())}"
                )
