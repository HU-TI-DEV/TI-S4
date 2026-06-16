"""
Navigate the digger to a target position using PID heading control.

    Author: GrijzePanda
"""
import math
import time
import sys
from gz.transport import Node
from gz.msgs.twist_pb2 import Twist
from gz.msgs.imu_pb2 import IMU

import code.tests.pid_heading as pid_heading  # Ocarian's PID controller

INTERFACE_DIRECTORY = "interface"
if INTERFACE_DIRECTORY not in sys.path:
    sys.path.insert(0, INTERFACE_DIRECTORY)

import interface

POSITION_TOLERANCE = 2
MAX_LINEAR_SPEED = 2.5
HEADING_THRESHOLD = math.radians(25)
CONTROL_INTERVAL = 0.1


def setup():
    node = Node()

    pose_received = None

    # Pose subscriber
    interface.start_subscribers()

    # Publisher to publish movements
    pub = node.advertise("/model/digger/cmd_vel", Twist)

    # IMU subscriber (from Ocarian's pid_heading)
    node.subscribe(
        IMU,
        "/digger/imu",
        pid_heading.imu_callback,
    )

    print("Waiting for pose + IMU data...")

    while not pose_received or not pid_heading.imu_data_ready:
        state = interface.get_state()
        if state["pose"]["current_x"] is not None and state["pose"]["current_y"] is not None:
            pose_received = True
        time.sleep(0.1)

    print("Pose + IMU data received.")

    return node, pub


def navigate_to(x: float, y: float):
    target_x, target_y = x, y

    while True:
        state = interface.get_state()
        
        current_x = state["pose"]["current_x"]
        current_y = state["pose"]["current_y"]
        
        dx = target_x - current_x
        dy = target_y - current_y

        distance = math.sqrt(dx * dx + dy * dy)

        if distance < POSITION_TOLERANCE:

            stop_msg = Twist()
            pub.publish(stop_msg)

            print("\nTarget reached.")
            return

        # PID stuff
        target_yaw = math.atan2(dy, dx)

        yaw_error = pid_heading.normalize_angle(target_yaw - pid_heading.current_yaw)

        angular_cmd = pid_heading.compute_heading_control(
            target_yaw,
            CONTROL_INTERVAL,
        )

        linear_cmd = MAX_LINEAR_SPEED
        
        # Slows down to rotate in place if badly aligned
        heading_scale = max(
            0.0,
            1.0 - abs(yaw_error) / math.radians(90)
        )

        linear_cmd *= heading_scale

        # Proportional slow down near target
        if distance < 4.0:
            linear_cmd *= max(0.25, distance / 4.0)

        msg = Twist()

        msg.linear.x = linear_cmd
        msg.angular.z = angular_cmd

        pub.publish(msg)

        # Useful stuff for in the terminal
        print(
            f"\r"
            f"target=({target_x:.1f},{target_y:.1f}) "
            f"x={current_x:.2f} "
            f"y={current_y:.2f} "
            f"dist={distance:.2f} "
            f"yaw_err={math.degrees(yaw_error):.1f}° "
            f"lin={linear_cmd:.2f} "
            f"ang={angular_cmd:.2f}",
            end="",
            flush=True,
        )

        time.sleep(CONTROL_INTERVAL)
