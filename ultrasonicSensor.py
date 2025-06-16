import time
from machine import Pin, time_pulse_us
# from WiFiConfig import WiFiConnector
# import secrets
# 
# print("Waiting 3 seconds...")
# time.sleep(3)
# 
# net = WiFiConnector(ssid=secrets.ssid, password=secrets.password, mode="STA")
# net.connect()
# print(net.get_status())


# Define pins
TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)

def measure_distance():
    # Ensure trigger is low
    TRIG.low()
    time.sleep_us(2)

    # Send a 10us pulse
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()

    # Measure the time the echo is high
    duration = time_pulse_us(ECHO, 1, 30000)  # timeout in microseconds

    if duration < 0:
        return None  # Timeout or invalid reading

    # Calculate distance in cm (speed of sound = 343 m/s)
    distance = (duration / 2) * 0.0343
    return round(distance, 1)

# Main loop
while True:
    dist = measure_distance()
    if dist is None:
        print("Out of range or timeout")
    else:
        print("Distance:", dist, "cm")
    time.sleep(0.5)
