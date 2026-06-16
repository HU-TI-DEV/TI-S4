# ==============================================================================
#  ProximityDetection.py
# ==============================================================================

import struct
import time
import gz.transport as gz
from gz.msgs import image_pb2
from gz.msgs import annotated_axis_aligned_2d_box_pb2 as box_pb2
from gz.msgs import boolean_pb2
import math
import numpy as np
import cv2

# ────── CONFIG ───────────────────────────────────────────────────────────────────────────────────────────────────

DETECTIONS_TOPIC        = "/detections"
DEPTH_CAMERA_TOPIC      = "/depth_camera/image"
ARM_COMMUNICATION_TOPIC = "/arm/pause"

IMAGE_WIDTH             = 800
IMAGE_HEIGHT            = 600
HORIZONTAL_FOV          = 1.5  

CAM_POSE                = (0, 7, 3.5, 0, 0.5999, -1.5708)
ARM_POSE                = np.array([0.0, 0.0, 0.0])

PROXIMITY_THRESH        = 4   # max proximity to the arm without it stopping. in Meters
MAX_BOX_AGE             = 0.5 # discards boxes older than this constant

# ────── CONSTS ───────────────────────────────────────────────────────────────────────────────────────────────────

focal_length_x          = (IMAGE_WIDTH / 2) / math.tan(HORIZONTAL_FOV / 2)
focal_length_y          = focal_length_x
principal_point_x       = IMAGE_WIDTH  / 2
principal_point_y       = IMAGE_HEIGHT / 2

# ────── GLOBALS ──────────────────────────────────────────────────────────────────────────────────────────────────

node                    = gz.Node()
publisher               = node.advertise(ARM_COMMUNICATION_TOPIC, boolean_pb2.Boolean)

person_box              = None
person_box_timestamp    = 0

stopped                 = False

# ────── CALCULATION FUNCTIONS ────────────────────────────────────────────────────────────────────────────────────

# turns a pixel from the depth camera into a 3d point relative to the camera
def pixel_to_3d(pixel_x, pixel_y, depth, focal_length_x, focal_length_y, principal_point_x, principal_point_y): 
    if depth == 0 or math.isinf(depth): # discards the pixel if it isnt from an object. A sky pixel for example
        return None
    
    gazebo_x = depth
    gazebo_y = -(pixel_x - principal_point_x) * depth / focal_length_x
    gazebo_z = -(pixel_y - principal_point_y) * depth / focal_length_y

    return (gazebo_x, gazebo_y, gazebo_z)

# turns a point relative to the camera into a 3d point that is accurate in the simulation
def camera_to_world(camera_x, camera_y, camera_z, cam_pose):
    translate_x, translate_y, translate_z, roll, pitch, yaw = cam_pose

    rotation_x = np.array([[1, 0,            0            ],
                           [0, np.cos(roll), -np.sin(roll)],
                           [0, np.sin(roll), np.cos(roll)]])

    rotation_y = np.array([[np.cos(pitch),  0, np.sin(pitch)],
                           [0,              1, 0            ],
                           [-np.sin(pitch), 0, np.cos(pitch)]])

    rotation_z = np.array([[np.cos(yaw), -np.sin(yaw), 0],
                           [np.sin(yaw), np.cos(yaw) , 0],
                           [0,           0           , 1]])

    rotation_matrix = rotation_z @ rotation_y @ rotation_x
    point_in_camera_space = np.array([camera_x, camera_y, camera_z])
    translation = np.array([translate_x, translate_y, translate_z])
    point_in_world_space = rotation_matrix @ point_in_camera_space + translation
    return point_in_world_space

# combines both prior functions to calculate the 3d point of a specific pixel in an image from the depth cam
def get_world_position(pixel_x, pixel_y, pixels, width):
    depth = pixels[pixel_y * width + pixel_x]
    point_in_camera_space = pixel_to_3d(pixel_x, pixel_y, depth,
                                        focal_length_x, focal_length_y,
                                        principal_point_x, principal_point_y)
    if point_in_camera_space is None:
        return None
    return camera_to_world(*point_in_camera_space, CAM_POSE)

# given a bounding box and a frame from the depth cam this function will find the actor in that box
def get_actor_world_position(box, pixels, width):
    x1, y1, x2, y2 = box

    # sample a horizontal line at 60% of the box's height (to get a pixel from the torso)
    scan_y = y1 + int((y2 - y1) * 0.4)

    closest_world_position = None
    closest_distance = math.inf

    for scan_x in range(x1, x2): # tries to find the closest point to the camera in that line of pixels
        world_position = get_world_position(scan_x, scan_y, pixels, width)

        if world_position is None:
            continue

        # keep track of the closest point
        distance = math.sqrt((world_position[0] - CAM_POSE[0])**2 +
                             (world_position[1] - CAM_POSE[1])**2 +
                             (world_position[2] - CAM_POSE[2])**2)
        
        if distance < closest_distance:
            closest_distance = distance
            closest_world_position = world_position

    return closest_world_position

# ────── CALLBACKS ──────────────────────────────────────────────────────────────────────────────────────────────

def detections_callback(msg: box_pb2.AnnotatedAxisAligned2DBox):
    global person_box, person_box_timestamp
    b = msg.box
    person_box = (
        int(min(b.min_corner.x, b.max_corner.x)),
        int(min(b.min_corner.y, b.max_corner.y)),
        int(max(b.min_corner.x, b.max_corner.x)),
        int(max(b.min_corner.y, b.max_corner.y)),
    )
    person_box_timestamp = time.time()

def depth_callback(msg: image_pb2.Image):
    global person_box, person_box_timestamp
    global stopped

    pixels = struct.unpack(f'{IMAGE_WIDTH * IMAGE_HEIGHT}f', msg.data)

    # build depth array for visualization
    depth_array = np.array(pixels).reshape((IMAGE_HEIGHT, IMAGE_WIDTH))
    depth_array = np.clip(depth_array, 0, 10)
    depth_visual = (depth_array / 10 * 255).astype(np.uint8)
    debug = cv2.cvtColor(depth_visual, cv2.COLOR_GRAY2BGR)

    # draw bounding box and scan line if we have a detection
    if person_box is not None:
        x1, y1, x2, y2 = person_box
        scan_y       = y1 + int((y2 - y1) * 0.4)
        scan_x_start = x1 + int((x2 - x1) * 0.2)
        scan_x_end   = x1 + int((x2 - x1) * 0.8)
        cv2.rectangle(debug, (x1, y1), (x2, y2), (0, 255, 0), 1)
        cv2.line(debug, (scan_x_start, scan_y), (scan_x_end, scan_y), (0, 0, 255), 2)

    # show a live feed in a window
    cv2.imwrite('frames/depth_debug.jpg', debug)
    cv2.imshow('Depth Debug', debug)
    cv2.waitKey(1)

    # discards old frames so it doesnt try to find the actor in a box where the actor is no longer in 
    box_age = time.time() - person_box_timestamp
    if person_box is None or box_age > MAX_BOX_AGE:
        print("No fresh person detection")
        return

    # gets the actors position and detects wether they dont come too close to the arm
    actor_position = get_actor_world_position(person_box, pixels, IMAGE_WIDTH)
    if actor_position is not None:
        prox = np.linalg.norm(actor_position - ARM_POSE)
        print(f"Actor world position: "
              f"x={actor_position[0]:.3f} "
              f"y={actor_position[1]:.3f} "
              f"z={actor_position[2]:.3f} | distance to arm: {prox:.3f}m")
        if prox < PROXIMITY_THRESH and not stopped:
            stopped = True
            msg = boolean_pb2.Boolean()
            msg.data = stopped
            publisher.publish(msg)
            print(stopped)
        elif prox > PROXIMITY_THRESH and stopped:
            stopped = False
            msg = boolean_pb2.Boolean()
            msg.data = stopped
            publisher.publish(msg)
            print(stopped)
    else:
        print("Could not determine actor position")

# ────── SUBSCRIBING ────────────────────────────────────────────────────────────────────────────────

node.subscribe(box_pb2.AnnotatedAxisAligned2DBox, DETECTIONS_TOPIC, detections_callback)
node.subscribe(image_pb2.Image, DEPTH_CAMERA_TOPIC, depth_callback)

# ────── MAIN LOOP ────────────────────────────────────────────────────────────────────────────────

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("shutting down")