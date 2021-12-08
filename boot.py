from board.wifi import connect_to_wifi
from board.log import logger

connect_to_wifi()

# Ensure we have all of the proper 3rd party libraries
try:
    import umqtt.simple

except ImportError:
    import upip
    upip.install("umqtt.simple")


logger("Boot done!")
