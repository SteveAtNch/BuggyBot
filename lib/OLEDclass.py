from machine import Pin, I2C
import ssd_1306

class OLEDDisplay:
    def __init__(self, scl_pin, sda_pin, width=128, height=64, i2c_freq=400000):
        # Accept pin numbers or Pin objects
        self.scl_pin = scl_pin if isinstance(scl_pin, Pin) else Pin(scl_pin)
        self.sda_pin = sda_pin if isinstance(sda_pin, Pin) else Pin(sda_pin)
        self.i2c = I2C(0, scl=self.scl_pin, sda=self.sda_pin, freq=i2c_freq)

        self.width = width
        self.height = height
        self.display = ssd_1306.SSD1306_I2C(self.width, self.height, self.i2c)

    def clear(self):
        self.display.fill(0)
        self.display.show()

    def show_text(self, text, x=0, y=0):
        self.display.fill(0)
        self.display.text(text, x, y)
        self.display.show()

    def draw_text(self, text, x=0, y=0):
        self.display.text(text, x, y)

    def update(self):
        self.display.show()
