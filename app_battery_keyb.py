from flask import Flask, render_template, jsonify
from sensor_msgs.msg import BatteryState

from rclpy.qos import QoSProfile
from rclpy.qos import ReliabilityPolicy
from rclpy.qos import DurabilityPolicy
from rclpy.qos import HistoryPolicy
import threading

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

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

    def battery_callback(self, msg):

        self.battery = msg.percentage * 100
        print(f"Battery: {self.battery:.1f}%")

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)