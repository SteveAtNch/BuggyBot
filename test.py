from time import sleep
from MG90SClass import MG90S

servo = MG90S(pin_number=15)

servo.go_to(0)       # Go to center
servo_delay = .004


while True:
    d = int(input("angle: "))
    servo.go_to(d)
# while True:
#     for d in range(0, 181, 1):
#         servo.go_to(d-90)
#         sleep(servo_delay)
#         print(d)
#     for d in range(179, 0, -1):
#         servo.go_to(d-90)
#         sleep(servo_delay)
#         print(d)
