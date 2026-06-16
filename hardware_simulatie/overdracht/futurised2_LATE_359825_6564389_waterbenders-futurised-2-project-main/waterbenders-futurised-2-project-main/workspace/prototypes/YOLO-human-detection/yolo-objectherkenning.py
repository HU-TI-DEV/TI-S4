#!/usr/bin/env python3

import argparse
import time

import cv2
import gz.transport as gz
import numpy as np
from gz.msgs import image_pb2
from ultralytics import YOLO


def gz_image_to_bgr(msg: image_pb2.Image) -> np.ndarray | None:
    """
    Convert a Gazebo Image message to an OpenCV BGR image.
    """
    if msg.pixel_format_type == 3:      # RGB_INT8
        channels = 3
    elif msg.pixel_format_type == 4:    # RGBA_INT8
        channels = 4
    elif msg.pixel_format_type == 1:    # L_INT8 / grayscale
        channels = 1
    else:
        print("Unsupported pixel format:", msg.pixel_format_type)
        return None

    img = np.frombuffer(msg.data, dtype=np.uint8)

    try:
        img = img.reshape((msg.height, msg.width, channels))
    except ValueError as exc:
        print(f"Could not reshape image data: {exc}")
        return None

    if channels == 3:
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    if channels == 4:
        return cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


class GazeboYoloPeopleApp:
    def __init__(self, topic: str, model_path: str, conf: float, only_person: bool):
        self.topic = topic
        self.conf = conf
        self.only_person = only_person

        self.node = gz.Node()
        self.model = YOLO(model_path)

        print(f"Loaded YOLO model: {model_path}")

    def image_cb(self, msg: image_pb2.Image) -> None:
        img_bgr = gz_image_to_bgr(msg)
        if img_bgr is None:
            return

        # YOLO works well with RGB input. We draw on the original BGR image.
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        # For pretrained COCO YOLO models, class 0 = person.
        classes = [0] if self.only_person else None

        results = self.model.predict(
            source=img_rgb,
            imgsz=640,
            conf=self.conf,
            classes=classes,
            verbose=False,
        )

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.model.names[class_id]

                label = f"{class_name} {confidence:.2f}"

                cv2.rectangle(img_bgr, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    img_bgr,
                    label,
                    (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                print({
                    "class": class_name,
                    "confidence": round(confidence, 3),
                    "bbox": [int(x1), int(y1), int(x2), int(y2)],
                    "center_px": [int(center_x), int(center_y)],
                })

        cv2.imshow("Gazebo YOLO People Detection", img_bgr)
        cv2.waitKey(1)

    def run(self) -> None:
        self.node.subscribe(image_pb2.Image, self.topic, self.image_cb)
        print(f"Subscribed to {self.topic}. Press Ctrl+C to exit.")

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Exiting...")
        finally:
            cv2.destroyAllWindows()


def parse_args():
    parser = argparse.ArgumentParser(
        description="YOLO person/victim detection from a Gazebo camera topic."
    )

    parser.add_argument(
        "--topic",
        default="/front/image",
        help="Gazebo camera image topic. Default: /front/image",
    )
    parser.add_argument(
        "--model",
        default="yolo11n.pt",
        help="YOLO model path. Example: yolo11n.pt or runs/detect/train/weights/best.pt",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.35,
        help="Confidence threshold. Default: 0.35",
    )
    parser.add_argument(
        "--all-classes",
        action="store_true",
        help="Detect all classes instead of only COCO person class.",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    app = GazeboYoloPeopleApp(
        topic=args.topic,
        model_path=args.model,
        conf=args.conf,
        only_person=not args.all_classes,
    )
    app.run()


if __name__ == "__main__":
    main()