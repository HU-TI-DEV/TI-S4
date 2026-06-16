import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan
from cv_bridge import CvBridge
import torch
import cv2
import numpy as np

class DoorDetector(Node):

    def __init__(self):
        super().__init__('door_detector')

        self.bridge = CvBridge()

        # Subscribers
        self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)
        self.create_subscription(LaserScan, '/scan', self.lidar_callback, 10)

        # Load model (bijv YOLOv5 custom)
        self.model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)

        self.latest_scan = None

    def lidar_callback(self, msg):
        self.latest_scan = msg

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # PyTorch inference
        results = self.model(frame)

        detections = results.xyxy[0].cpu().numpy()

        for det in detections:
            x1, y1, x2, y2, conf, cls = det

            if conf < 0.5:
                continue

            cls = int(cls)

            # voorbeeld: detecteer alleen personen (test)
            if cls != 0:
                continue

            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0,255,0), 2)

            cx = int((x1 + x2) / 2)
            distance = self.get_distance_from_lidar(cx, frame.shape[1])

            self.get_logger().info(f"Object op {distance:.2f} meter")

    def get_distance_from_lidar(self, pixel_x, width):
        if self.latest_scan is None:
            return -1

        angle = (pixel_x / width) * (self.latest_scan.angle_max - self.latest_scan.angle_min) + self.latest_scan.angle_min

        index = int((angle - self.latest_scan.angle_min) / self.latest_scan.angle_increment)

        if index < 0 or index >= len(self.latest_scan.ranges):
            return -1

        return self.latest_scan.ranges[index]


def main():
    rclpy.init()
    node = DoorDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()