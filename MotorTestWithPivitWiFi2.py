import network
import socket
from machine import Pin, PWM
from time import sleep
import Secrets  # contains SSID and PASSWORD

# Motor pins setup
MA1 = Pin(15, Pin.OUT)
MA2 = Pin(14, Pin.OUT)
MApwm = PWM(Pin(11))
MApwm.freq(1000)

MB1 = Pin(13, Pin.OUT)
MB2 = Pin(12, Pin.OUT)
MBpwm = PWM(Pin(10))
MBpwm.freq(1000)

# Motor control logic
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

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(Secrets.SSID, Secrets.PASSWORD)
print("Connecting to WiFi...")
while not wlan.isconnected():
    sleep(0.5)
ip = wlan.ifconfig()[0]
print(f"Connected, IP address: {ip}")

# Web UI with fullscreen joystick
html = """
<!DOCTYPE html>
<html>
<head>
<title>Fullscreen Joystick Control</title>
<style>
  html, body {
    margin: 0;
    padding: 0;
    overflow: hidden;
    background: #f0f0f0;
    height: 100%;
    width: 100%;
    touch-action: none;
  }

  #joystickBase {
    width: 100vw;
    height: 100vh;
    position: relative;
    background: #f0f0f0;
  }

  #stick {
    width: 80px;
    height: 80px;
    background: #333;
    border-radius: 50%;
    position: absolute;
    left: calc(50% - 40px);
    top: calc(50% - 40px);
    box-shadow: 0 0 20px rgba(0,0,0,0.3);
    touch-action: none;
  }
</style>
</head>
<body>
<div id="joystickBase">
  <div id="stick"></div>
</div>

<script>
let stick = document.getElementById('stick');
let base = document.getElementById('joystickBase');
let dragging = false;

base.addEventListener('touchstart', start, false);
base.addEventListener('touchmove', move, false);
base.addEventListener('touchend', end, false);

base.addEventListener('mousedown', start, false);
window.addEventListener('mousemove', move, false);
window.addEventListener('mouseup', end, false);

function start(e) {
  dragging = true;
  move(e);
}

function move(e) {
  if (!dragging) return;
  let rect = base.getBoundingClientRect();
  let x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
  let y = (e.touches ? e.touches[0].clientY : e.clientY) - rect.top;
  x = Math.max(0, Math.min(rect.width, x));
  y = Math.max(0, Math.min(rect.height, y));

  stick.style.left = (x - 40) + "px";
  stick.style.top = (y - 40) + "px";

  let joyX = Math.round((x / rect.width) * 100);
  let joyY = Math.round((y / rect.height) * 100);

  fetch(`/joy?x=${joyX}&y=${joyY}`);
}

function end(e) {
  dragging = false;
  stick.style.left = "calc(50% - 40px)";
  stick.style.top = "calc(50% - 40px)";
  fetch(`/joy?x=50&y=50`);
}
</script>
</body>
</html>
"""

# Socket server to handle requests
addr = socket.getaddrinfo("0.0.0.0", 8080)[0][-1]
sock = socket.socket()
sock.bind(addr)
sock.listen(1)
print("Listening on http://%s" % ip)

try:
    while True:
        cl, addr = sock.accept()
        request = cl.recv(1024).decode()
#         print("Request:", request)

        if "GET /joy?" in request:
            try:
                # Extract joystick values
                x_part = request.split("x=")[1]
                x = int(x_part.split("&")[0])
                y = int(request.split("y=")[1].split(" ")[0])
                print(f'X = {x}\tY = {y}')

                # Deadzone for smoother control
                dead_zone = 5
                if abs(y - 50) > dead_zone:
                    direction = 'forward' if y < 50 else 'backward'
                    speed_pct = abs(y - 50) * 2
                    base_speed = int((speed_pct / 100) * 65535)

                    # Steering logic based on X axis
                    steering = x - 50
                    if steering < 0:
                        left_scale = 1.0 - (abs(steering) / 50.0)
                        right_scale = 1.0
                    else:
                        left_scale = 1.0
                        right_scale = 1.0 - (abs(steering) / 50.0)

                    # Set motor speeds with scaling based on joystick position
                    set_motor('A', direction, int(base_speed * left_scale))
                    set_motor('B', direction, int(base_speed * right_scale))

                elif abs(x - 50) > dead_zone:
                    # In-place turning
                    turn_speed = int((abs(x - 50) * 2 / 100) * 65535)
                    if x < 50:
                        set_motor('A', 'backward', turn_speed)
                        set_motor('B', 'forward', turn_speed)
                    else:
                        set_motor('A', 'forward', turn_speed)
                        set_motor('B', 'backward', turn_speed)
                else:
                    stop_motors()

            except Exception as e:
                print("Joystick error:", e)

        cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
        cl.send(html)
        cl.close()

except KeyboardInterrupt:
    stop_motors()
    sock.close()
    print("Server stopped.")
