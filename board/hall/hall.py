from board.device_state import DeviceState
from board.mqtt import Client
from board.servo import servo
from machine import Pin


class Hall:
    def __init__(self) -> None:
        # pin 26 corresponds to A0
        self.pin = Pin(26, Pin.IN, Pin.PULL_UP)

    def check_open(self) -> bool:
        return bool(self.pin.value())

    def basic_update_state(self, state) -> None:
        state.open = bool(self.pin.value())

    def update_state(self, state: DeviceState, client: Client) -> None:
        if state.locked:
            return

        new_open = self.check_open()
        if new_open != state.open:
            if new_open:  # if open
                state.open = True  # = new_open
            else:  # state has unlocked and open, our hall sensor says closed
                state.open = False  # correct state
                state.last_closed = state.now  # correct state

        if state.now and state.last_closed:
            if not state.open and (state.now - state.last_closed) >= 3:
                # 3 seconds passed since last closed and still unlocked
                servo.lock()
                state.locked = True
                client.publish_message(topic="/smartlock/pub", data=state.data)
