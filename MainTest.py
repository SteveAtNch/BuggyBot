from machine import Pin, PWM
from time import sleep, sleep_ms
import _thread
import secrets

from WiFiConfigClass import WiFiConnector
from UltrasonicSensorClass import UltrasonicSensor
from RunningFilterClass import RunningFilter
from OLEDclass import OLEDDisplay
from MG90SClass import MG90S

# Constants
WIDTH  = 128
HEIGHT = 32
SCL_PIN = 17
SDA_PIN = 16
SERVO_PIN = 15
TRIG_PIN = 3
ECHO_PIN = 2

# Shared data
distance_data = [None] * 181  # Index 0 for -90, index 180 for +90

# Initialize OLED display
oled = OLEDDisplay(scl_pin=SCL_PIN, sda_pin=SDA_PIN, width=WIDTH, height=HEIGHT)
oled.clear()
oled.display.write_text("BuggyBot", x=0, y=HEIGHT // 4, size=2)
oled.update()
sleep(1)

# Connect to WiFi
wifi = WiFiConnector(
    ssid=secrets.SSID,
    password=secrets.PASSWORD,
    mode="STA",
    auto_connect=True
)
print("WiFi Status:", wifi.get_status())

# Servo and sensor instances
servo = MG90S(SERVO_PIN)
sensor = UltrasonicSensor(trig_pin=TRIG_PIN, echo_pin=ECHO_PIN)
filter = RunningFilter(tank_size=2)

# Function to run on CPU1 (infinite scanning loop)
def scanner_task():
    global distance_data
    directions = [range(-90, 91), range(90, -91, -1)]  # forward and reverse scan

    try:
        while True:
            for direction in directions:
                for angle in direction:
                    servo.go_to(angle)
                    sleep_ms(50)  # Allow time for servo to move

                    raw = sensor.measure_distance()
                    if raw is not None:
                        filter.add(raw)
                        avg = filter.average()
                        distance_data[angle + 90] = avg
                    else:
                        distance_data[angle + 90] = None

                    sleep_ms(5)
    except Exception as e:
        print("Error in scanner task:", e)

# Start scanning on CPU1
_thread.start_new_thread(scanner_task, ())

# Main loop on CPU0
while True:
    # Example: CPU0 just shows center reading on OLED
    center_distance = distance_data[90]  # Angle 0°
    oled.display.fill_rect(0, 0, WIDTH, HEIGHT, 0)

    if center_distance is not None:
        msg = f"Center: {center_distance:.1f} cm"
    else:
        msg = "Center: N/A"

    x = (WIDTH - len(msg) * 8) // 2
    oled.display.write_text(msg, x=x, y=10, size=1)
    oled.update()

    print("Center Distance:", center_distance)
    sleep(0.2)
