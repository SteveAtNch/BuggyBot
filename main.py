from WiFiConfigClass import WiFiConnector
from UltrasonicSensorClass import UltrasonicSensor
from RunningFilterClass import RunningFilter
from OLEDclass import OLEDDisplay
from time import sleep
import secrets

# OLED parameters
WIDTH  = 128                                          
HEIGHT = 32  # 32 for the small .91" and 64 for the bigger OLED display
SCL_PIN = 17
SDA_PIN = 16

# Create an instance of the OLED display
oled = OLEDDisplay(scl_pin=SCL_PIN, sda_pin=SDA_PIN, width=WIDTH, height=HEIGHT)

# Add a splash Screen to the display
oled.clear()
oled.display.write_text("BuggyBot", x=0, y=HEIGHT//4, size=2)
oled.update()
sleep(1)

# Create WiFi connector and connect on boot
wifi = WiFiConnector(
    ssid=secrets.SSID,
    password=secrets.PASSWORD,
    mode="STA",             # Change to "AP" if you want Access Point mode
    auto_connect=True       # Connect automatically on creation
)

print(wifi.get_status())

# Create an instance of the distance sensor
sensor = UltrasonicSensor(trig_pin=3, echo_pin=2)



# Setup the running filter
filter = RunningFilter(tank_size=2)

while True:
    distance = sensor.measure_distance()
    if distance is not None:

        NewAvg = filter.add(distance) 
        msg = f'{NewAvg:.1f} cm'
        print(filter.average())
        
        font_size = 2
        text_width = len(msg) * 8 * font_size
        text_height = 8 * font_size

        x = (WIDTH - text_width) // 2
        y = (HEIGHT - text_height) // 2

        oled.display.fill_rect(0, 0, WIDTH, HEIGHT, 0)
        oled.display.write_text(msg, x=x, y=y, size=font_size)
        oled.update()
    else:
        print("Out of range or timeout")

    sleep(0.05)