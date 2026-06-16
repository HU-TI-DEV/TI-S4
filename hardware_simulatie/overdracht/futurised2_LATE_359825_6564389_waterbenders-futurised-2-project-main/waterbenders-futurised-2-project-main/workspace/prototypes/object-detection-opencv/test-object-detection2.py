#!/usr/bin/env python3
import time
import cv2
import gz.transport as gz
import numpy as np
from gz.msgs import image_pb2

TOPIC = "/front/image"
MIN_AREA = 500
frame_count = 0

COLOR_HUES = {
    "red": 0,
    "orange": 15,
    "yellow": 30,
    "green": 60,
    "cyan": 90,
    "blue": 115,
    "purple": 145,
    "pink": 165,
}

def hue_distance(h1, h2):
    diff = abs(h1 - h2)
    return min(diff, 180 - diff)

"""
Converts raw HUE value to colorname
"""
def closest_color_name(hue):
    best_name = "unknown"
    best_dist = 999

    for name, ref_hue in COLOR_HUES.items():
        dist = hue_distance(hue, ref_hue)
        if dist < best_dist:
            best_dist = dist
            best_name = name
    return best_name

"""
Converts HSV color to OpenCV BGR color
"""
def hsv_to_bgr(h, s=255, v=255):
    pixel = np.uint8([[[h, s, v]]])
    bgr = cv2.cvtColor(pixel, cv2.COLOR_HSV2BGR)[0, 0]
    return int(bgr[0]), int(bgr[1]), int(bgr[2])

"""
Calculate shape of detected object using contours
"""
def classify_shape(contour):
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
    
    # confirm objects based on vertices first (corners)
    # Triangle
    if vertices == 3:
        return "triangle"
    # Rectangle / square
    if vertices == 4:
        if 0.80 <= aspect_ratio <= 1.20:
            return "cube"
        return "box"
    # Circle-like
    if circularity > 0.75 and 0.75 <= aspect_ratio <= 1.25:
        return "sphere"
    # Cylinder-like
    if vertices >= 5 and 0.30 <= aspect_ratio <= 0.90 and extent > 0.55:
        return "cylinder"

    # Fallback convex object
    if solidity > 0.85 and extent > 0.60:
        if 0.80 <= aspect_ratio <= 1.20:
            return "cube/round-object"
        return "box/cylinder"
    return "unknown"

"""
Convert Gz image to OpenCV Image
"""
def gz_image_to_bgr(msg):
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

node = gz.Node()
last_print_time = 0

"""

"""
def image_cb(msg):
    global frame_count, last_print_time

    frame_count += 1
    if frame_count % 3 != 0:
        return

    frame = gz_image_to_bgr(msg)
    if frame is None:
        return

    frame = cv2.resize(frame, (640, 360))

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # =====================================================
    # 1. SEGMENT (same idea as old segment_colored_objects)
    # =====================================================
    lower = np.array([0, 60, 50])
    upper = np.array([179, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)

    kernel = np.ones((3, 3), np.uint8)

    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # =====================================================
    # 2. FIND CONTOURS
    # =====================================================
    contours, _ = cv2.findContours(
        mask,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    for contour in contours:

        area = cv2.contourArea(contour)
        if area < MIN_AREA:
            continue

        x, y, w, h = cv2.boundingRect(contour)

        cx = x + w // 2
        cy = y + h // 2

        # =====================================================
        # 3. CONTEXT MASK (same as old estimate_dominant_color)
        # =====================================================
        contour_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)

        cv2.drawContours(contour_mask, [contour], -1, 255, -1)

        pixels = hsv[contour_mask == 255]

        if len(pixels) == 0:
            continue

        # IMPORTANT FIX: filter noise like OLD script
        pixels = pixels[
            (pixels[:, 1] >= 60) &
            (pixels[:, 2] >= 50)
        ]

        if len(pixels) == 0:
            continue

        # =====================================================
        # 4. DOMINANT COLOR (same as old)
        # =====================================================
        hues = pixels[:, 0].astype(np.int32)

        hue_hist = np.bincount(hues, minlength=180)

        dominant_hue = int(np.argmax(hue_hist))

        median_s = int(np.median(pixels[:, 1]))
        median_v = int(np.median(pixels[:, 2]))

        color_name = closest_color_name(dominant_hue)

        draw_color = hsv_to_bgr(
            dominant_hue,
            median_s,
            median_v
        )

        # =====================================================
        # 5. SHAPE CLASSIFICATION (unchanged but now stable input)
        # =====================================================
        shape = classify_shape(contour)

        label = f"{color_name} {shape}"

        # =====================================================
        # 6. DRAW (same as draw_detections)
        # =====================================================
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            draw_color,
            2
        )

        cv2.circle(
            frame,
            (cx, cy),
            4,
            draw_color,
            -1
        )

        cv2.putText(
            frame,
            label,
            (x, max(20, y - 10)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            draw_color,
            2
        )

        # =====================================================
        # 7. PRINT
        # =====================================================
        now = time.time()

        if now - last_print_time > 2.0:
            print({
                "label": label,
                "bbox": [x, y, w, h],
                "area": area
            })
            last_print_time = now

    cv2.imshow("Detection", frame)
    cv2.imshow("Mask", mask)
    cv2.waitKey(1)

def main():
    node = gz.Node()
    node.subscribe(
        image_pb2.Image,
        TOPIC,
        image_cb
    )
    print(f"Subscribed to {TOPIC}")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()