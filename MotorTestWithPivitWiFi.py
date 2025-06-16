import network
import socket
from machine import Pin, PWM
from time import sleep
import Secrets  # contains SSID and PASSWORD

# Motor A (left)
MA1 = Pin(15, Pin.OUT)
MA2 = Pin(14, Pin.OUT)
MApwm = PWM(Pin(11))
MApwm.freq(1000)

# Motor B (right)
MB1 = Pin(13, Pin.OUT)
MB2 = Pin(12, Pin.OUT)
MBpwm = PWM(Pin(10))
MBpwm.freq(1000)

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
    for pin in [MA1, MA2, MB1, MB2]:
        pin.value(0)
    MApwm.duty_u16(0)
    MBpwm.duty_u16(0)

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(Secrets.SSID, Secrets.PASSWORD)

print("Connecting to WiFi...")
while not wlan.isconnected():
    sleep(0.5)

ip = wlan.ifconfig()[0]
print(f"Connected, IP: {ip}")

# Web server
html = """<!DOCTYPE html>
<html>
<head><title>Motor Control</title></head>
<body>
<h2>Control Motors</h2>
<form>
  <button name="cmd" value="F">Forward</button>
  <button name="cmd" value="B">Backward</button>
  <button name="cmd" value="L">Left</button>
  <button name="cmd" value="R">Right</button>
  <button name="cmd" value="S">Stop</button>
</form>
</body>
</html>
"""

# Start listening
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
sock = socket.socket()
sock.bind(addr)
sock.listen(1)
print("Listening on", addr)

try:
    while True:
        cl, addr = sock.accept()
        request = cl.recv(1024).decode()
        print("Request:", request)

        # Determine command
        cmd = ""
        if 'GET /?cmd=' in request:
            cmd = request.split('GET /?cmd=')[1].split(' ')[0]
            print("Command:", cmd)

        if cmd == "F":
            set_motor('A', 'forward', 40000)
            set_motor('B', 'forward', 40000)
        elif cmd == "B":
            set_motor('A', 'backward', 40000)
            set_motor('B', 'backward', 40000)
        elif cmd == "L":
            set_motor('A', 'backward', 30000)
            set_motor('B', 'forward', 30000)
        elif cmd == "R":
            set_motor('A', 'forward', 30000)
            set_motor('B', 'backward', 30000)
        elif cmd == "S":
            stop_motors()

        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(html)
        cl.close()

except KeyboardInterrupt:
    stop_motors()
    sock.close()
    print("Server stopped.")
