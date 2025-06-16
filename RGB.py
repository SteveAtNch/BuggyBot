import machine
import neopixel
import time

Enable_WDT = False
try_pin = 23
intensity = 50

# Set up the pin and neopixel
pin = machine.Pin(try_pin, machine.Pin.OUT)
led = neopixel.NeoPixel(pin, 1)

# Set up the Watchdog Timer (WDT)
if Enable_WDT == True:
    wdt = machine.WDT(timeout=5000)  # Timeout is in milliseconds (5 seconds)

def set_color(r, g, b, i):
    led[0] = (int(r*(i/100)), int(g*(i/100)), int(b*(i/100)))
    led.write()
#     print(r, g, b, i)

colors = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (0, 0, 0)]  # Black (off)

while True:
    for color in colors:
        for i in range(0, intensity, 1):
            set_color(*color, i)
            time.sleep(.005)
#             wdt.feed()  # Feed the WDT to prevent a reset
        for i in range(intensity, -1, -1):
            set_color(*color, i)
            time.sleep(.005)
#             wdt.feed()  # Feed the WDT to prevent a reset
        time.sleep(.25)
        if Enable_WDT == True:
            wdt.feed()  # Feed the WDT to prevent a reset
