import time
from pathlib import Path
from threading import Lock

import numpy as np
import cv2
import torch

# --- GAZEBO IMPORTS ---
from gz.msgs10.image_pb2 import Image
from gz.transport13 import Node

print("Loading Custom Legacy YOLOv5 model via PyTorch Hub...")

MODEL_PATH = Path(__file__).resolve().parents[1] / "runs" / "yolov5s.pt"
model = torch.hub.load("ultralytics/yolov5", "custom", path=str(MODEL_PATH))

latest_frame_lock = Lock()
latest_frame = None


def image_callback(msg: Image):
    """Convert a Gazebo image message to an annotated OpenCV frame.

    The callback does not call `imshow` directly. That keeps image
    handling fast and avoids UI flicker or blocking in the transport thread.
    """
    global latest_frame

    try:
        # Gazebo sends raw RGB bytes. Convert them into a frame for YOLO.
        raw_data = np.frombuffer(msg.data, dtype=np.uint8)
        img = raw_data.reshape((msg.height, msg.width, 3))

        # Run detection and draw the boxes on the frame.
        results = model(img)

        results.render()
        annotated_frame_rgb = results.ims[0]
        annotated_frame_bgr = cv2.cvtColor(annotated_frame_rgb, cv2.COLOR_RGB2BGR)

        # Keep only the newest frame so the UI shows live data instead of a queue.
        with latest_frame_lock:
            latest_frame = annotated_frame_bgr
        
    except Exception as e:
        print(f"Error processing image: {e}")


def main():
    """Subscribe to the camera topic and show the latest annotated frame."""
    node = Node()
    topic_name = "/camera/image"
    
    print(f"Subscribing to {topic_name}...")
    if node.subscribe(Image, topic_name, image_callback):
        print("Successfully subscribed! Waiting for images...")
    else:
        print(f"Failed to subscribe to: {topic_name}")
        return

    try:
        cv2.namedWindow("Direct Gazebo -> Legacy YOLOv5", cv2.WINDOW_NORMAL)

        while True:
            # Read the most recent frame; if none exists yet, keep the window alive.
            with latest_frame_lock:
                frame_to_show = None if latest_frame is None else latest_frame.copy()

            if frame_to_show is not None:
                cv2.imshow("Direct Gazebo -> Legacy YOLOv5", frame_to_show)

            # Allow the window to refresh and let the user quit with q or Esc.
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")):
                print("Exit requested, shutting down...")
                break

            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()