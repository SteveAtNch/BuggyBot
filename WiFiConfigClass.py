import network
import time

class WiFiConnector:
    def __init__(self, ssid=None, password=None, mode="STA", auto_connect=False):
        self.ssid = ssid
        self.password = password
        self.mode = mode
        self.wlan = None
        if auto_connect:
            self.connect()

    def connect(self):
        if self.mode == "STA":
            # Only touch STA_IF
            self.wlan = network.WLAN(network.STA_IF)
            if not self.wlan.active():
                self.wlan.active(True)
                time.sleep(0.5)

            if not self.wlan.isconnected():
                print("Connecting to WiFi...")
                self.wlan.connect(self.ssid, self.password)
                timeout = 10
                while not self.wlan.isconnected() and timeout > 0:
                    print("Waiting for connection...")
                    time.sleep(1)
                    timeout -= 1

            if self.wlan.isconnected():
                print("Connected to WiFi")
                return self.wlan.ifconfig()
            else:
                print("Failed to connect")
                return None

        elif self.mode == "AP":
            self.wlan = network.WLAN(network.AP_IF)
            self.wlan.active(True)
            self.wlan.config(essid="BuggyBot_AP", password="12345678")
            print("Running in Access Point mode")
            return self.wlan.ifconfig()

        else:
            raise ValueError("Invalid mode: should be 'STA' or 'AP'")

    def get_status(self):
        if not self.wlan:
            return "WiFi not initialized"
        if self.wlan.isconnected():
            return f"Connected - IP: {self.wlan.ifconfig()[0]}"
        elif self.wlan.active():
            return "WiFi active but not connected"
        else:
            return "WiFi inactive"
