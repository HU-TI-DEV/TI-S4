#!/usr/bin/env python3
import time
import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO

class HybridDetector(Node):

    def __init__(self):
        super().__init__('hybrid_detector')
        self.bridge = CvBridge()

        # Subscribers
        self.sub = self.create_subscription(
            Image,
            '/front/image',
            self.image_cb,
            10
        )
        # Debug image publisher for RViz
        self.pub_debug = self.create_publisher(
            Image,
            '/vision/debug',
            10
        )

        # YOLO
        self.model = YOLO('yolo11n.pt')

        # Performance limiter
        self.last_time = 0.0
        self.min_interval = 0.15

        self.get_logger().info('Hybrid detector started')

    def image_cb(self, msg):
        now = time.time()

        # FPS limiter
        if now - self.last_time < self.min_interval:
            return
        self.last_time = now
        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )
        debug = frame.copy()

        # =====================================================
        # YOLO PERSON DETECTION
        # =====================================================

        results = self.model.predict(
            source=frame,
            imgsz=320,
            conf=0.4,
            classes=[0],
            verbose=False
        )

        person_boxes = []
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0]
                )
                person_boxes.append((x1, y1, x2, y2))
                cv2.rectangle(
                    debug,
                    (x1, y1),
                    (x2, y2),
                    (0, 255, 0),
                    2
                )
                cv2.putText(
                    debug,
                    'person',
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    2
                )

        # =====================================================
        # SIMPLE OBJECT DETECTION
        # =====================================================
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        lower = np.array([40, 60, 60])
        upper = np.array([140, 255, 255])
        mask = cv2.inRange(hsv, lower, upper)
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(
            mask,
            cv2.MORPH_OPEN,
            kernel
        )

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 700:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(
                debug,
                (x, y),
                (x + w, y + h),
                (255, 0, 0),
                2
            )

            cv2.putText(
                debug,
                'object',
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 0, 0),
                2
            )

        # =====================================================
        # PUBLISH TO RVIZ
        # =====================================================

        debug_msg = self.bridge.cv2_to_imgmsg(
            debug,
            encoding='bgr8'
        )
        debug_msg.header = msg.header
        self.pub_debug.publish(debug_msg)


def main(args=None):
    rclpy.init(args=args)
    node = HybridDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()