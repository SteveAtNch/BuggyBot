import uasyncio as asyncio
from machine import Pin, PWM
import time
import socket
import network
import secrets
import _thread
from array import array
import gc

# Set up Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)

# Wait for connection
while not wlan.isconnected():
    time.sleep(0.5)
print("Connected to Wi-Fi:", wlan.ifconfig()[0])

# Constants
ANGLE_MIN = -80
ANGLE_MAX = 80
TOTAL_POINTS = ANGLE_MAX - ANGLE_MIN + 1  # 161 points

# Shared distance data (initialize with zeros)
distance_data = array('H', [0] * TOTAL_POINTS)

# Servo Setup
servo = PWM(Pin(15), freq=50)

def angle_to_duty(angle):
    return int((angle + 90) * (8000 / 180) + 2000)

def set_servo_angle(angle):
    duty = angle_to_duty(angle)
    servo.duty_u16(duty)

# Ultrasonic sensor
TRIG = Pin(3, Pin.OUT)
ECHO = Pin(2, Pin.IN)

def read_distance():
    TRIG.low()
    time.sleep_us(2)
    TRIG.high()
    time.sleep_us(10)
    TRIG.low()

    while ECHO.value() == 0:
        signaloff = time.ticks_us()
    while ECHO.value() == 1:
        signalon = time.ticks_us()

    time_passed = time.ticks_diff(signalon, signaloff)
    distance_cm = (time_passed * 0.0343) / 2
    return int(distance_cm) if 2 < distance_cm < 400 else 0

# CPU1 scanning task
def scan_loop():
    global distance_data
    while True:
        for i in range(TOTAL_POINTS):
            angle = ANGLE_MIN + i
            set_servo_angle(angle)
            time.sleep(0.04)
            distance = read_distance()
            distance_data[i] = distance
            gc.collect()
        time.sleep(0.2)

# Start CPU1 scanning
_thread.start_new_thread(scan_loop, ())

# Web server
async def handle_client(reader, writer):
    request_line = await reader.readline()
    if not request_line:
        await writer.aclose()
        return

    request = request_line.decode()
    if "/data" in request:
        response = ",".join(str(d) for d in distance_data)
        await writer.awrite("HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\n")
        await writer.awrite(response)
    else:
        await writer.awrite("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
        await writer.awrite(html_page)

    await writer.aclose()

# HTML page with radar chart
html_page = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Radar View</title>
  <style>
    body { margin: 0; background: black; }
    canvas { display: block; margin: auto; background: black; }
  </style>
</head>
<body>
  <canvas id="radar" width="400" height="400"></canvas>
  <script>
    const canvas = document.getElementById("radar");
    const ctx = canvas.getContext("2d");
    const centerX = canvas.width / 2;
    const centerY = canvas.height;
    const maxRadius = canvas.height;

    const TOTAL_POINTS = 161;
    const ANGLE_MIN = -80;
    const ANGLE_MAX = 80;

    function drawRadar(data) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = "lime";
      ctx.beginPath();
      for (let i = 0; i < TOTAL_POINTS; i++) {
        const angleDeg = ANGLE_MIN + i;
        const angleRad = angleDeg * Math.PI / 180;
        const dist = Math.min(data[i], 200); // Auto-range to 200 cm
        const r = dist * 2; // scale for canvas
        const x = centerX + r * Math.sin(angleRad);
        const y = centerY - r * Math.cos(angleRad);
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
    }

    async function fetchData() {
      try {
        const res = await fetch("/data");
        const text = await res.text();
        const data = text.split(",").map(Number);
        if (data.length === TOTAL_POINTS) drawRadar(data);
      } catch (e) {
        console.error("Data fetch error", e);
      }
    }

    setInterval(fetchData, 500);
  </script>
</body>
</html>
"""

# Start async web server
async def main():
    server = await asyncio.start_server(handle_client, "0.0.0.0", 80)
    print("Web server running...")
    while True:
        await asyncio.sleep(1)


asyncio.run(main())
