import network
import ubinascii
DEVICE_ID = ubinascii.hexlify(network.WLAN().config('mac'),':').decode()
