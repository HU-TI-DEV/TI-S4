#!/usr/bin/env python3
import gz.transport as gz
from gz.msgs import image_pb2
import numpy as np
import cv2
import time

TOPIC = "/camera/image"

node = gz.Node()

def image_cb(msg: image_pb2.Image):
    # Use numeric values for pixel format
    if msg.pixel_format_type == 3:   # RGB_INT8
        channels = 3
    elif msg.pixel_format_type == 4: # RGBA_INT8
        channels = 4
    elif msg.pixel_format_type == 1: # L_INT8
        channels = 1
    else:
        print("Unsupported pixel format:", msg.pixel_format_type)
        return

    img = np.frombuffer(msg.data, dtype=np.uint8)
    img = img.reshape((msg.height, msg.width, channels))

    if channels == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif channels == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

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
