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
"""

import time
from typing import Dict, List, Tuple, Any

import cv2
import gz.transport as gz
import numpy as np
from gz.msgs import image_pb2


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
        Computes the distance between two HSV hue values,
        taking into account that hue wraps around (0 is close to 179 in OpenCV). 
        -> This ensures correct color comparison across the red boundary.
        """
        diff = abs(int(h1) - int(h2))
        return min(diff, 180 - diff)

    def closest_color_name(self, hue: int) -> str:
        """
        Finds the closest named color (red, green, blue, etc.) by comparing the input hue against predefined reference hues.
        Uses the smallest hue distance to determine the best match.
        """
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
        """
        Converts a single HSV color value into a BGR color tuple.
        Used for drawing bounding boxes in the correct visual color corresponding to the detected object hue.
        """
        pixel = np.uint8([[[h, s, v]]])
        bgr = cv2.cvtColor(pixel, cv2.COLOR_HSV2BGR)[0, 0]
        return int(bgr[0]), int(bgr[1]), int(bgr[2])

    def segment_colored_objects(self, hsv: np.ndarray) -> np.ndarray:
        """
        Creates a binary mask that isolates "colored" regions in the image.
        It filters out low-saturation and low-brightness pixels (background noise), then applies morphological operations to remove small noise and fill gaps.
        The result is a clean mask of potential objects.
        """
        lower = np.array([0, self.min_saturation, self.min_value], dtype=np.uint8)
        upper = np.array([179, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        self.last_mask = mask
        return mask

    def estimate_dominant_color(self, hsv: np.ndarray, contour: np.ndarray,) -> Tuple[str, List[int], Tuple[int, int, int]]:
        """
        Estimates the dominant color inside a detected contour.
        Returns both the color name and a BGR color for drawing.
        """
        # create mask for pixels inside contour
        contour_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        cv2.drawContours(contour_mask, [contour], -1, 255, -1)
        
        # Extracts HSV pixel values from that region
        pixels = hsv[contour_mask == 255]                                       # only pixels inside object
        if len(pixels) == 0:
            return "unknown", [0, 0, 0], (0, 255, 0)
        pixels = pixels[
            (pixels[:, 1] >= self.min_saturation) &
            (pixels[:, 2] >= self.min_value)
        ]
        if len(pixels) == 0:
            return "unknown", [0, 0, 0], (0, 255, 0)

        # Builds a hue histogram to find the most common hue
        hues = pixels[:, 0].astype(np.int32)
        hue_hist = np.bincount(hues, minlength=180)
        dominant_hue = int(np.argmax(hue_hist))                                 # find most 'common' color in object
        
        # median saturation and brightness for stability
        median_s = int(np.median(pixels[:, 1]))
        median_v = int(np.median(pixels[:, 2]))
        
        # Converts dominant hue into color name
        color_name = self.closest_color_name(dominant_hue)
        draw_color = self.hsv_to_bgr_tuple(dominant_hue, median_s, median_v)
        return color_name, [dominant_hue, median_s, median_v], draw_color

    @staticmethod
    def classify_shape_from_contour(contour: np.ndarray) -> str:
        """
        Classifies the 2D shape of an object using its contour geometry.
        Uses vertices, aspect-ratio, circularity, extent, solidity.
        ! Note: This is 2D vision, so depth-based ambiguity (sphere vs cylinder) can still occur depending on camera angle.
        """
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            return "unknown"
        
        approx = cv2.approxPolyDP(contour, 0.035 * perimeter, True)                 # approximite amount of corners
        vertices = len(approx)                                                      # amount of corners detected
        
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / float(h) if h > 0 else 0.0                               # detect difference square/rectangle
        
        circularity = 4.0 * np.pi * area / (perimeter * perimeter)                  # to detect spheres (perfect sphere = 1.0)
        
        rect_area = w * h               
        extent = area / float(rect_area) if rect_area > 0 else 0.0                  # how bounding the box is (perfect shape or irregular, like cilinders)
        
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = area / float(hull_area) if hull_area > 0 else 0.0                # robustness check ( solid shape = 1.0)
        
        # where object definition happens, in this order for most reliable to least reliable:
        # vertices -> circularity -> extent + solidity
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

    def detect_objects(self, img_bgr: np.ndarray) -> List[Dict[str, Any]]:
        """
        Main detection pipeline in single frame.
        Returns a list of detected objects with color, shape, and position data.
        """
        # Convert image to HSV color space
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        # create mask of colored regions
        mask = self.segment_colored_objects(hsv)
        
        # Extract contours from mask
        contours, _ = cv2.findContours(
            mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )
        detections = []
        for contour in contours:
            # Compute bounding box and center point
            area = cv2.contourArea(contour)
            if area < self.min_area:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            cx = x + w // 2
            cy = y + h // 2

            # Estimate dominant color
            color_name, dominant_hsv, draw_bgr = self.estimate_dominant_color(
                hsv,
                contour,
            )
            # Classify shape
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
        # Store data in dictionairy
        detections.sort(key=lambda det: det["area_px"], reverse=True)
        return detections

    @staticmethod
    def draw_detections(img_bgr: np.ndarray, detections: List[Dict[str, Any]]) -> None:
        """
        Draws detection results onto image, for each object:
        bounding box in object color, marks object center point, overlays text with object color + shape
        """
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
    Converts a Gazebo image message into an OpenCV BGR image.
    Handles different pixel formats (RGB, RGBA, grayscale).
    Reshapes raw byte data into an image array and converts color format so it is compatible with OpenCV processing.
    """
    if msg.pixel_format_type == 3:
        channels = 3
    elif msg.pixel_format_type == 4:
        channels = 4
    elif msg.pixel_format_type == 1:
        channels = 1
    else:
        return None

    img = np.frombuffer(msg.data, dtype=np.uint8)

    try:
        img = img.reshape((msg.height, msg.width, channels))
    except ValueError:
        return None

    if channels == 3:
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    if channels == 4:
        return cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

    return cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)


class GazeboCameraObjectDetectionApp:
    def __init__(self, topic: str = "/front/image"):
        self.topic = topic
        self.node = gz.Node()
        self.detector = ObjectDetector()
        self.last_print_time = 0.0

    def image_cb(self, msg: image_pb2.Image) -> None:
        """
        Callback function triggered for every incoming camera frame.
        """
        # Convert GZ image to OpenCV format
        img = gz_image_to_bgr(msg)
        if img is None:
            return
        
        # Run detection pipeline
        detections = self.detector.detect_objects(img)
        # Draw detections on frame
        self.detector.draw_detections(img, detections)

        # Print results at controlled rate (better fps and less spam)
        now = time.time()
        if detections and now - self.last_print_time > 0.5:
            for det in detections:
                printable = dict(det)
                printable.pop("draw_bgr", None)
                print(printable)
            self.last_print_time = now

        cv2.imshow("Gazebo Object Recognition", img)

        # Dislay processed image (and optionally mask)
        if self.detector.show_mask and self.detector.last_mask is not None:
            cv2.imshow("Object Mask", self.detector.last_mask)

        cv2.waitKey(1)

    def run(self) -> None:
        """
        Starts the Gazebo subscription and begins listening for images.
        Keeps the program alive in a loop until interrupted (Ctrl+C).
        Handles cleanup of OpenCV windows on exit.
        """
        self.node.subscribe(image_pb2.Image, self.topic, self.image_cb)
        print(f"Subscribed to {self.topic}")

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            cv2.destroyAllWindows()


def main() -> None:
    app = GazeboCameraObjectDetectionApp()
    app.run()


if __name__ == "__main__":
    main()