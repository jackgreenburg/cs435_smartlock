from board.device_state import DeviceState
from machine import UART, RTC

import time


class GPS:
    def __init__(self):
        self._uart = UART(2, baudrate=9600, rx=16, tx=17, timeout=10)
        self.rtc = RTC()

        # Only turn on RMC to grab timestamp and location
        self.send_command("PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
        self.send_command("PMTK220,1000")

    def send_command(self, command, add_checksum=True):
        """
        Sends a command to the GPS.
        """
        self._uart.write("$")
        self._uart.write(command)
        if add_checksum:
            checksum = 0
            for char in command:
                checksum ^= ord(char)
            self._uart.write("*")
            self._uart.write("{:02x}".format(checksum).upper())
        self._uart.write("\r\n")

    def to_epoch(self, hhmmss, ddmmyy):

        hour = int(hhmmss[:2])
        minute = int(hhmmss[2:4])
        second = int(hhmmss[4:])

        day = int(ddmmyy[:2])
        month = int(ddmmyy[2:4])
        year = int(ddmmyy[4:]) + 2000

        # (year, month, day, weekday?, minute, second, microsecond)
        self.rtc.datetime((year, month, day, 0, hour, minute, second, 0))

        # time.time() returns seconds after 1/1/2000, adding 30 years gives epoch
        return time.time() + 946684800

    def update_state(self, state: DeviceState):

        sentence = self._uart.readline()

        if not sentence:
            return

        # Let's clean it up.
        sentence = sentence.strip().decode("utf-8")

        # Remove checksum
        sentence = sentence[:-7]

        if "$GNRMC" not in sentence:
            print("No RMC data.")
            return

        parts = sentence.split(",")

        """
        $GNRMC,024054.000,A,4400.6241,N,07310.8063,W,0.52,282.00,021221
        $GNRMC,024627.000,V,,,,,0.41,302.99,021221
        """

        if len(parts) < 3:
            print("Not enough parts")
            return

        accept = parts[2] == "A"

        lat = None
        lng = None

        if accept:
            lat = float(parts[3]) / 100
            if parts[4] == "S":
                lat *= -1

            lng = float(parts[5]) / 100
            if parts[6] == "W":
                lng *= -1

        now: int = self.to_epoch(parts[1][:6], parts[-1])

        print(f"{lat=} {lng=} {now=}")

        # boom. update the state
        if lat is not None:
            state.lat = lat

        if lng is not None:
            state.lng = lng

        state.now = now


gps = GPS()
