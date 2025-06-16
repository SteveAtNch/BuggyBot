from machine import Pin, PWM

class Motor:
    def __init__(self, in1_pin, in2_pin, pwm_pin, freq=1000):
        self.in1 = Pin(in1_pin, Pin.OUT)
        self.in2 = Pin(in2_pin, Pin.OUT)
        self.pwm = PWM(Pin(pwm_pin))
        self.pwm.freq(freq)
        self.pwm.duty_u16(0)  # Initially stopped

    def forward(self, speed=65535):
        self.in1.on()
        self.in2.off()
        self.set_speed(speed)

    def backward(self, speed=65535):
        self.in1.off()
        self.in2.on()
        self.set_speed(speed)

    def stop(self):
        self.in1.off()
        self.in2.off()
        self.set_speed(0)

    def set_speed(self, speed):
        # Clamp speed between 0 and 65535
        speed = max(0, min(65535, speed))
        self.pwm.duty_u16(speed)
