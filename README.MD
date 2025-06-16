# 🤖 BuggyBot: Smart Autonomous Rover with Web Radar

BuggyBot is a Wi-Fi-controlled, sensor-driven autonomous vehicle based on the Raspberry Pi Pico W. It features real-time obstacle detection, radar-style scanning, power monitoring, and a web-based dashboard for interactive control and feedback.

---

## 🚀 Features

- **Raspberry Pi Pico W (Dual Core)**
- **MG90S Servo**: Rotates the ultrasonic sensor to scan from -90° to +90°
- **Ultrasonic Sensor**: Measures distances and generates a radar view
- **OLED Display (SSD1306)**: Shows voltage, current, power, and charge %
- **INA219 Power Sensor**: Monitors current, voltage, power, AH, and charge state
- **Dual Motor Drive**: Controls two DC motors (rear-wheel drive) with front caster
- **Wi-Fi Web UI**: Displays radar sweep with auto-scaling and live data
- **MicroPython**: Clean, modular code running on the Pico W
- **SD Card Logging** (Optional): Record sensor data over time

---

## 📷 Project Preview

![BuggyBot Radar UI](./docs/screenshot-radar.png)

---

## 🛠️ Hardware Requirements

- Raspberry Pi Pico W
- L298N or DRV8833 Dual H-Bridge Motor Driver
- 2 x DC Gear Motors + Caster Wheel
- MG90S Servo
- HC-SR04 Ultrasonic Distance Sensor
- INA219 Current/Voltage Sensor
- SSD1306 I2C OLED (128x64)
- Micro SD card reader (optional)
- Li-ion Battery Pack (7.4V or 11.1V recommended)
- Resistor divider for battery monitoring (e.g., 9K + 5K)
- Breadboard or custom PCB
- Jumper wires

---

## 🧠 Software Features

- Multicore support:  
  - **Core 0**: Web server, display updates, battery logic  
  - **Core 1**: Servo scan, stepper/ultrasonic measurement loop

- Filtering:  
  - **EMA filter** for stable readings  
  - Optional Kalman filter for advanced smoothing

- Display Metrics:  
  - Voltage (V), Current (mA), Power (W)  
  - Discharge rate (W), Total AH, Battery % charge

- Web UI:  
  - Live radar chart (180° sweep, polar graph)  
  - No labels, 0° up, auto-ranging based on distance  
  - Serves over Wi-Fi using MicroPython's `socket`

---

## 📂 File Structure

