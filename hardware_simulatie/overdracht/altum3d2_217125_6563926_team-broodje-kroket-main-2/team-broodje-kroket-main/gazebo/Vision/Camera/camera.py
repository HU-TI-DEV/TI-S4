#!/usr/bin/env python3
## @file camera.py
#  @brief Gazebo camera subscriber with real-time station outline and opening detection.
#
#  Subscribes to Gazebo image topics via gz.transport, runs an OpenCV-based
#  detection pipeline on every frame, and displays the annotated results in
#  OpenCV windows.
#
#  Detected objects:
#  - **Station**: large rectangular contours (station outlines), drawn in cyan-yellow.
#  - **Station opening**: highest-density cluster of hex-angle Hough lines, drawn in orange.
import gz.transport as gz
from gz.msgs import image_pb2
import numpy as np
import cv2
import time

TOPIC = "/arm/wrist_camera/image"

node = gz.Node()

def detect_and_annotate(img, detect_station_outline=True, detect_station_opening=True):
    ## @brief Run the full detection pipeline on a BGR image.
    #
    #  @param img                     Input BGR image as a numpy ndarray (modified in-place).
    #  @param detect_station_outline  Detect station outer rectangles (default True).
    #  @param detect_station_opening  Detect station openings via hex Hough lines (default True).
    #  @return     Tuple (annotated_img, edges, lines_img).
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    edges = cv2.Canny(gray, 50, 150)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    all_contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    min_area = 0.001 * (img.shape[0] * img.shape[1])

    rectangles = []  # 4-sided contours (allow 3-5 vertices)
    min_area_confident = 0.01 * (img.shape[0] * img.shape[1])  # at least 1% of image

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.05 * perimeter, True)
        num_vertices = len(approx)
        if 3 <= num_vertices <= 5:
            rectangles.append((area, cnt, approx))

    # --- Station outline detection: all large rectangles ---
    if detect_station_outline and rectangles:
        for area, cnt, approx in rectangles:
            hull = cv2.convexHull(cnt)
            hull_area = cv2.contourArea(hull)
            solidity = area / hull_area if hull_area > 0 else 0
            x, y, w, h = cv2.boundingRect(hull)
            aspect = w / h if h > 0 else 0
            confident = (
                solidity >= 0.75
                and area >= min_area_confident
                and 0.15 <= aspect <= 6.0
            )
            if confident:
                cv2.drawContours(img, [hull], -1, (200, 200, 0), 3)
                cv2.rectangle(img, (x, y), (x + w, y + h), (200, 200, 0), 3)
                cv2.putText(img, "Station", (x, max(20, y - 5)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 0), 2, cv2.LINE_AA)

    # --- Station opening detection: hex-angle Hough line density ---
    lines_img = img.copy()
    if detect_station_opening:
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=40, minLineLength=30, maxLineGap=10)
        if lines is not None:
            h_img, w_img = img.shape[:2]
            cell = 40

            hex_roi = None

            def hex_angle_score(x1, y1, x2, y2):
                angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1))) % 180
                best = min(abs(angle - a) % 180 for a in (0, 60, 120))
                return max(0.0, 1.0 - best / 30.0)

            grid_h = h_img // cell + 1
            grid_w = w_img // cell + 1
            density = np.zeros((grid_h, grid_w), dtype=np.float32)

            for line in lines:
                x1, y1, x2, y2 = line[0]
                score = hex_angle_score(x1, y1, x2, y2)
                cv2.line(lines_img, (x1, y1), (x2, y2), (255, 0, 255), 1)
                weight = 0.5 + 9.5 * score
                if hex_roi is not None:
                    rx1, ry1, rx2, ry2 = hex_roi
                    in_roi = (rx1 <= x1 <= rx2 and ry1 <= y1 <= ry2) or \
                             (rx1 <= x2 <= rx2 and ry1 <= y2 <= ry2)
                    if not in_roi:
                        weight *= 0.1
                length = int(np.hypot(x2 - x1, y2 - y1))
                num_samples = max(length // (cell // 2), 2)
                for i in range(num_samples + 1):
                    t = i / num_samples
                    px = int(x1 + t * (x2 - x1))
                    py = int(y1 + t * (y2 - y1))
                    gx = min(px // cell, grid_w - 1)
                    gy = min(py // cell, grid_h - 1)
                    density[gy, gx] += weight

            density_f = cv2.GaussianBlur(density, (5, 5), 0)
            _, max_val, _, max_loc = cv2.minMaxLoc(density_f)
            if max_val >= 5:
                CLUSTER_RADIUS = 3
                gx_peak, gy_peak = max_loc
                mask = np.zeros_like(density_f)
                peak_val = density_f[gy_peak, gx_peak]
                threshold_val = peak_val * 0.4
                for gy in range(max(0, gy_peak - CLUSTER_RADIUS), min(grid_h, gy_peak + CLUSTER_RADIUS + 1)):
                    for gx in range(max(0, gx_peak - CLUSTER_RADIUS), min(grid_w, gx_peak + CLUSTER_RADIUS + 1)):
                        if density_f[gy, gx] >= threshold_val:
                            mask[gy, gx] = 1

                cluster_points = []
                hex_line_count = 0
                total_line_count = 0
                for line in lines:
                    x1, y1, x2, y2 = line[0]
                    in_cluster = False
                    for px, py in [(x1, y1), (x2, y2)]:
                        gx = min(px // cell, grid_w - 1)
                        gy = min(py // cell, grid_h - 1)
                        if mask[gy, gx] > 0:
                            cluster_points.append([px, py])
                            in_cluster = True
                    if in_cluster:
                        total_line_count += 1
                        if hex_angle_score(x1, y1, x2, y2) >= 0.5:
                            hex_line_count += 1

                hex_ratio = hex_line_count / total_line_count if total_line_count > 0 else 0
                if len(cluster_points) >= 4 and hex_ratio >= 0.5:
                    pts = np.array(cluster_points, dtype=np.int32)
                    hull = cv2.convexHull(pts)
                    for target in (img, lines_img):
                        cv2.drawContours(target, [hull], -1, (0, 165, 255), 3)
                        x, y, w, h = cv2.boundingRect(hull)
                        cv2.rectangle(target, (x, y), (x + w, y + h), (0, 165, 255), 3)
                        cv2.putText(target, "Station opening", (x, max(20, y - 5)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2, cv2.LINE_AA)

    return img, edges, lines_img


def image_cb(msg: image_pb2.Image):
    ## @brief Callback for the wrist camera topic.
    #
    #  Decodes the raw Gazebo image message, converts it to BGR, runs
    #  detect_and_annotate(), and displays the result in an OpenCV window.
    #
    #  @param msg  gz.msgs.Image protobuf message received from the topic.
    if msg.pixel_format_type == 3:
        channels = 3
    elif msg.pixel_format_type == 4:
        channels = 4
    elif msg.pixel_format_type == 1:
        channels = 1
    else:
        print("Unsupported pixel format:", msg.pixel_format_type)
        return

    img = np.frombuffer(msg.data, dtype=np.uint8).reshape((msg.height, msg.width, channels))
    if channels == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif channels == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
    elif channels == 1:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    img, edges, lines_img = detect_and_annotate(img)

    cv2.imshow("Gazebo Camera", img)
    cv2.imshow("Gazebo Camera (Edges)", edges)
    cv2.waitKey(1)

# Subscribe to wrist camera (with detection)
ok = node.subscribe(image_pb2.Image, TOPIC, image_cb)

if not ok:
    raise RuntimeError(f"Failed to subscribe to topic: {TOPIC}")

# Subscribe to the 5 fixed world cameras (raw feed)
FIXED_CAMERAS = {
    "Wrist Left":  "/arm/wrist_camera_left/image",
    "Wrist Back":  "/arm/wrist_camera_back/image",
    "Wrist Right": "/arm/wrist_camera_right/image",
}

def make_camera_cb(window_name):
    ## @brief Factory that creates a camera callback bound to a named OpenCV window.
    #
    #  The returned callback decodes incoming Gazebo image messages, applies
    #  detect_and_annotate(), and shows the annotated frame in the window
    #  identified by @p window_name.
    #
    #  @param window_name  Title of the OpenCV display window.
    #  @return             Callable `cb(msg: image_pb2.Image)` suitable for
    #                      node.subscribe().
    def cb(msg: image_pb2.Image):
        if msg.pixel_format_type == 3:
            channels = 3
        elif msg.pixel_format_type == 4:
            channels = 4
        elif msg.pixel_format_type == 1:
            channels = 1
        else:
            return
        img = np.frombuffer(msg.data, dtype=np.uint8).reshape((msg.height, msg.width, channels))
        if channels == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif channels == 4:
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)
        elif channels == 1:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        img, edges, lines_img = detect_and_annotate(img)
        cv2.imshow(window_name, img)
        cv2.imshow(window_name + " (Edges)", edges)
        cv2.waitKey(1)
    return cb

for name, topic in FIXED_CAMERAS.items():
    if not node.subscribe(image_pb2.Image, topic, make_camera_cb(f"Camera: {name}")):
        print(f"Warning: failed to subscribe to {topic}")

print(f"Subscribed to {TOPIC}. Press Ctrl+C to exit.")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")

cv2.destroyAllWindows()
