#!/usr/bin/env python3
import gz.transport as gz
from gz.msgs import image_pb2
import numpy as np
import cv2
import time

# Thermal camera topic
TOPIC = "/thermal_camera"

# Temperature range from your SDF plugin
MIN_TEMP = 100.0
MAX_TEMP = 700.0

# Create a transport node
node = gz.Node()

def thermal_callback(msg: image_pb2.Image):
    # Check the pixel format
    if msg.pixel_format_type == 2:  # L_INT16
        dtype = np.uint16
    else:
        print("Unsupported pixel format:", msg.pixel_format_type)
        return

    # Convert raw data to numpy array
    img = np.frombuffer(msg.data, dtype=dtype).reshape((msg.height, msg.width))

    # Map 16-bit grayscale to temperature
    temp_image = MIN_TEMP + (img / 65535.0) * (MAX_TEMP - MIN_TEMP)

    # Print center pixel temperature
    cy, cx = msg.height // 2, msg.width // 2
    center_temp = temp_image[cy, cx]
    print(f"Center pixel temperature: {center_temp:.2f} K")

    # Scale to 0–255 for visualization
    display_img = ((temp_image - MIN_TEMP) / (MAX_TEMP - MIN_TEMP) * 255).astype(np.uint8)
    cv2.imshow("Thermal Camera", display_img)
    cv2.waitKey(1)

# Subscribe to the thermal camera topic
node.subscribe(image_pb2.Image, TOPIC, thermal_callback)
print(f"Subscribed to {TOPIC}. Press Ctrl+C to exit.")

# Spin
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
    cv2.destroyAllWindows()