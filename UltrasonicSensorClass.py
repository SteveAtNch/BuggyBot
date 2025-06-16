import time
from machine import Pin, time_pulse_us

class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.trig.low()
        time.sleep_ms(50)  # Give sensor time to settle

    def measure_distance(self):
        self.trig.low()
        time.sleep_us(2)
        self.trig.high()
        time.sleep_us(10)
        self.trig.low()

        duration = time_pulse_us(self.echo, 1, 30000)  # 30 ms timeout
        if duration < 0:
            return None  # Timeout or error

        distance_cm = (duration / 2) * 0.0343
        return round(distance_cm, 1)
