"""
The current device state class.
"""
from board.config import DEVICE_ID

class DeviceState:
    id: str = DEVICE_ID
    # GPS
    now: int = None
    lat: float = None
    lng: float = None
    # Hall
    locked: bool = False
    last_closed: int = None
    open: bool = False
    # Batt
    battery_percentage: str = None

    """
    Formats the data for MQTT publish.
    """
    @property
    def data(self) -> dict:
        return {
            "id": self.id,
            "lat": self.lat or 44.016,
            "lng": self.lng or -73.16,
            "locked": self.locked,
            "updated_at": self.now or 0,
            "battery_percentage": self.battery_percentage or "69%",
            "last_closed": self.last_closed or 0,
        }

    """
    Returns preformatted device state for logging.
    """
    def __str__(self) -> str:
        message = f"DeviceState:\n"
        message += f" now={self.now}\n"
        message += f" lat={self.lat}\n"
        message += f" lng={self.lng}\n"
        message += f" locked={self.locked}\n"
        message += f" open={self.open}\n"
        message += f" batt={self.battery_percentage}\n"
        message += f" lc={self.last_closed}"

        return message



state = DeviceState()
