import time

from machine import PWM, Pin

UNLOCKED_DUTY = 115
LOCKED_DUTY = 40

class Servo:
    def __init__(self, pin: int=13) -> None:
        self.servo = PWM(Pin(pin), freq=50)
        self.servo.duty(UNLOCKED_DUTY)  # turn off motor

    def duty(self, duty_cycle: int) -> None:
        if (40 <= duty_cycle) and (duty_cycle <= 115):
            self.servo.duty(duty_cycle)

    def lock(self) -> None:
        self.duty(LOCKED_DUTY)
    
    def unlock(self) -> None:
        self.duty(UNLOCKED_DUTY)
