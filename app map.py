from flask import Flask, render_template, jsonify
from sensor_msgs.msg import BatteryState

from rclpy.qos import QoSProfile
from rclpy.qos import ReliabilityPolicy
from rclpy.qos import DurabilityPolicy
from rclpy.qos import HistoryPolicy
import threading
from rclpy.qos import qos_profile_sensor_data

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from rclpy.action import ActionClient

from irobot_create_msgs.action import Dock
from irobot_create_msgs.action import Undock
import subprocess
import signal
from nav_msgs.msg import OccupancyGrid
from flask import send_file
import numpy as np
from PIL import Image
import io



app = Flask(__name__)

rclpy.init()


class WebTeleop(Node):

    def __init__(self):
        super().__init__('web_teleop')
        self.pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        battery_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        self.battery = 0.0
        self.battery_sub = self.create_subscription(
            BatteryState,
            '/battery_state',
            self.battery_callback,
            battery_qos
        )

        self.dock_client = ActionClient(
            self,
            Dock,
            '/dock'
        )

        self.undock_client = ActionClient(
            self,
            Undock,
            '/undock'
        )

        map_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )
        
        self.map_data = None

        self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            map_qos
        )


    def battery_callback(self, msg):

        self.battery = msg.percentage * 100
        print(f"Battery: {self.battery:.1f}%")

    def dock(self):

        goal = Dock.Goal()
        self.dock_client.wait_for_server()
        self.dock_client.send_goal_async(goal)

        print("Dock command sent")

    def undock(self):

        goal = Undock.Goal()
        self.undock_client.wait_for_server()
        self.undock_client.send_goal_async(goal)

        print("Undock command sent")

    def map_callback(self,msg):

        self.map_data = msg

    def send_cmd(self, linear, angular):

        msg = Twist()

        msg.linear.x = linear
        msg.angular.z = angular

        self.pub.publish(msg)

teleop = WebTeleop()

threading.Thread(
    target=rclpy.spin,
    args=(teleop,),
    daemon=True
).start()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/forward')
def forward():

    teleop.send_cmd(0.2,0.0)

    return "ok"


@app.route('/backward')
def backward():

    teleop.send_cmd(-0.2,0.0)

    return "ok"


@app.route('/left')
def left():

    teleop.send_cmd(0.0,0.5)

    return "ok"


@app.route('/right')
def right():

    teleop.send_cmd(0.0,-0.5)

    return "ok"


@app.route('/stop')
def stop():

    teleop.send_cmd(0.0,0.0)

    return "ok"

@app.route('/battery')
def battery():

    return jsonify(
        battery=teleop.battery
    )

@app.route('/dock')
def dock():

    teleop.dock()

    return "ok"

@app.route('/undock')
def undock():

    teleop.undock()

    return "ok"


slam_process = None
@app.route('/start_mapping')
def start_mapping():

    global slam_process

    if slam_process is None or slam_process.poll() is not None:

        slam_process = subprocess.Popen(
            """
            source /opt/ros/humble/setup.bash
            ros2 launch turtlebot4_navigation slam.launch.py
            """,
            shell=True,
            executable="/bin/bash"
        )

    return "Mapping Started"


@app.route('/save_map')
def save_map():

    subprocess.Popen([
        "ros2",
        "service",
        "call",
        "/slam_toolbox/save_map",
        "slam_toolbox/srv/SaveMap",
        "{name: {data: '/home/pg/web_control/maps/web_map'}}"
    ])

    return "Map Saved"

@app.route('/map_image')
def map_image():

    if teleop.map_data is None:
        return "No map yet", 404

    msg = teleop.map_data

    width = msg.info.width
    height = msg.info.height

    data = np.array(msg.data, dtype=np.int16)

    img = np.zeros_like(data, dtype=np.uint8)

    img[data == -1] = 127
    img[data == 0] = 255
    img[data > 50] = 0

    img = img.reshape((height, width))

    img = np.flipud(img)

    image = Image.fromarray(img)

    buffer = io.BytesIO()

    image.save(buffer, format="PNG")

    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="image/png"
    )

try:
    app.run(host='0.0.0.0', port=5000)
finally:
    teleop.destroy_node()
    rclpy.shutdown()