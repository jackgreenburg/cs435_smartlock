"""
This is where the MQTT Client handler will live.

It will be responsible for calling the appropriate function
with the corresponding message depending on what topic it recieved
a message for.
"""
from board.log import logger
from board.servo import servo
from board.device_state import state

def refresh_handler(message: dict) -> None:
    pass

def unlock_handler(message: dict) -> None:
    servo.unlock()
    state.locked = False

    # so lock does not close immediately
    state.last_closed = state.now
