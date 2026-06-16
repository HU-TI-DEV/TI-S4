
"""Subscriber and publisher demo for GreenDigger sensor and command flow.

This script subscribes to IMU, LIDAR, GPS, camera, and contact sensors, prints
terminal feedback, and publishes velocity commands to the
GreenDigger. It supports a PID heading rotation, and can optionally be switched to keyboard
control by uncommenting the keyboard line at the bottom of this file.

    Author: Ocarian
"""

import sys
import time
from gz.transport import Node

from gz.msgs.twist_pb2 import Twist
from gz.msgs.imu_pb2 import IMU
from gz.msgs.image_pb2 import Image
from gz.msgs.laserscan_pb2 import LaserScan
from gz.msgs.navsat_pb2 import NavSat
from gz.msgs.contacts_pb2 import Contacts
from keyboard_publisher import get_twist_from_keyboard
from pid_heading import rotate_to_target_yaw

node = Node()
last_time = 0
USE_PID = True
PID_TARGET_DEG = 140.0
PID_DURATION_S = 60.0

# Publisher
pub = node.advertise("/model/digger/cmd_vel", Twist)

# Callbacks
def imu_cb(msg):
    sys.stdout.write("\r")
    print(f"[IMU] ang vel: {msg.angular_velocity.z:.2f}", flush=True)

def lidar_cb(msg):
    sys.stdout.write("\r")
    print(f"[LIDAR] first range: {msg.ranges[0]:.2f}", flush=True)

def gps_cb(msg):
    sys.stdout.write("\r")
    print(f"[GPS] lat: {msg.latitude_deg:.5f}, lon: {msg.longitude_deg:.5f}, alt: {msg.altitude:.2f}", flush=True)

def camera_cb(msg):
    sys.stdout.write("\r")
    print(f"[CAM] {msg.width}x{msg.height}", flush=True)

def contact_cb(msg):
    global last_time

    if len(msg.contact) > 0:
        now = time.time()
        if now - last_time >= 1.0:
            sys.stdout.write("\r")
            print("[CONTACT] Chassis touching something", flush=True)
            last_time = now

# Subscribers
node.subscribe(IMU, "/digger/imu", imu_cb)
node.subscribe(LaserScan, "/digger/lidar", lidar_cb)
node.subscribe(NavSat, "/digger/gps", gps_cb)
node.subscribe(Image, "/digger/camera", camera_cb)
node.subscribe(Contacts, "/world/starting_environment/model/digger/model/digger/link/chassis/sensor/contact_sensor_chassis/contact", contact_cb)

# Publish movement commands
msg = Twist()
msg.linear.x = 0.0
msg.angular.z = 0.0

if USE_PID:
    rotate_to_target_yaw(
        target_heading_degrees=PID_TARGET_DEG,
        max_duration_s=PID_DURATION_S,
    )
    time.sleep(1.0)  # wait a bit before sending new commands

print("Publishing + listening...")

while True:

    # UNCOMMENT FOR KEYBOARD CONTROL
    # msg = get_twist_from_keyboard()

    pub.publish(msg)
    time.sleep(0.05)
    