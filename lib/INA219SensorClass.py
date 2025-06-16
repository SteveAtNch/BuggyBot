from INA219 import INA219

class INA219Sensor:
    def __init__(self, i2c):
        # Pass the i2c device as positional argument, and optionally address as second positional
        self.ina = INA219(i2c, 0x40)
        self.ina.configure()

    def read_voltage(self):
        return self.ina.voltage()

    def read_current(self):
        return self.ina.current() / 1000  # convert mA to A

    def read_power(self):
        return self.ina.power() / 1000  # convert mW to W
