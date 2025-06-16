from machine import I2C, Pin
from INA219SensorClass import INA219Sensor
from time import sleep

# Initialize I2C on GPIO0 (SDA) and GPIO1 (SCL)
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=25000)

# Create INA219 sensor instance
sensor = INA219Sensor(i2c)

# Read values continuously
while True:
    try:
        voltage = sensor.read_voltage()
        current = sensor.read_current()
        power = sensor.read_power()

        print("Bus Voltage: {:.2f} V".format(voltage))
        print("Current: {:.3f} A".format(current))
        print("Power: {:.3f} W".format(power))
        print("------------------------")

    except Exception as e:
        print("Sensor Error:", e)

    sleep(1)
