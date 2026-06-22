# TurtleBot4 Flask Web Dashboard

A lightweight web-based control dashboard for **TurtleBot4** built using **Flask** and **ROS2 Humble**.

The dashboard allows remote robot control from any device on the same network through a browser, without requiring direct terminal access.

---

## Features

### Teleoperation

Control the TurtleBot4 using on-screen buttons:

- Forward
- Backward
- Left
- Right
- Stop

Supports:

- Mouse control
- Touchscreen control
- Continuous movement while holding buttons

### Keyboard Control

Use keyboard shortcuts directly from the browser:

| Key | Action |
|-------|---------|
| W | Forward |
| A | Left |
| S | Backward |
| D | Right |
| Space | Stop |

---

### Battery Monitoring

Displays live TurtleBot4 battery percentage by subscribing to:

```text
/battery_state
```

Battery updates automatically on the webpage without requiring a page refresh.

---

### Docking Controls

Provides quick access to:

- Dock
- Undock

for autonomous charging operations.

---

## System Architecture

```text
┌─────────────┐
│ Web Browser │
└──────┬──────┘
       │ HTTP Requests
       ▼
┌─────────────┐
│ Flask App   │
└──────┬──────┘
       │ ROS2 Publisher
       ▼
┌─────────────┐
│  /cmd_vel   │
└──────┬──────┘
       ▼
┌─────────────┐
│ TurtleBot4  │
└─────────────┘
```

Battery monitoring:

```text
TurtleBot4
    │
    ▼
 /battery_state
    │
    ▼
 Flask Subscriber
    │
    ▼
 Web Dashboard
```

---

## Requirements

### Hardware

- TurtleBot4
- Laptop/PC
- Common Wi-Fi Network

### Software

- Ubuntu 22.04
- ROS2 Humble
- Python 3

---

## Dependencies

Install Flask:

```bash
pip install flask
```

Install ROS2 packages:

```bash
sudo apt install ros-humble-desktop
```

---

## ROS Configuration

Ensure both the laptop and TurtleBot4 are using the same ROS Domain ID.

Example:

```bash
export ROS_DOMAIN_ID=0
```

Verify communication:

```bash
ros2 topic list
```

You should see topics such as:

```text
/cmd_vel
/battery_state
/odom
/scan
```

---

## Running the Dashboard

Source ROS2:

```bash
source /opt/ros/humble/setup.bash
```

Run the Flask server:

```bash
python3 app.py
```

Expected output:

```text
Running on http://0.0.0.0:5000
```

Open the dashboard:

```text
http://<laptop-ip>:5000
```

Example:

```text
http://192.168.240.117:5000
```

---

## ROS Topics Used

### Published

```text
/cmd_vel
```

Message Type:

```text
geometry_msgs/msg/Twist
```

Used for robot movement commands.

---

### Subscribed

```text
/battery_state
```

Message Type:

```text
sensor_msgs/msg/BatteryState
```

Used for live battery monitoring.

---

## Project Structure

```text
web_control/
│
├── app.py
│
├── templates/
│   └── index.html
│
├── static/
│   └── style.css
│
└── README.md
```

---

## Future Improvements

- Live Camera Feed
- Dock Status Monitoring
- Robot Pose Display
- Live Map Visualization
- Click-to-Navigate Goals
- Navigation Status
- Emergency Stop
- Multi-Robot Support
- Mobile Responsive Interface

---

## Screenshot

```text
┌─────────────────────────────┐
│     TurtleBot4 Dashboard    │
└─────────────────────────────┘

┌─────────────────────────────┐
│ Battery Status              │
│                             │
│          83.4 %             │
└─────────────────────────────┘

┌─────────────────────────────┐
│ Teleoperation               │
│             ↑               │
│                             │
│      ←   STOP   →           │
│                             │
│             ↓               │
└─────────────────────────────┘

┌─────────────────────────────┐
│ Docking Controls            │
│                             │
│ [ Dock ] [ Undock ]         │
└─────────────────────────────┘
```

---

## Author

Pulkit Garg

Robotics | ROS2 | Autonomous Systems | Computer Vision