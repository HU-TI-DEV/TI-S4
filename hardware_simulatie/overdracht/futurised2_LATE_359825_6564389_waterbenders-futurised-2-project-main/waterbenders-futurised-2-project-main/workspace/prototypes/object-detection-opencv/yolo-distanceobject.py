import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2
import numpy as np

from ultralytics import YOLO


class ObjectDistanceScanner(Node):

    def __init__(self):

        super().__init__('object_distance_scanner')

        self.bridge = CvBridge()

        # RGB CAMERA
        self.rgb_subscription = self.create_subscription(
            Image,
            '/front/image',
            self.rgb_callback,
            10
        )

        # DEPTH CAMERA
        self.depth_subscription = self.create_subscription(
            Image,
            '/depth_camera',
            self.depth_callback,
            10
        )

        # YOLO MODEL
        self.model = YOLO('yolov8n.pt')

        self.class_names = self.model.names

        # LATEST DEPTH FRAME
        self.depth_frame = None

        self.get_logger().info(
            "Object Distance Scanner Started"
        )

    def depth_callback(self, msg):

        # DEPTH IMAGE -> OPENCV
        self.depth_frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='passthrough'
        )

    def rgb_callback(self, msg):

        # WACHT TOT DEPTH IMAGE BESCHIKBAAR IS
        if self.depth_frame is None:
            return

        # RGB IMAGE -> OPENCV
        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )

        frame_height, frame_width = frame.shape[:2]

        # YOLO DETECTION
        results = self.model(frame)

        # IMAGE MET YOLO BOXES
        annotated_frame = results[0].plot()

        # LOOP THROUGH OBJECTS
        for box in results[0].boxes:

            # CLASS ID
            cls_id = int(box.cls[0])

            # CLASS NAME
            class_name = self.class_names[cls_id]

            # CONFIDENCE
            confidence = float(box.conf[0])

            # CONFIDENCE FILTER
            if confidence < 0.5:
                continue

            # BOUNDING BOX
            x1, y1, x2, y2 = box.xyxy[0]

            x1, y1, x2, y2 = map(
                int,
                [x1, y1, x2, y2]
            )

            # CHECK OF OBJECT VOLLEDIG IN BEELD STAAT
            fully_visible = (
                x1 > 0 and
                y1 > 0 and
                x2 < frame_width and
                y2 < frame_height
            )

            # SKIP ALS OBJECT NIET VOLLEDIG ZICHTBAAR IS
            if not fully_visible:
                continue

            # MIDDEN VAN OBJECT
            center_x = int((x1 + x2) / 2)
            center_y = int((y1 + y2) / 2)

            # CHECK OF PIXEL BESTAAT
            if (
                center_y >= self.depth_frame.shape[0]
                or
                center_x >= self.depth_frame.shape[1]
            ):
                continue

            # DEPTH WAARDE OPHALEN
            distance = self.depth_frame[
                center_y,
                center_x
            ]

            # CHECK OP ONGELDIGE WAARDES
            if np.isnan(distance):
                continue

            if distance <= 0:
                continue

            # PRINT RESULTAAT
            print(
                f"Object: {class_name} | "
                f"Confidence: {confidence:.2f} | "
                f"Distance: {distance:.2f} meters"
            )

            # TEKST OP SCHERM
            cv2.putText(
                annotated_frame,
                f"{class_name} {distance:.2f}m",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            # MIDDENPUNT TEKENEN
            cv2.circle(
                annotated_frame,
                (center_x, center_y),
                5,
                (0, 0, 255),
                -1
            )

        # TOON RESULTAAT
        cv2.imshow(
            "Object Distance Scanner",
            annotated_frame
        )

        cv2.waitKey(1)


def main(args=None):

    rclpy.init(args=args)

    node = ObjectDistanceScanner()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()