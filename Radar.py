import socket
import json
from machine import Pin
from time import sleep_ms
import _thread
import secrets
import network
from UltrasonicSensorClass import UltrasonicSensor
from RunningFilterClass import RunningFilter
from MG90SClass import MG90S
from OLEDclass import OLEDDisplay
import gc


# Constants
SERVO_PIN = 15
TRIG_PIN = 3
ECHO_PIN = 2
SCL_PIN = 17
SDA_PIN = 16
WIDTH = 128
HEIGHT = 32

MIN_ANGLE = -90
MAX_ANGLE = 90
ANGLE_RANGE = MAX_ANGLE - MIN_ANGLE + 1
distance_data = [0] * ANGLE_RANGE  # Array from -90 to +90

# Initialize OLED
oled = OLEDDisplay(scl_pin=SCL_PIN, sda_pin=SDA_PIN, width=WIDTH, height=HEIGHT)
oled.clear()
oled.display.write_text("BuggyBot", x=0, y=HEIGHT//4, size=2)
oled.update()

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(secrets.SSID, secrets.PASSWORD)
while not wlan.isconnected():
    sleep_ms(100)
print("Connected to WiFi:", wlan.ifconfig())
oled.display.fill_rect(0, 0, WIDTH, HEIGHT, 0)
oled.display.write_text("WiFi OK", x=10, y=10, size=1)
oled.update()

# HTML page with half-circle radar chart
html = """\
HTTP/1.0 200 OK

<!DOCTYPE html>
<html>
<head>
  <title>BuggyBot Radar Scan</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { font-family: Arial; text-align: center; }
    canvas { max-width: 500px; }
  </style>
</head>
<body>
  <h2>BuggyBot Radar Scan</h2>
  <canvas id="radarChart"></canvas>

  <script>
    const ctx = document.getElementById('radarChart').getContext('2d');

    // Labels from 90 to -90 for half circle
    const angles = [...Array(181).keys()].map(i => 90 - i);

    const data = {
      labels: angles.map(a => a.toString()),
      datasets: [{
        label: 'Distance (cm)',
        data: new Array(181).fill(0),
        fill: true,
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgb(54, 162, 235)',
        pointRadius: 2,
        tension: 0.1
      }]
    };

    const radarChart = new Chart(ctx, {
      type: 'radar',
      data: data,
      options: {
        animation: false,
        responsive: true,
        aspectRatio: 1.5,
        scales: {
          r: {
            beginAtZero: true,
            suggestedMax: 200,
            startAngle: 180,
            min: 0,
            max: 200,
            ticks: {
              backdropColor: 'transparent'
            },
            pointLabels: {
              display: true,
              centerPointLabels: true,
              font: {
                size: 10
              }
            },
            angleLines: {
              display: true
            },
            grid: {
              circular: true
            }
          }
        },
        plugins: {
          legend: {
            display: false
          }
        },
        elements: {
          line: {
            borderWidth: 2
          }
        }
      }
    });

    async function updateData() {
      const res = await fetch('/data');
      const json = await res.json();
      radarChart.data.datasets[0].data = json.slice().reverse(); // Reverse to match label order
      radarChart.update();
    }

    setInterval(updateData, 500);
  </script>
</body>
</html>
"""

def load_html():
    try:
        with open('index.html', 'r') as f:
            return f.read()
    except Exception as e:
        print("Error loading index.html:", e)
        return "<h1>Error loading page</h1>"
    
# Web server on CPU0
def start_server():
    addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Avoid EADDRINUSE
    s.bind(addr)
    s.listen(1)
    print("Web server running on http://%s" % wlan.ifconfig()[0])

    try:
        while True:
            cl, addr = s.accept()
            req = cl.recv(1024).decode()
            print("Request:", req)

            if "GET /data" in req:
                print("Sending distance data:", distance_data)
                cl.send("HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n")
                cl.send(json.dumps(distance_data))
            elif "GET /" in req:
                cl.send("HTTP/1.0 200 OK\r\nContent-Type: text/html\r\n\r\n")
                cl.send(load_html())
            else:
                cl.send("HTTP/1.0 404 Not Found\r\nContent-Type: text/plain\r\n\r\nPage not found.")
            cl.close()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        s.close()

# Scanner thread on CPU1
def scanner_task():
    global distance_data
    print('Scanner started')
    try:
        servo = MG90S(SERVO_PIN)
        sensor = UltrasonicSensor(trig_pin=TRIG_PIN, echo_pin=ECHO_PIN)
        filter = RunningFilter(tank_size=2)

        directions = [range(MIN_ANGLE, MAX_ANGLE + 1), range(MAX_ANGLE, MIN_ANGLE - 1, -1)]
        while True:
            for direction in directions:
                for angle in direction:
                    servo.go_to(angle)
                    sleep_ms(40)
                    reading = sensor.measure_distance()
                    if reading is not None:
                        filter.add(reading)
                        distance_data[angle - MIN_ANGLE] = filter.average()
                    else:
                        distance_data[angle - MIN_ANGLE] = 0

                    oled.display.fill_rect(0, 0, WIDTH, HEIGHT, 0)
                    oled.display.write_text("Angle: {}".format(angle), x=0, y=0, size=1)
                    oled.display.write_text("Dist: {}cm".format(int(distance_data[angle - MIN_ANGLE])), x=0, y=10, size=1)
                    oled.update()
                    sleep_ms(5)
                    print("Free memory:", gc.mem_free())
    except Exception as e:
        gc.collect()
        print("Error in scanner task:", e)

# Run server and scanner
print('Starting CPU1 tasks.')
_thread.start_new_thread(scanner_task, ())
sleep_ms(50)
print('starting server')
start_server()


