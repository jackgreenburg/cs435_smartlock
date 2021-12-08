import time

from board.log import logger

from board.mqtt import Client
from board.device_state import state
from board.hall import hall
from board.gps import gps

client = Client(
    topics=["/smartlock/unlock", "/smartlock/refresh"],
    state=state,
)

# Wrap the main loop in a try except block to restart the loop
# if an exception occurs. Probably bad practice, but not a bad idea.
while True:
    try:
        gps.update_state(state)
        hall.update_state(state=state, client=client)

        # Update the display
        logger(str(state))
        client.check_for_message()
        time.sleep(0.5)

    except Exception as e:
        print(e)
