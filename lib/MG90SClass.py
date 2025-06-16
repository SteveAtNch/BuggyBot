from machine import Pin, PWM

class MG90S:
    def __init__(self, pin_number):
        self.pwm = PWM(Pin(pin_number))
        self.pwm.freq(50)  # Standard servo frequency

    def angle_to_duty(self, angle):
        # Clamp angle to -90 to +90
        angle = max(-90, min(90, angle))
        # Map angle to pulse width: 0.5ms to 2.5ms = 2.5% to 12.5% duty cycle
        # duty_u16 = (pulse_ms / 20ms) * 65535
        min_pulse = 0.5  # ms
        max_pulse = 2.5  # ms
        mid_pulse = 1.5  # ms
        
        # Scale: -90 maps to 0.5ms, 0 to 1.5ms, +90 to 2.5ms
        pulse_ms = mid_pulse + (angle / 90.0) * (max_pulse - mid_pulse)
        duty_u16 = int((pulse_ms / 20.0) * 65535)
        return duty_u16

    def go_to(self, angle):
        duty = self.angle_to_duty(angle)
        self.pwm.duty_u16(duty)

    def off(self):
        self.pwm.duty_u16(0)  # optional: turn off servo to save power
