import os
import sys

# =====================================================================
# 1. SILENCE THE COLLIDING C++ LIBRARIES (Mute Protobuf Warnings)
# =====================================================================
try:
    original_stderr = os.dup(sys.stderr.fileno())
    devnull = os.open(os.devnull, os.O_WRONLY)
    os.dup2(devnull, sys.stderr.fileno())
except Exception:
    original_stderr = None

# --- ALL NOISY IMPORTS GO HERE ---
import time
from pathlib import Path
from threading import Lock
import argparse
from os import getenv

import numpy as np
import cv2
import torch

# --- GAZEBO IMPORTS ---
from gz.msgs10.image_pb2 import Image
from gz.transport13 import Node

# Setup paths using your environment variables
# Uses trained YOLO model to detect valve
DEFAULT_MODEL_PATH = Path(__file__).resolve().parents[3] / "runs" / "train" / "exp3" / "weights" / "best.pt" 
MODEL_PATH = Path(getenv("YOLO_WEIGHTS_PATH", str(DEFAULT_MODEL_PATH)))

# Fail safe if file is missing
if not MODEL_PATH.exists():
    if original_stderr is not None:
        os.dup2(original_stderr, sys.stderr.fileno())  # Unmute terminal to show error
    raise FileNotFoundError(
        f"Trained model not found: {MODEL_PATH}. Set YOLO_WEIGHTS_PATH or place best.pt at the default path."
    )

print("Loading Custom Legacy YOLOv5 model via PyTorch Hub...")
model = torch.hub.load("ultralytics/yolov5", "custom", path=str(MODEL_PATH))

# =====================================================================
# 2. RESTORE STANDARD ERROR (Unmute Terminal for Normal Python Output)
# =====================================================================
if original_stderr is not None:
    os.dup2(original_stderr, sys.stderr.fileno())
    os.close(devnull)
    os.close(original_stderr)

# =====================================================================
# 3. APPLICATION CODE
# =====================================================================
latest_frame_lock = Lock()
latest_msg = None


def image_callback(msg: Image):
    """
    Lightning-fast callback. 
    Only grabs the raw message structure and immediately returns so Gazebo doesn't lag.
    """
    global latest_msg
    with latest_frame_lock:
        latest_msg = msg


def main():
    global latest_msg
    
    node = Node()
    topic_name = "/camera/image"  # Remember to swap out if using a deep hierarchical name!
    
    print(f"Subscribing to {topic_name}...")
    if node.subscribe(Image, topic_name, image_callback):
        print("Successfully subscribed! Waiting for images...")
    else:
        print(f"Failed to subscribe to: {topic_name}")
        return

    try:
        # Register both UI windows
        cv2.namedWindow("Direct Gazebo -> Legacy YOLOv5", cv2.WINDOW_NORMAL)
        cv2.namedWindow("Gazebo Camera Live Feed", cv2.WINDOW_NORMAL)

        while True:
            # 1. Pull the most recent frame out of our mailbox
            msg_to_process = None
            with latest_frame_lock:
                if latest_msg is not None:
                    msg_to_process = latest_msg
                    latest_msg = None  # Flush mailbox to drop intermediate backlogged frames

            # 2. Process frame down here in the main thread to guarantee real-time playback
            if msg_to_process is not None:
                raw_data = np.frombuffer(msg_to_process.data, dtype=np.uint8)
                img_rgb = raw_data.reshape((msg_to_process.height, msg_to_process.width, 3))
                
                # Render clean raw feed
                raw_frame_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                
                # Render separate inference feed
                results = model(img_rgb)
                results.render()
                annotated_frame_bgr = cv2.cvtColor(results.ims[0], cv2.COLOR_RGB2BGR)

                # Send matrices to windows simultaneously
                cv2.imshow("Gazebo Camera Live Feed", raw_frame_bgr)
                cv2.imshow("Direct Gazebo -> Legacy YOLOv5", annotated_frame_bgr)

            # Keep window refreshing alive and look for escape triggers
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