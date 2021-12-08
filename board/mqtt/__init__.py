"""
Helper methods for use with publishing and subscribing to the AWS IoT
MQTT message broker. See https://mpython.readthedocs.io/en/master/library/mPython/umqtt.simple.html
for more information.
"""
import json

from board.certs import CERT, PRIVATE_KEY
from board.config import DEVICE_ID
from board.log import logger
from board.device_state import DeviceState
from umqtt.simple import MQTTClient

from .handlers import refresh_handler, unlock_handler

"""
Attempts to connect the board to the AWS MQTT Broker
@returns the mqtt client.
"""
def connect_to_aws_mqtt() -> MQTTClient:
    logger("Trying to connect to AWS MQTT...")
    mqtt_client = MQTTClient(
        "smartlock",
        "<IOT CORE ENDPOINT>",
        port = 8883,
        keepalive = 10000,
        ssl = True,
        ssl_params = {
            "key": PRIVATE_KEY,
            "cert": CERT,
            "server_side": False,
        },
    )
    mqtt_client.connect()
    logger("Connected!!!!")

    return mqtt_client

"""
Simple wrapper of the umqtt.simple client to enable pub/sub with AWS IoT core.
"""
class Client():

    """
    @param topics: List[str] of topics to subscribe to.
    @param state: State class
    """
    def __init__(self, topics, state: DeviceState) -> None:

        self.id = DEVICE_ID
        self.topics = topics
        self.state = state

        client = connect_to_aws_mqtt()
        client.set_callback(self.callback_handler)

        for topic in topics:
            client.subscribe(topic)

        self._client = client


    """
    Publishes a message to the specified topic.

    @param topic: the topic to publish to
    @param data: the dictionary to publish
    """
    def publish_message(self, topic: str, data: dict) -> None:

        self._client.publish(
            topic=topic,
            msg=json.dumps(data),
            qos=0,
        )


    """
    Subscribes to a given topic if the client is not already subscribed.

    @param topic: the topic to subscribe to
    """
    def subscribe(self, topic: str) -> None:

        if topic not in self.topics:
            self.topics.append(topic)
            self._client.subscribe(topic)

    """
    Set's the root callback function. This callback could be used as a handler
    depending on the topic the message was recieved for.
    """
    def set_callback(self, callback) -> None:

        self._client.set_callback(callback)

    """
    The default callback handler. Will only take action if the device ID in the
    message matches this devices ID.
    """
    def callback_handler(self, topic: bytes, message: str) -> None:
        flattened_topic = topic.decode("utf-8")
        flattened_message = json.loads(message)

        print(flattened_topic)
        print(str(flattened_message))

        handler_mapping = {
            "/smartlock/refresh": refresh_handler,
            "/smartlock/unlock": unlock_handler,
            # More handlers here!!
        }

        id = flattened_message.get("id")

        if id != self.id:
            print("Did not request this device to update.")
            return

        # boom. execute the correct callback handler
        handler_mapping[flattened_topic](flattened_message)

        # publish the device state
        self.publish_message(topic="/smartlock/pub", data=self.state.data)

    """
    Checks to see if there is are any pending message without blocking.
    If there is a message, it will pass it to the callback function.
    """
    def check_for_message(self) -> None:

        self._client.check_msg()

    """
    Waits for the next message, blocking all other processes in its thread.
    When a message arrives, it will pass it to the callback function.
    """
    def wait_for_message(self) -> None:

        self._client.wait_msg()

    """
    Pings the server to maintain the connection.
    """
    def ping(self) -> None:

        self._client.ping()

    """
    Disconnects the client from the server. Once done, you must re-instantiate
    the Client() object to reconnect. <--- NGL, this seems stupid, maybe we should
    fix later.
    """
    def disconnect(self) -> None:

        self._client.disconnect()
