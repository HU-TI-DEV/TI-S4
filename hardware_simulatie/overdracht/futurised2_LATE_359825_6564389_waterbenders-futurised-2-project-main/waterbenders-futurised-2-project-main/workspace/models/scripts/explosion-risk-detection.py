#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image, FluidPressure
from std_msgs.msg import String

import numpy as np
import cv2
import time

from cv_bridge import CvBridge


class ExplosionRiskNode(Node):

    def __init__(self):

        super().__init__('explosion_risk_node')

        # SUBSCRIBERS

        self.sub_rgb = self.create_subscription(
            Image,
            '/front/image',
            self.rgb_cb,
            10
        )

        self.sub_thermal = self.create_subscription(
            Image,
            '/FLIP/thermal_camera',
            self.thermal_cb,
            10
        )

        self.sub_pressure = self.create_subscription(
            FluidPressure,
            '/air_pressure',
            self.pressure_cb,
            10
        )

        # PUBLISHERS

        self.pub_status = self.create_publisher(
            String,
            '/explosion_risk/status',
            10
        )

        self.pub_debug = self.create_publisher(
            Image,
            '/explosion_risk/debug',
            10
        )

        # VARIABLES

        self.bridge = CvBridge()

        self.rgb = None
        self.thermal = None

        self.pressure = None
        self.previous_pressure = None
        self.pressure_change = 0.0

        self.last_pub_time = 0
        self.min_interval = 0.1

        self.get_logger().info(
            "===== Explosion Risk Node Started ====="
        )

    # CALLBACKS

    def rgb_cb(self, msg):
        self.rgb = msg
        self.try_process()

    def thermal_cb(self, msg):
        self.thermal = msg
        self.try_process()

    def pressure_cb(self, msg):

        pressure = msg.fluid_pressure

        if self.previous_pressure is not None:

            self.pressure_change = abs(
                pressure - self.previous_pressure
            )

        self.previous_pressure = pressure
        self.pressure = pressure

    # MAIN PROCESS

    def try_process(self):

        if self.rgb is None:
            return

        if self.thermal is None:
            return

        now = time.time()

        if now - self.last_pub_time < self.min_interval:
            return

        self.last_pub_time = now

        # RGB IMAGE

        rgb_image = self.bridge.imgmsg_to_cv2(
            self.rgb,
            desired_encoding='bgr8'
        )

        # THERMAL IMAGE

        thermal_raw = np.frombuffer(
            self.thermal.data,
            dtype=np.uint16
        ).reshape(
            (
                self.thermal.height,
                self.thermal.width
            )
        )

        temp_celsius = (
            thermal_raw.astype(np.float32) * 0.01
        ) - 273.15

        center_temp = temp_celsius[
            temp_celsius.shape[0] // 2,
            temp_celsius.shape[1] // 2
        ]

        # EXPLOSION RISK SCORE

        risk_score = 0

        # Temperature contribution
        if center_temp > 60:
            risk_score += 20

        if center_temp > 100:
            risk_score += 20

        if center_temp > 150:
            risk_score += 20

        # Pressure contribution
        if self.pressure_change > 5:
            risk_score += 20

        if self.pressure_change > 15:
            risk_score += 20

        # RISK LEVEL

        if risk_score >= 80:
            status_text = "HIGH_RISK"
            color = (0, 0, 255)

        elif risk_score >= 50:
            status_text = "MEDIUM_RISK"
            color = (0, 165, 255)

        elif risk_score >= 20:
            status_text = "LOW_RISK"
            color = (0, 255, 255)

        else:
            status_text = "SAFE"
            color = (0, 255, 0)

        # PUBLISH STATUS

        status_msg = String()
        status_msg.data = status_text
        self.pub_status.publish(status_msg)

        # DEBUG VISUALIZATION

        debug = rgb_image.copy()

        cv2.putText(
            debug,
            f'EXPLOSION RISK: {status_text}',
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            3
        )

        cv2.putText(
            debug,
            f'Score: {risk_score}',
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            color,
            2
        )

        cv2.putText(
            debug,
            f'Temp: {center_temp:.1f}C',
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        cv2.putText(
            debug,
            f'Pressure Δ: {self.pressure_change:.2f}',
            (20, 160),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )

        # PUBLISH DEBUG IMAGE

        debug_msg = self.bridge.cv2_to_imgmsg(
            debug,
            encoding='bgr8'
        )

        self.pub_debug.publish(debug_msg)


# MAIN

def main(args=None):

    rclpy.init(args=args)

    node = ExplosionRiskNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()