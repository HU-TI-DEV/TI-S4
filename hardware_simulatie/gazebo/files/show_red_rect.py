#!/usr/bin/env python3
import gz.transport as gz
from gz.msgs import image_pb2
import numpy as np
import cv2
import time

TOPIC = "/camera/image"

node = gz.Node()

def image_cb(msg: image_pb2.Image):
    # Determine number of channels
    if msg.pixel_format_type == 3:   # RGB_INT8
        channels = 3
    elif msg.pixel_format_type == 4: # RGBA_INT8
        channels = 4
    elif msg.pixel_format_type == 1: # L_INT8
        channels = 1
    else:
        print("Unsupported pixel format:", msg.pixel_format_type)
        return

    # Convert message to numpy array
    img = np.frombuffer(msg.data, dtype=np.uint8)
    img = img.reshape((msg.height, msg.width, channels))

    # Convert to BGR for OpenCV
    if channels == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif channels == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

    # ----- Red rectangle detection -----
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Red color range (two ranges because red wraps around 180 hue)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw green rectangle

    # Show image
    cv2.imshow("Gazebo Camera", img)
    cv2.waitKey(1)

# Subscribe
node.subscribe(image_pb2.Image, TOPIC, image_cb)

print(f"Subscribed to {TOPIC}. Press Ctrl+C to exit.")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")

cv2.destroyAllWindows()
