from machine import I2C, Pin
import struct
import time

# ==== CONFIG ====
INA219_ADDR = 0x40
REG_CALIBRATION = 0x05
REG_CURRENT = 0x04
REG_BUS_VOLTAGE = 0x02

# Shunt resistor value (in ohms)
SHUNT_OHMS = 0.1

# Calibration values (use your actual calibration results)
CURRENT_LSB = 0.212 / 1024  # Replace with your own measured value
CALIBRATION_VALUE = int(0.04096 / (CURRENT_LSB * SHUNT_OHMS))

# === I2C Setup ===
i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)

def write_register(reg, value):
    data = struct.pack(">H", value)
    i2c.writeto_mem(INA219_ADDR, reg, data)

def read_register_u16(reg):
    raw = i2c.readfrom_mem(INA219_ADDR, reg, 2)
    return struct.unpack(">H", raw)[0]

def read_register_s16(reg):
    raw = i2c.readfrom_mem(INA219_ADDR, reg, 2)
    return struct.unpack(">h", raw)[0]

def get_current_mA():
    raw_current = read_register_s16(REG_CURRENT)
    return abs(raw_current * CURRENT_LSB * 1000)  # Convert to mA

def get_voltage_V():
    raw_voltage = read_register_u16(REG_BUS_VOLTAGE)
    return (raw_voltage >> 3) * 0.004  # LSB = 4mV, 13-bit value

# === Apply calibration ===
write_register(REG_CALIBRATION, CALIBRATION_VALUE)

# === EMA Filter Class ===
class EMAFilter:
    def __init__(self, alpha=0.95):
        self.alpha = alpha
        self.filtered = 0

    def update(self, measurement):
        self.filtered = self.alpha * measurement + (1 - self.alpha) * self.filtered
        return self.filtered

# Create EMA filters for voltage and current
voltage_filter = EMAFilter(alpha=0.95)
current_filter = EMAFilter(alpha=0.95)

# === Main Loop ===
print("Reading real-time voltage and current with EMA filter:")
try:
    while True:
        v = get_voltage_V()
        voltage = voltage_filter.update(v)

        c = get_current_mA()
        current = current_filter.update(c)

#         print(f"{c:.3f}\t{current:.3f}\t{c-current:.3f}")
        print(f"{v+.1:.3f}\t{voltage:.3f}\t{v-voltage:.3f}")

        time.sleep(0.05)

except KeyboardInterrupt:
    print("Stopped by user.")
