from machine import Pin, PWM, ADC
from time import sleep

# Motor A configuration
MA1 = Pin(15, Pin.OUT)
MA2 = Pin(14, Pin.OUT)
MApwm = PWM(Pin(11))
MApwm.freq(1000)

# Motor B configuration
MB1 = Pin(13, Pin.OUT)
MB2 = Pin(12, Pin.OUT)
MBpwm = PWM(Pin(10))
MBpwm.freq(1000)

# Joystick setup
sw = Pin(22, Pin.IN, Pin.PULL_UP)
xAxis = ADC(Pin(26))
yAxis = ADC(Pin(27))

# Calibration (optional)
xcal = 0
ycal = 0

def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

def set_motor(motor, direction, speed):
    speed = min(max(speed, 0), 65535)
    if motor == 'A':
        MA1.value(1 if direction == 'forward' else 0)
        MA2.value(0 if direction == 'forward' else 1)
        MApwm.duty_u16(speed)
    elif motor == 'B':
        MB1.value(1 if direction == 'forward' else 0)
        MB2.value(0 if direction == 'forward' else 1)
        MBpwm.duty_u16(speed)

def stop_motors():
    MA1.value(0)
    MA2.value(0)
    MApwm.duty_u16(0)
    MB1.value(0)
    MB2.value(0)
    MBpwm.duty_u16(0)

try:
    while True:
        xRaw = xAxis.read_u16()
        yRaw = yAxis.read_u16()

        # Normalize joystick values (0–100)
        x = map_value(xRaw, 65535, 0, 0, 100) + xcal
        y = map_value(yRaw, 65535, 0, 0, 100) + ycal

        dead_zone = 5

        if abs(y - 50) > dead_zone:
            # Normal driving (forward/backward)
            direction = 'forward' if y > 50 else 'backward'
            speed_pct = abs(y - 50) * 2  # 0–100%
            base_speed = int((speed_pct / 100) * 65535)

            # Steering factor from X
            steering = x - 50
            if steering < 0:
                left_scale = 1.0 - (abs(steering) / 50.0)
                right_scale = 1.0
            elif steering > 0:
                left_scale = 1.0
                right_scale = 1.0 - (abs(steering) / 50.0)
            else:
                left_scale = right_scale = 1.0

            set_motor('A', direction, int(base_speed * left_scale))
            set_motor('B', direction, int(base_speed * right_scale))

        elif abs(x - 50) > dead_zone:
            # In-place pivot turning
            turn_pct = abs(x - 50) * 2  # 0–100%
            turn_speed = int((turn_pct / 100) * 65535)

            if x < 50:
                # Turn left: left motor backward, right motor forward
                set_motor('A', 'backward', turn_speed)
                set_motor('B', 'forward', turn_speed)
            else:
                # Turn right: left motor forward, right motor backward
                set_motor('A', 'forward', turn_speed)
                set_motor('B', 'backward', turn_speed)

        else:
            stop_motors()

        sleep(0.05)

except KeyboardInterrupt:
    stop_motors()
    print("Stopped by user.")
