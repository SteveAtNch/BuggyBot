# INA219.py for MicroPython
from machine import I2C
import time

class INA219:
    def __init__(self, i2c: I2C, address=0x40):
        self.i2c = i2c
        self.addr = address
        self._cal_value = 4096
        self._current_lsb = 0.1  # default current LSB in mA
        self._power_lsb = 0.002  # power LSB in W

        # Initialize sensor
        self._write_register(0x00, 0x399F)  # config register, example: 32V, 2A range
        self._write_register(0x05, self._cal_value)  # calibration register

    def _write_register(self, reg, value):
        buf = bytearray(3)
        buf[0] = reg
        buf[1] = (value >> 8) & 0xFF
        buf[2] = value & 0xFF
        self.i2c.writeto(self.addr, buf)

    def _read_register(self, reg):
        self.i2c.writeto(self.addr, bytes([reg]))
        data = self.i2c.readfrom(self.addr, 2)
        return (data[0] << 8) | data[1]

    def voltage(self):
        # Bus voltage register (0x02), shift right 3 bits and multiply by 4mV
        raw = self._read_register(0x02)
        voltage = ((raw >> 3) * 4) / 1000.0  # Volts
        return voltage

    def current(self):
        # Current register (0x04)
        raw = self._read_register(0x04)
        # convert 16-bit signed int
        if raw > 32767:
            raw -= 65536
        # multiply by current LSB (mA)
        current_mA = raw * self._current_lsb
        return current_mA

    def power(self):
        # Power register (0x03), power LSB = 20 * current LSB according to datasheet
        raw = self._read_register(0x03)
        power_mW = raw * self._power_lsb * 1000
        return power_mW
