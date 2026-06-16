#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import gz.transport as gz
from gz.msgs import image_pb2

import numpy as np


FRONT_TOPIC = "/front/image"
REAR_TOPIC = "/rear/image"
THERMAL_TOPIC = "/FLIP/thermal_camera"


class CameraBridge(Node):

    def __init__(self):
        super().__init__("camera_bridge")

        # ROS publishers (for RViz)
        self.pub_front = self.create_publisher(Image, "/camera/front", 10)
        self.pub_rear = self.create_publisher(Image, "/camera/rear", 10)

        self.bridge = CvBridge()

        # Gazebo node
        self.node = gz.Node()

        # Subscriptions (Gazebo → Python)
        self.node.subscribe(
            image_pb2.Image,
            FRONT_TOPIC,
            self.front_cb
        )

        self.node.subscribe(
            image_pb2.Image,
            REAR_TOPIC,
            self.rear_cb
        )

        self.get_logger().info("Camera bridge started (Gazebo → RViz)")

    # -------------------------
    # IMAGE CONVERSION
    # -------------------------
    def convert(self, msg):

        img = np.frombuffer(msg.data, dtype=np.uint8)

        if msg.pixel_format_type == 3:
            img = img.reshape((msg.height, msg.width, 3))
            return img

        elif msg.pixel_format_type == 4:
            img = img.reshape((msg.height, msg.width, 4))
            img = img[:, :, :3]
            return img

        elif msg.pixel_format_type == 1:
            img = img.reshape((msg.height, msg.width))
            img = np.stack([img]*3, axis=-1)
            return img

        else:
            self.get_logger().warn("Unsupported format")
            return None

    # -------------------------
    # CALLBACKS
    # -------------------------
    def front_cb(self, msg):
        img = self.convert(msg)
        if img is None:
            return

        ros_msg = self.bridge.cv2_to_imgmsg(img, encoding="rgb8")
        ros_msg.header.stamp = self.get_clock().now().to_msg()
        ros_msg.header.frame_id = "front_camera"

        self.pub_front.publish(ros_msg)

    def rear_cb(self, msg):
        img = self.convert(msg)
        if img is None:
            return

        ros_msg = self.bridge.cv2_to_imgmsg(img, encoding="rgb8")
        ros_msg.header.stamp = self.get_clock().now().to_msg()
        ros_msg.header.frame_id = "rear_camera"

        self.pub_rear.publish(ros_msg)


# -------------------------
# MAIN
# -------------------------
def main(args=None):
    rclpy.init(args=args)
    node = CameraBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
