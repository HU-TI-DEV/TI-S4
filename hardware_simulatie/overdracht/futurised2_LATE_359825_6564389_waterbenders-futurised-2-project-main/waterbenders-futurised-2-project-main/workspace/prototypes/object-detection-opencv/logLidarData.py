#!/usr/bin/env python3


# locatie laserscan proto file for data
# /usr/share/gz/gz-msgs/protos/gz/msgs/laserscan.proto


import math
import time
import json
from pathlib import Path

import gz.transport as gz
from gz.msgs import laserscan_pb2


TOPIC = "/lidar"

node = gz.Node()

# Logging state
logging_enabled = False
logged_scans = []
max_scans_to_log = 5
output_json_file = "object_lidar_scans.json"


def start_logging_5_scans(filename="object_lidar_scans.json"):
    """
    Call this function yourself when you decide an object has been detected.

    It will log the next 5 LaserScan messages to a JSON file.
    """
    global logging_enabled
    global logged_scans
    global output_json_file

    output_json_file = filename
    logged_scans = []
    logging_enabled = True

    print(f"Started logging next {max_scans_to_log} lidar scans to {output_json_file}")


def get_stamp_seconds(msg):
    try:
        sec = msg.header.stamp.sec
        nsec = msg.header.stamp.nsec
        return float(sec) + float(nsec) * 1e-9
    except Exception:
        return time.time()


def is_valid_range(r, msg):
    if math.isnan(r) or math.isinf(r):
        return False

    if r < msg.range_min:
        return False

    if r > msg.range_max:
        return False

    return True


def convert_scan_to_dict(msg):
    """
    Converts one LaserScan message to a dictionary that can be saved as JSON.
    """
    scan_time = get_stamp_seconds(msg)

    scan_data = {
        "scan_time_sec": scan_time,
        "frame": msg.frame,
        "range_min_m": float(msg.range_min),
        "range_max_m": float(msg.range_max),
        "angle_min_rad": float(msg.angle_min),
        "angle_max_rad": float(msg.angle_max),
        "angle_step_rad": float(msg.angle_step),
        "points": []
    }

    for i, r in enumerate(msg.ranges):
        r = float(r)

        if not is_valid_range(r, msg):
            continue

        angle = float(msg.angle_min) + i * float(msg.angle_step)

        x = r * math.cos(angle)
        y = r * math.sin(angle)
        z = 0.0

        scan_data["points"].append({
            "beam_index": i,
            "angle_rad": angle,
            "range_m": r,
            "position_lidar_frame_m": {
                "x": x,
                "y": y,
                "z": z
            }
        })

    return scan_data


def save_logged_scans_to_json():
    output_data = {
        "topic": TOPIC,
        "number_of_scans": len(logged_scans),
        "scans": logged_scans
    }

    Path(output_json_file).write_text(
        json.dumps(output_data, indent=4),
        encoding="utf-8"
    )

    print(f"Saved {len(logged_scans)} lidar scans to {output_json_file}")


def log_scan_if_enabled(msg):
    """
    This function is called for every incoming LaserScan.
    It only logs data when start_logging_5_scans() has been called.
    """
    global logging_enabled

    if not logging_enabled:
        return

    scan_data = convert_scan_to_dict(msg)
    logged_scans.append(scan_data)

    print(f"Logged scan {len(logged_scans)} / {max_scans_to_log}")

    if len(logged_scans) >= max_scans_to_log:
        save_logged_scans_to_json()
        logging_enabled = False


def laserScan_cb(msg: laserscan_pb2.LaserScan):
    # Always call this in the callback.
    # It only logs when logging_enabled is True.
    log_scan_if_enabled(msg)

    # Example:
    # If you decide here that an object has been detected,
    # call start_logging_5_scans().
    #
    # if object_detected:
    #     start_logging_5_scans("detected_object_scans.json")


if node.subscribe(laserscan_pb2.LaserScan, TOPIC, laserScan_cb):
    print(f"Subscribed to {TOPIC}")
else:
    print(f"Failed to subscribe to {TOPIC}")
    exit(1)


print("Press Enter to manually start logging 5 lidar scans.")
print("Press Ctrl+C to exit.")

try:
    while True:
        user_input = input()

        # Manual trigger
        start_logging_5_scans("manual_object_detection.json")

except KeyboardInterrupt:
    print("\nExiting...")