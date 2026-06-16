#!/usr/bin/env python3
"""
Hybrid Gazebo camera detection.

This script does both:

1. YOLO person detection
   - Uses a pretrained YOLO model.
   - Detects only COCO class 0, which is "person".

2. OpenCV colored-object detection
   - Detects clearly colored Gazebo objects.
   - Estimates dominant color.
   - Estimates simple 2D shape from the contour.

Recommended use:
    python3 cv2-yolo-detection.py

    or 

    vpy cv2-yolo-detection.py

Optional:
    python3/vpy cv2-yolo-detection.py --topic /front/image
    python3/vpy cv2-yolo-detection.py --model yolo11n.pt
    python3/vpy cv2-yolo-detection.py --show-mask
    python3/vpy cv2-yolo-detection.py --no-mask-people-for-objects
"""

import argparse
import time
from typing import Any, Dict, List, Tuple

import cv2
import gz.transport as gz
import numpy as np
from gz.msgs import image_pb2
from ultralytics import YOLO


# OpenCV HSV uses:
# H: 0-179
# S: 0-255
# V: 0-255
COLOR_HUES: Dict[str, int] = {
    "red": 0,
    "orange": 15,
    "yellow": 30,
    "green": 60,
    "cyan": 90,
    "blue": 115,
    "purple": 145,
    "pink": 165,
}


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


def clamp_box_xyxy(
    box: List[int],
    image_width: int,
    image_height: int,
    padding: int = 0,
) -> List[int]:
    """
    Clamp an xyxy bounding box to the image boundaries.
    """
    x1, y1, x2, y2 = box

    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(image_width - 1, x2 + padding)
    y2 = min(image_height - 1, y2 + padding)

    return [int(x1), int(y1), int(x2), int(y2)]


class YoloPersonDetector:
    def __init__(
        self,
        model_path: str = "yolo11n.pt",
        conf: float = 0.35,
        imgsz: int = 640,
    ):
        self.model_path = model_path
        self.conf = conf
        self.imgsz = imgsz

        self.model = YOLO(model_path)
        print(f"Loaded YOLO model: {model_path}")

    def detect_people(self, img_bgr: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect people with YOLO.

        For pretrained COCO YOLO models:
            class 0 = person
        """
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

        results = self.model.predict(
            source=img_rgb,
            imgsz=self.imgsz,
            conf=self.conf,
            classes=[0],
            verbose=False,
        )

        detections: List[Dict[str, Any]] = []

        img_h, img_w = img_bgr.shape[:2]

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])

                if isinstance(self.model.names, dict):
                    class_name = self.model.names.get(class_id, str(class_id))
                else:
                    class_name = self.model.names[class_id]

                x1, y1, x2, y2 = clamp_box_xyxy(
                    [x1, y1, x2, y2],
                    image_width=img_w,
                    image_height=img_h,
                )

                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                detections.append({
                    "source": "yolo",
                    "class": class_name,
                    "confidence": round(confidence, 3),
                    "bbox_xyxy": [int(x1), int(y1), int(x2), int(y2)],
                    "bbox": [int(x1), int(y1), int(x2 - x1), int(y2 - y1)],
                    "center_px": [int(center_x), int(center_y)],
                })

        return detections

    @staticmethod
    def draw_people(img_bgr: np.ndarray, detections: List[Dict[str, Any]]) -> None:
        for det in detections:
            x1, y1, x2, y2 = det["bbox_xyxy"]
            label = f"person {det['confidence']:.2f}"

            # YOLO/person detections are drawn in green.
            draw_color = (0, 255, 0)

            cv2.rectangle(img_bgr, (x1, y1), (x2, y2), draw_color, 2)
            cv2.circle(img_bgr, tuple(det["center_px"]), 4, draw_color, -1)

            cv2.putText(
                img_bgr,
                label,
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                draw_color,
                2,
                cv2.LINE_AA,
            )


class ObjectDetector:
    def __init__(
        self,
        min_area: int = 500,
        min_saturation: int = 60,
        min_value: int = 50,
        show_mask: bool = False,
    ):
        self.min_area = min_area
        self.min_saturation = min_saturation
        self.min_value = min_value
        self.show_mask = show_mask
        self.last_mask: np.ndarray | None = None

    @staticmethod
    def hue_distance(h1: int, h2: int) -> int:
        """
        OpenCV hue wraps around at red.
        Example: hue 179 is very close to hue 0.
        """
        diff = abs(int(h1) - int(h2))
        return min(diff, 180 - diff)

    def closest_color_name(self, hue: int) -> str:
        best_name = "unknown"
        best_dist = 999

        for color_name, ref_hue in COLOR_HUES.items():
            dist = self.hue_distance(hue, ref_hue)
            if dist < best_dist:
                best_dist = dist
                best_name = color_name

        return best_name

    @staticmethod
    def hsv_to_bgr_tuple(
        h: int,
        s: int = 255,
        v: int = 255,
    ) -> Tuple[int, int, int]:
        pixel = np.uint8([[[h, s, v]]])
        bgr = cv2.cvtColor(pixel, cv2.COLOR_HSV2BGR)[0, 0]
        return int(bgr[0]), int(bgr[1]), int(bgr[2])

    def mask_out_boxes(
        self,
        img_bgr: np.ndarray,
        boxes_xyxy: List[List[int]],
        padding: int = 8,
    ) -> np.ndarray:
        """
        Black out person boxes before colored-object segmentation.

        This prevents colored clothing / textured person models from being
        detected again as generic colored objects.
        """
        masked = img_bgr.copy()
        img_h, img_w = masked.shape[:2]

        for box in boxes_xyxy:
            x1, y1, x2, y2 = clamp_box_xyxy(
                box,
                image_width=img_w,
                image_height=img_h,
                padding=padding,
            )
            masked[y1:y2, x1:x2] = (0, 0, 0)

        return masked

    def segment_colored_objects(self, hsv: np.ndarray) -> np.ndarray:
        """
        Segment all clearly colored objects at once.
        """
        lower = np.array(
            [0, self.min_saturation, self.min_value],
            dtype=np.uint8,
        )
        upper = np.array([179, 255, 255], dtype=np.uint8)

        mask = cv2.inRange(hsv, lower, upper)

        # Remove small noise and fill small holes.
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        self.last_mask = mask
        return mask

    def estimate_dominant_color(
        self,
        hsv: np.ndarray,
        contour: np.ndarray,
    ) -> Tuple[str, List[int], Tuple[int, int, int]]:
        """
        Estimate the dominant object color inside a contour.
        """
        contour_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        cv2.drawContours(contour_mask, [contour], -1, 255, -1)

        pixels = hsv[contour_mask == 255]
        if len(pixels) == 0:
            return "unknown", [0, 0, 0], (255, 255, 255)

        pixels = pixels[
            (pixels[:, 1] >= self.min_saturation) &
            (pixels[:, 2] >= self.min_value)
        ]

        if len(pixels) == 0:
            return "unknown", [0, 0, 0], (255, 255, 255)

        hues = pixels[:, 0].astype(np.int32)

        hue_hist = np.bincount(hues, minlength=180)
        dominant_hue = int(np.argmax(hue_hist))

        median_s = int(np.median(pixels[:, 1]))
        median_v = int(np.median(pixels[:, 2]))

        color_name = self.closest_color_name(dominant_hue)
        draw_color = self.hsv_to_bgr_tuple(dominant_hue, median_s, median_v)

        return color_name, [dominant_hue, median_s, median_v], draw_color

    @staticmethod
    def classify_shape_from_contour(contour: np.ndarray) -> str:
        """
        Estimate the 2D silhouette shape from an OpenCV contour.

        Limitation:
        A single RGB camera sees a 2D projection. A sphere and a front-facing
        cylinder can both look circular. A cube and box can both look
        rectangular depending on viewpoint.
        """
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)

        if perimeter == 0:
            return "unknown"

        approx = cv2.approxPolyDP(contour, 0.035 * perimeter, True)
        vertices = len(approx)

        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h) if h > 0 else 0.0

        circularity = 4.0 * np.pi * area / (perimeter * perimeter)

        rect_area = w * h
        extent = area / float(rect_area) if rect_area > 0 else 0.0

        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / float(hull_area) if hull_area > 0 else 0.0

        if vertices == 3:
            return "triangle"

        if vertices == 4:
            if 0.80 <= aspect_ratio <= 1.20:
                return "cube"
            return "box"

        if circularity > 0.75 and 0.75 <= aspect_ratio <= 1.25:
            return "sphere"

        if vertices >= 5 and 0.30 <= aspect_ratio <= 0.90 and extent > 0.55:
            return "cylinder"

        if solidity > 0.85 and extent > 0.60:
            if 0.80 <= aspect_ratio <= 1.20:
                return "cube/round-object"
            return "box/cylinder"

        return "unknown"

    def detect_objects(
        self,
        img_bgr: np.ndarray,
        ignore_boxes_xyxy: List[List[int]] | None = None,
        ignore_box_padding: int = 8,
    ) -> List[Dict[str, Any]]:
        """
        Detect colored objects.

        If ignore_boxes_xyxy is given, those boxes are blacked out first.
        This is useful for ignoring YOLO-detected people.
        """
        if ignore_boxes_xyxy:
            work_img = self.mask_out_boxes(
                img_bgr,
                ignore_boxes_xyxy,
                padding=ignore_box_padding,
            )
        else:
            work_img = img_bgr

        hsv = cv2.cvtColor(work_img, cv2.COLOR_BGR2HSV)
        mask = self.segment_colored_objects(hsv)

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        detections: List[Dict[str, Any]] = []

        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)
            cx = x + w // 2
            cy = y + h // 2

            color_name, dominant_hsv, draw_bgr = self.estimate_dominant_color(
                hsv,
                contour,
            )
            object_type = self.classify_shape_from_contour(contour)

            detections.append({
                "source": "opencv",
                "class": "object",
                "color": color_name,
                "dominant_hsv": dominant_hsv,
                "object_type": object_type,
                "bbox": [int(x), int(y), int(w), int(h)],
                "bbox_xyxy": [int(x), int(y), int(x + w), int(y + h)],
                "center_px": [int(cx), int(cy)],
                "area_px": float(area),
                "draw_bgr": draw_bgr,
            })

        detections.sort(key=lambda det: det["area_px"], reverse=True)
        return detections

    @staticmethod
    def draw_objects(
        img_bgr: np.ndarray,
        detections: List[Dict[str, Any]],
    ) -> None:
        for det in detections:
            x, y, w, h = det["bbox"]
            color_name = det["color"]
            object_type = det["object_type"]
            draw_color = det.get("draw_bgr", (255, 255, 255))

            label = f"{color_name} {object_type}"

            cv2.rectangle(img_bgr, (x, y), (x + w, y + h), draw_color, 2)
            cv2.circle(img_bgr, tuple(det["center_px"]), 4, draw_color, -1)

            cv2.putText(
                img_bgr,
                label,
                (x, max(20, y - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                draw_color,
                2,
                cv2.LINE_AA,
            )


class GazeboHybridDetectionApp:
    def __init__(
        self,
        topic: str,
        model_path: str,
        yolo_conf: float,
        yolo_imgsz: int,
        min_area: int,
        min_saturation: int,
        min_value: int,
        print_every_seconds: float,
        show_mask: bool,
        mask_people_for_objects: bool,
        person_mask_padding: int,
    ):
        self.topic = topic
        self.print_every_seconds = print_every_seconds
        self.last_print_time = 0.0
        self.mask_people_for_objects = mask_people_for_objects
        self.person_mask_padding = person_mask_padding

        self.node = gz.Node()

        self.person_detector = YoloPersonDetector(
            model_path=model_path,
            conf=yolo_conf,
            imgsz=yolo_imgsz,
        )

        self.object_detector = ObjectDetector(
            min_area=min_area,
            min_saturation=min_saturation,
            min_value=min_value,
            show_mask=show_mask,
        )

    def image_cb(self, msg: image_pb2.Image) -> None:
        img_bgr = gz_image_to_bgr(msg)
        if img_bgr is None:
            return

        people = self.person_detector.detect_people(img_bgr)

        if self.mask_people_for_objects:
            ignore_boxes = [person["bbox_xyxy"] for person in people]
        else:
            ignore_boxes = []

        objects = self.object_detector.detect_objects(
            img_bgr,
            ignore_boxes_xyxy=ignore_boxes,
            ignore_box_padding=self.person_mask_padding,
        )

        # Draw on original image.
        self.object_detector.draw_objects(img_bgr, objects)
        self.person_detector.draw_people(img_bgr, people)

        now = time.time()
        if now - self.last_print_time > self.print_every_seconds:
            for person in people:
                print(person)

            for obj in objects:
                printable_obj = dict(obj)
                printable_obj.pop("draw_bgr", None)
                print(printable_obj)

            if people or objects:
                print("-" * 60)

            self.last_print_time = now

        cv2.imshow("Gazebo Hybrid Detection: YOLO People + OpenCV Objects", img_bgr)

        if self.object_detector.show_mask and self.object_detector.last_mask is not None:
            cv2.imshow("OpenCV Object Mask", self.object_detector.last_mask)

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Hybrid Gazebo camera detection: YOLO people + OpenCV colored objects.",
    )

    parser.add_argument(
        "--topic",
        default="/front/image",
        help="Gazebo camera image topic. Default: /front/image",
    )

    parser.add_argument(
        "--model",
        default="yolo11n.pt",
        help="YOLO model path. Default: yolo11n.pt",
    )

    parser.add_argument(
        "--yolo-conf",
        type=float,
        default=0.35,
        help="YOLO person confidence threshold. Default: 0.35",
    )

    parser.add_argument(
        "--yolo-imgsz",
        type=int,
        default=640,
        help="YOLO inference image size. Default: 640",
    )

    parser.add_argument(
        "--min-area",
        type=int,
        default=500,
        help="Minimum OpenCV contour area in pixels. Default: 500",
    )

    parser.add_argument(
        "--min-saturation",
        type=int,
        default=60,
        help="Minimum HSV saturation for colored-object segmentation. Default: 60",
    )

    parser.add_argument(
        "--min-value",
        type=int,
        default=50,
        help="Minimum HSV value/brightness for colored-object segmentation. Default: 50",
    )

    parser.add_argument(
        "--print-every",
        type=float,
        default=0.5,
        help="Minimum seconds between terminal detection logs. Default: 0.5",
    )

    parser.add_argument(
        "--show-mask",
        action="store_true",
        help="Show the OpenCV binary mask used for object segmentation.",
    )

    parser.add_argument(
        "--no-mask-people-for-objects",
        action="store_true",
        help="Do not black out YOLO person boxes before OpenCV object detection.",
    )

    parser.add_argument(
        "--person-mask-padding",
        type=int,
        default=8,
        help="Padding around YOLO person boxes when masking them for object detection. Default: 8",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    app = GazeboHybridDetectionApp(
        topic=args.topic,
        model_path=args.model,
        yolo_conf=args.yolo_conf,
        yolo_imgsz=args.yolo_imgsz,
        min_area=args.min_area,
        min_saturation=args.min_saturation,
        min_value=args.min_value,
        print_every_seconds=args.print_every,
        show_mask=args.show_mask,
        mask_people_for_objects=not args.no_mask_people_for_objects,
        person_mask_padding=args.person_mask_padding,
    )

    app.run()


if __name__ == "__main__":
    main()