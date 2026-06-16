"""
detect.py

Subscribes to the Gazebo RGB camera topic, runs YOLO inference on each frame,
and prints detections to the console.
"""

import time
import numpy as np
import cv2
from ultralytics import YOLO

import gz.transport as transport
import gz.msgs.image_pb2 as image_pb2
from gz.msgs import annotated_axis_aligned_2d_box_pb2 as box_pb2

# ── CONFIG ────────────────────────────────────────────────────────────────────
MODEL_PATH         = 'best.pt'
CAMERA_TOPIC       = '/camera/image'
DETECTIONS_TOPIC   = '/detections'
CONF_THRESH        = 0.8
IOU_THRESH         = 0.1
ACTOR_CLASS_ID     = 4
# ─────────────────────────────────────────────────────────────────────────────

CLASS_NAMES = {
    0: 'rails',
    1: 'arm',
    2: 'curing_machine',
    3: 'printer',
    4: 'person'
}

latest_frame = None

print(f"Loading YOLO model...")
model = YOLO(MODEL_PATH)
model.to('cpu') # delete this if you want to run the model on your gpu
print("Model loaded.\n")

last_inference = 0
INFERENCE_INTERVAL = 0.1  # 10 fps max

node      = transport.Node()
publisher = node.advertise(DETECTIONS_TOPIC, box_pb2.AnnotatedAxisAligned2DBox)

def make_box_msg(x1, y1, x2, y2):
    person_box = box_pb2.AnnotatedAxisAligned2DBox()
    person_box.label = ACTOR_CLASS_ID
    person_box.box.min_corner.x = x1
    person_box.box.min_corner.y = y1
    person_box.box.max_corner.x = x2
    person_box.box.max_corner.y = y2
    return person_box

def on_image(msg):
    global latest_frame
    latest_frame = msg

def main():
    global last_inference

    print(f"Subscribing to: {CAMERA_TOPIC}")
    success = node.subscribe(
        image_pb2.Image,
        CAMERA_TOPIC,
        on_image
    )

    if not success:
        print(f"[ERROR] Failed to subscribe to {CAMERA_TOPIC}")
        print("Check that Gazebo is running and the topic exists.")
        print("List available topics with: gz topic -l")
        return

    print("Subscribed. Waiting for frames...")
    print("Press Ctrl+C to stop.\n")

    while True:
        if latest_frame is None:
            time.sleep(0.01)
            continue

        now = time.time()
        if now - last_inference < INFERENCE_INTERVAL:
            continue
        last_inference = now

        # print(f"Frame received: {msg.width}x{msg.height}")

        # Decode raw RGB bytes from Gazebo
        raw = np.frombuffer(latest_frame.data, dtype=np.uint8)

        try:
            frame = raw.reshape((latest_frame.height, latest_frame.width, 3))
        except ValueError:
            print(f"[WARN] Could not reshape image: got {len(raw)} bytes, "
                  f"expected {latest_frame.height * latest_frame.width * 3}")
            continue

        # RGB → BGR for YOLO
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        import os
        if not os.path.exists('frames/debug_frame.jpg'):
            cv2.imwrite('frames/debug_frame.jpg', frame_bgr)
            # print("Debug frame saved to debug_frame.jpg")

        # Run inference
        results = model(frame_bgr, conf=CONF_THRESH, iou=IOU_THRESH, verbose=False)
        annotated = results[0].plot()
        cv2.imwrite('frames/annotated_frame.jpg', annotated)
        print("Saved annotated_frame.jpg")

        # print(results[0])
        # print(results[0].boxes)

        detections = results[0].boxes

        if detections is None or len(detections) == 0:
            print(f"[{time.strftime('%H:%M:%S')}] No detections")
            continue

        # print(f"[{time.strftime('%H:%M:%S')}] {len(detections)} detection(s):")
        for box in detections:
            cls_id = int(box.cls[0])
            conf   = float(box.conf[0])
            name   = CLASS_NAMES.get(cls_id, f'class_{cls_id}')

            # Fix any remaining flipped coordinates
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            x1, x2 = int(min(x1, x2)), int(max(x1, x2))
            y1, y2 = int(min(y1, y2)), int(max(y1, y2))
            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2

            if cls_id == ACTOR_CLASS_ID:
                publisher.publish(make_box_msg(x1, y1, x2, y2))
                print(f"published actor box to {DETECTIONS_TOPIC}")
                break  # only publish the highest confidence person

            print(f"  {name:16s} | conf: {conf:.2f} | "
                  f"box: [{x1}, {y1}, {x2}, {y2}] | "
                  f"center: ({cx}, {cy})")
        
        print()

if __name__ == '__main__':
    main()