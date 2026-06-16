# ==============================================================================
#  DatasetGenerator.py
# ==============================================================================

import gz.transport as gz
from gz.msgs import image_pb2
from gz.msgs import annotated_axis_aligned_2d_box_v_pb2
from CamPositions import cam_positions
from CamPositions import make_request
import numpy as np
import cv2
import time
import os

# ────── CONFIG ────────────────────────────────────────────────────────────────────────────────────────────────────

RGB_TOPIC         = "/camera/image"
BB_TOPIC          = "/bounding_box_camera/boxes"

IS_SAVING         = True
SAVE_INTERVAL     = 1/35
SAVE_DIR          = "dataset"

CAM_TURN_INTERVAL = 2400
DATASET_SIZE      = 10000

# ────── GLOBALS ───────────────────────────────────────────────────────────────────────────────────────────────────

elapsed_frames    = 0
saved_frames      = 0
current_cam_pos   = 0
img               = None
boxes             = []

is_reading        = False
mutex             = False

node              = gz.Node()

label_to_class    = {
                    0:  0,  # rails
                    10: 1,  # arm
                    20: 2,  # curing_machine
                    30: 3,  # printer
                    40: 4,  # person
                    }

# ────── CALLBACKS ──────────────────────────────────────────────────────────────────────────────────────────────────

def rgb_cam_callback(msg: image_pb2.Image):
    global img, mutex
    mutex = True
    img = np.frombuffer(msg.data, dtype=np.uint8)
    img = img.reshape((msg.height, msg.width, 3))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    mutex = False

def boundingbox_cam_callback(msg: annotated_axis_aligned_2d_box_v_pb2.AnnotatedAxisAligned2DBox_V):
    global boxes
    boxes = []
    for annotated_box in msg.annotated_box:
        b = annotated_box.box
        boxes.append((
            int(min(b.min_corner.x, b.max_corner.x)),
            int(min(b.min_corner.y, b.max_corner.y)),
            int(max(b.min_corner.x, b.max_corner.x)),
            int(max(b.min_corner.y, b.max_corner.y)),
            annotated_box.label
        ))

# ────── SUBSCRIBING ─────────────────────────────────────────────────────────────────────────────────────────────────

node.subscribe(image_pb2.Image, RGB_TOPIC, rgb_cam_callback)
node.subscribe(annotated_axis_aligned_2d_box_v_pb2.AnnotatedAxisAligned2DBox_V, BB_TOPIC, boundingbox_cam_callback)

# ────── MAKING DIRECTORY ────────────────────────────────────────────────────────────────────────────────────────────

os.makedirs(SAVE_DIR, exist_ok=True)

# ────── MAIN LOOP ───────────────────────────────────────────────────────────────────────────────────────────────────

try:
    while True:
        if is_reading: # counts elapsed frames
            elapsed_frames += 1

        if img is not None and mutex is False: # if the simulation has started and the mutex is available

            if is_reading is False: # kickstarts the reading process when the simulation starts
                is_reading = True
                last_save_time = time.time()

            display = img.copy() # makes a copy of the image to display to the user NOT to save to the dataset
            for (x1, y1, x2, y2, label) in boxes:
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2) # draws the bounding box on the display

            now = time.time()
            if IS_SAVING and (now - last_save_time) >= SAVE_INTERVAL:        # only saves once every x frames so the dataset doesnt get too many 
                cv2.imwrite(f"{SAVE_DIR}/frame_{saved_frames:05d}.jpg", img) # identical frames
                with open(f"{SAVE_DIR}/frame_{saved_frames:05d}.txt", "w") as f:
                    for (x1, y1, x2, y2, label) in boxes: # converts bounding box to yolo format: center x, center y, width, height
                        cx = ((x1 + x2) / 2) / img.shape[1]
                        cy = ((y1 + y2) / 2) / img.shape[0]
                        w  = (x2 - x1) / img.shape[1]
                        h  = (y2 - y1) / img.shape[0]
                        if w <= 0 or h <= 0: # when the actor is off screen you can get a bounding box that is 0 pixels wide which leads to 
                            continue         # errors so we just skip those frames
                        class_id = label_to_class.get(label, -1)
                        if class_id == -1:
                            continue
                        f.write(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}\n") # writes the data to a txt file
                saved_frames += 1
                last_save_time = now
                print(f"{saved_frames} frames saved")

            cv2.imshow("Camera", display) # displays the image with bounding boxes to the user
            cv2.waitKey(1)
            img = None # resets image

        if elapsed_frames >= CAM_TURN_INTERVAL: # turns the camera every x frames to get a more diverse dataset
            current_cam_pos += 1
            request = make_request(cam_positions[current_cam_pos % 8], node)
            elapsed_frames = 0

        if saved_frames >= DATASET_SIZE: # stops the loop when dataset is complete
            print("all done!")
            break

        time.sleep(0.0167)

except KeyboardInterrupt:
    cv2.destroyAllWindows()