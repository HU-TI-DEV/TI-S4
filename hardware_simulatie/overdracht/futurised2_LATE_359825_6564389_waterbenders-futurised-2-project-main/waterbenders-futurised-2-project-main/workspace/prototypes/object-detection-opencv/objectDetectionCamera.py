#!/usr/bin/env python3
"""
Object detection for Gazebo camera images.

This version does NOT map colors to object types.
Instead it does:

    camera image -> generic colored-object mask -> contours
    contour -> dominant color estimation
    contour -> shape estimation

So the detected object label is based on the image itself, not on a hardcoded
mapping like "green = cylinder".

Run example:
    python3 objectDetectionCamera_auto.py

Optional:
    python3 objectDetectionCamera_auto.py --topic /front/image --min-area 500
    python3 objectDetectionCamera_auto.py --show-mask
"""

import argparse
import time
from typing import Dict, List, Tuple, Any

import cv2
import gz.transport as gz
import numpy as np
from gz.msgs import image_pb2


# OpenCV HSV uses:
# H: 0-179
# S: 0-255
# V: 0-255
#
# These are only reference hues for naming the detected color.
# They are NOT object-type mappings.
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
        self.last_mask = None

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
    def hsv_to_bgr_tuple(h: int, s: int = 255, v: int = 255) -> Tuple[int, int, int]:
        pixel = np.uint8([[[h, s, v]]])
        bgr = cv2.cvtColor(pixel, cv2.COLOR_HSV2BGR)[0, 0]
        return int(bgr[0]), int(bgr[1]), int(bgr[2])

    def segment_colored_objects(self, hsv: np.ndarray) -> np.ndarray:
        """
        Segment all clearly colored objects at once.

        This avoids separate hardcoded masks for red, green, blue, etc.
        It works best in simulation when the objects are saturated colors
        and the walls/floor/background are less saturated.
        """
        lower = np.array([0, self.min_saturation, self.min_value], dtype=np.uint8)
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

        Returns:
            color_name: human-readable color name
            dominant_hsv: [h, s, v]
            draw_bgr: color used for drawing the bounding box
        """
        contour_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        cv2.drawContours(contour_mask, [contour], -1, 255, -1)

        pixels = hsv[contour_mask == 255]
        if len(pixels) == 0:
            return "unknown", [0, 0, 0], (0, 255, 0)

        # Ignore weak/noisy pixels inside the contour.
        pixels = pixels[
            (pixels[:, 1] >= self.min_saturation) &
            (pixels[:, 2] >= self.min_value)
        ]

        if len(pixels) == 0:
            return "unknown", [0, 0, 0], (0, 255, 0)

        hues = pixels[:, 0].astype(np.int32)

        # Dominant hue by histogram.
        hue_hist = np.bincount(hues, minlength=180)
        dominant_hue = int(np.argmax(hue_hist))

        # Median S/V is more stable than mean when there are shadows/highlights.
        median_s = int(np.median(pixels[:, 1]))
        median_v = int(np.median(pixels[:, 2]))

        color_name = self.closest_color_name(dominant_hue)
        draw_color = self.hsv_to_bgr_tuple(dominant_hue, median_s, median_v)

        return color_name, [dominant_hue, median_s, median_v], draw_color

    @staticmethod
    def classify_shape_from_contour(contour: np.ndarray) -> str:
        """
        Estimate the 2D silhouette shape from an OpenCV contour.

        Important limitation:
        A single RGB camera sees a 2D projection. A sphere and a front-facing
        cylinder can both look circular. A box and a cube can both look
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

        # Triangle-like object.
        if vertices == 3:
            return "triangle"

        # Square / rectangle silhouette.
        if vertices == 4:
            if 0.80 <= aspect_ratio <= 1.20:
                return "cube"
            return "box"

        # Round silhouette.
        # In a normal camera image this may be a sphere or a cylinder facing the camera.
        if circularity > 0.75 and 0.75 <= aspect_ratio <= 1.25:
            return "sphere"

        # Tall rounded rectangle silhouette.
        if vertices >= 5 and 0.30 <= aspect_ratio <= 0.90 and extent > 0.55:
            return "cylinder"

        # A mostly filled convex silhouette that was not approximated as 4 vertices.
        if solidity > 0.85 and extent > 0.60:
            if 0.80 <= aspect_ratio <= 1.20:
                return "cube/round-object"
            return "box/cylinder"

        return "unknown"

    def detect_objects(self, img_bgr: np.ndarray) -> List[Dict[str, Any]]:
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        mask = self.segment_colored_objects(hsv)

        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        detections = []

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
                "color": color_name,
                "dominant_hsv": dominant_hsv,
                "object_type": object_type,
                "bbox": [int(x), int(y), int(w), int(h)],
                "center_px": [int(cx), int(cy)],
                "area_px": float(area),
                "draw_bgr": draw_bgr,
            })

        # Largest objects first.
        detections.sort(key=lambda det: det["area_px"], reverse=True)
        return detections

    @staticmethod
    def draw_detections(img_bgr: np.ndarray, detections: List[Dict[str, Any]]) -> None:
        for det in detections:
            x, y, w, h = det["bbox"]
            color_name = det["color"]
            object_type = det["object_type"]
            draw_color = det.get("draw_bgr", (0, 255, 0))

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


class GazeboCameraObjectDetectionApp:
    def __init__(
        self,
        topic: str,
        min_area: int,
        print_every_seconds: float,
        min_saturation: int,
        min_value: int,
        show_mask: bool,
    ):
        self.topic = topic
        self.print_every_seconds = print_every_seconds
        self.last_print_time = 0.0

        self.node = gz.Node()
        self.detector = ObjectDetector(
            min_area=min_area,
            min_saturation=min_saturation,
            min_value=min_value,
            show_mask=show_mask,
        )

    def image_cb(self, msg: image_pb2.Image) -> None:
        img = gz_image_to_bgr(msg)
        if img is None:
            return

        detections = self.detector.detect_objects(img)
        self.detector.draw_detections(img, detections)

        now = time.time()
        if detections and now - self.last_print_time > self.print_every_seconds:
            for det in detections:
                # draw_bgr is useful internally, but it clutters terminal logs.
                printable_det = dict(det)
                printable_det.pop("draw_bgr", None)
                print(printable_det)
            self.last_print_time = now

        cv2.imshow("Gazebo Object Recognition", img)

        if self.detector.show_mask and self.detector.last_mask is not None:
            cv2.imshow("Object Mask", self.detector.last_mask)

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
        description="Detect object color and 2D shape from a Gazebo RGB camera topic.",
    )

    parser.add_argument(
        "--topic",
        default="/front/image",
        help="Gazebo camera image topic. Default: /front/image",
    )
    parser.add_argument(
        "--min-area",
        type=int,
        default=500,
        help="Minimum contour area in pixels. Default: 500",
    )
    parser.add_argument(
        "--print-every",
        type=float,
        default=0.5,
        help="Minimum seconds between terminal detection logs. Default: 0.5",
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
        "--show-mask",
        action="store_true",
        help="Show the binary mask used for object segmentation.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    app = GazeboCameraObjectDetectionApp(
        topic=args.topic,
        min_area=args.min_area,
        print_every_seconds=args.print_every,
        min_saturation=args.min_saturation,
        min_value=args.min_value,
        show_mask=args.show_mask,
    )
    app.run()


if __name__ == "__main__":
    main()
