import os

import numpy as np

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image

from ultralytics import YOLO


def find_model_path(filename='best.pt'):
    candidates = []

    repo_env = os.environ.get('TONK_REPO')
    if repo_env:
        candidates.append(os.path.join(repo_env, 'vision', 'models', filename))

    candidates.append(os.path.join('/workspace', 'vision', 'models', filename))

    current = os.path.dirname(os.path.realpath(__file__))
    for _ in range(10):
        candidates.append(os.path.join(current, 'vision', 'models', filename))
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent

    for path in candidates:
        if os.path.isfile(path):
            return path

    raise FileNotFoundError(
        f"Model '{filename}' niet gevonden. Gezochte locaties:\n  "
        + "\n  ".join(candidates)
        + "\nZet de omgevingsvariabele TONK_REPO naar de repo-root."
    )


class PersonDetector(Node):
    def __init__(self):
        super().__init__('person_detector')

        # we gebruiken yolov8s omdat ons eigen model (best.pt) de brandende auto
        # ook als persoon herkende, yolov8s is getraind op echte foto's en maakt
        # dit onderscheid wel goed
        model_path = find_model_path('best1.pt')
        self.get_logger().info(f"Model geladen: {model_path}")
        self.model = YOLO(model_path)

        # luisteren naar de rgb camera
        self.sub = self.create_subscription(
            Image, '/camera/image_raw', self.callback, 10)

        # het geannoteerde beeld publiceren zodat we het in rviz kunnen zien
        self.pub = self.create_publisher(
            Image, '/person_detection/image', 10)

        self.get_logger().info("Person detector gestart (yolov8s, classes=[person])")

    # ros sensor_msgs/Image -> BGR numpy, ZONDER cv_bridge.
    # cv_bridge laadt de systeem-OpenCV, wat botst met de opencv-python van
    # ultralytics (ABI-conflict -> lege cv::Mat). Handmatig converteren omzeilt dat.
    @staticmethod
    def _imgmsg_to_bgr(msg):
        if not msg.data or msg.width == 0 or msg.height == 0:
            return None

        channels = max(1, len(msg.data) // (msg.height * msg.width))
        arr = np.frombuffer(msg.data, dtype=np.uint8).reshape(msg.height, msg.width, channels)

        enc = (msg.encoding or '').lower()
        if enc in ('rgb8', 'rgba8'):
            arr = arr[:, :, 2::-1]          # rgb(a) -> bgr
        elif enc in ('bgr8', 'bgra8'):
            arr = arr[:, :, :3]
        elif enc in ('mono8', ''):
            arr = np.repeat(arr[:, :, :1], 3, axis=2)
        else:
            arr = arr[:, :, :3]
        return np.ascontiguousarray(arr)

    def callback(self, msg):
        frame = self._imgmsg_to_bgr(msg)
        if frame is None:
            return  # leeg/corrupt frame overslaan

        # alleen class 0 (person) detecteren, confidence minimaal 0.5
        results = self.model(frame, conf=0.5, classes=[0])

        if results[0].boxes:
            for box in results[0].boxes:
                self.get_logger().info(f"Persoon conf={float(box.conf):.2f}")

        # resultaat met bounding boxes tekenen (BGR numpy) en publiceren
        annotated = np.ascontiguousarray(results[0].plot())

        out_msg = Image()
        out_msg.header = msg.header
        out_msg.height = int(annotated.shape[0])
        out_msg.width = int(annotated.shape[1])
        out_msg.encoding = 'bgr8'
        out_msg.is_bigendian = 0
        out_msg.step = int(annotated.shape[1] * 3)
        out_msg.data = annotated.tobytes()
        self.pub.publish(out_msg)


def main(args=None):
    rclpy.init(args=args)
    node = PersonDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
