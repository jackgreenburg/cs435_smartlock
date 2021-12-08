import network
from board.display import oled

"""
Connects the board to WiFi
"""
def connect_to_wifi(ssid="<SSID>", password=None):
    net = network.WLAN(network.STA_IF)


    # TODO: Scan for the network you are attempting to connect to first

    if not net.isconnected():
        print(f"Connecting to network {ssid}...")
        oled.write_text(f"connecting to network {ssid}...")
        net.active(True)
        net.connect(ssid, password)
        while not net.isconnected():
            pass
    print("network config:", net.ifconfig())
    oled.qr()
