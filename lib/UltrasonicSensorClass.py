import time
from machine import Pin, time_pulse_us

class UltrasonicSensor:
    def __init__(self, trig_pin, echo_pin, max_distance_cm=500):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.trig.low()
        time.sleep_ms(50)  # Give sensor time to settle
        self.max_distance_cm = max_distance_cm  # User-defined cutoff

    def measure_distance(self):
        # Send trigger pulse
        self.trig.low()
        time.sleep_us(2)
        self.trig.high()
        time.sleep_us(10)
        self.trig.low()

        try:
            # Wait for echo response, timeout after 30ms (roughly 5 meters)
            duration = time_pulse_us(self.echo, 1, 30000)
            if duration < 0:
                return None  # Timeout or error

            # Convert duration to distance (speed of sound = ~343 m/s)
            distance_cm = (duration / 2) * 0.0343

            # Filter out invalid or noisy values
            if 2 <= distance_cm <= self.max_distance_cm:
                return round(distance_cm, 1)
            else:
                return None
        except OSError:
            return None  # In case of any I/O error
