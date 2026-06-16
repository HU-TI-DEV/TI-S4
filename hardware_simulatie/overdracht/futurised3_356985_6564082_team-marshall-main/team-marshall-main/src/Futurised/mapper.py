#!/usr/bin/env python3
"""
Gazebo Standalone LiDAR Mapper
================================
Reads /lidar topic via `gz topic -e --json -t /lidar`
Builds an occupancy grid and displays it with OpenCV.

Requirements: python3, opencv-python, numpy
Usage:
    python3 mapper.py
    python3 mapper.py --save          # also saves map.png when you press 's'
    python3 mapper.py --odom /odom    # if you have an odom topic too
"""

import subprocess
import json
import math
import numpy as np
import cv2
import threading
import argparse
import sys
import time

# ─── MAP CONFIG ────────────────────────────────────────────────────────────────
MAP_SIZE_M   = 40.0      # total map width/height in meters
RESOLUTION   = 0.05      # meters per cell
MAP_CELLS    = int(MAP_SIZE_M / RESOLUTION)   # grid size in cells
ORIGIN       = MAP_CELLS // 2                 # robot starts at center

# Log-odds values for occupancy update
LO_OCC  =  2.0   # log-odds added when a cell is hit
LO_FREE = -0.1   # log-odds added when a ray passes through (very small!)
LO_MAX  =  10.0  # high ceiling so walls need many free rays to erase
LO_MIN  = -5.0

# ─── STATE ─────────────────────────────────────────────────────────────────────
log_odds   = np.zeros((MAP_CELLS, MAP_CELLS), dtype=np.float32)
robot_x    = 0.0   # meters, updated from /odom if available
robot_y    = 0.0
robot_yaw  = 0.0
lock       = threading.Lock()
last_scan_time = 0.0


def world_to_grid(wx, wy):
    """Convert world coords (meters) to grid cell indices."""
    gx = int(ORIGIN + wx / RESOLUTION)
    gy = int(ORIGIN - wy / RESOLUTION)   # Y flipped for image coords
    return gx, gy


def bresenham(x0, y0, x1, y1, max_cells):
    """Yield all cells on the line from (x0,y0) to (x1,y1), clipped to grid."""
    cells = []
    dx = abs(x1 - x0); dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        if 0 <= x0 < max_cells and 0 <= y0 < max_cells:
            cells.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy; x0 += sx
        if e2 < dx:
            err += dx; y0 += sy
        if len(cells) > 2000:   # safety cap
            break
    return cells


def update_map_from_scan(ranges, angle_min, angle_increment, lidar_x, lidar_y):
    """Ray-cast each beam into the occupancy grid."""
    global log_odds

    # Lidar is 1.45m ahead of model origin, corrected for 180deg yaw flip
    LIDAR_OFFSET = 1.45
    scan_x = robot_x + LIDAR_OFFSET * math.cos(robot_yaw)
    scan_y = robot_y + LIDAR_OFFSET * math.sin(robot_yaw)

    rx, ry = world_to_grid(scan_x, scan_y)

    with lock:
        for i, r in enumerate(ranges):
            # angle is relative to lidar frame, robot_yaw rotates into world frame
            angle = robot_yaw + angle_min + i * angle_increment

            if math.isnan(r) or r <= 0.08:
                continue   # truly invalid reading

            # Clamp infinity to max range so free space gets marked
            if math.isinf(r):
                r = 9.5   # just under max range, no occupied cell marked

            # End point of the beam in world coords
            hit_x = scan_x + r * math.cos(angle)
            hit_y = scan_y + r * math.sin(angle)
            hx, hy = world_to_grid(hit_x, hit_y)

            # Mark free cells along the ray
            cells = bresenham(rx, ry, hx, hy, MAP_CELLS)
            for cx, cy in cells[:-3]:
                log_odds[cy, cx] = max(LO_MIN, log_odds[cy, cx] + LO_FREE)

            # Only mark occupied if it was a real hit (not clamped infinity)
            if r < 9.5 and 0 <= hx < MAP_CELLS and 0 <= hy < MAP_CELLS:
                log_odds[hy, hx] = min(LO_MAX, log_odds[hy, hx] + LO_OCC)


def parse_lidar_json(line):
    """Parse a JSON line from gz topic -e --json-output output."""
    try:
        data = json.loads(line)
        # gz uses camelCase: angleMin, angleStep
        angle_min  = data.get("angleMin",  -math.pi)
        angle_step = data.get("angleStep", 0.00628)
        raw_ranges = data.get("ranges", [])
        # Gazebo outputs "Infinity" as a string — convert to float
        ranges = []
        for r in raw_ranges:
            try:
                ranges.append(float(r))
            except (ValueError, TypeError):
                ranges.append(float('inf'))
        # Get lidar world position directly from message
        world_pose = data.get("worldPose", {})
        pos = world_pose.get("position", {})
        lidar_x = pos.get("x", None)
        lidar_y = pos.get("y", None)
        return ranges, angle_min, angle_step, lidar_x, lidar_y
    except (json.JSONDecodeError, KeyError):
        return None, None, None, None, None


last_odom_time = 0.0

def parse_odom_json(line):
    """Parse odometry JSON from gz topic."""
    global robot_x, robot_y, robot_yaw, last_odom_time
    try:
        data = json.loads(line)
        pos = data["pose"]["position"]
        ori = data["pose"]["orientation"]
        robot_x = pos.get("x", 0.0)
        robot_y = pos.get("y", 0.0)
        qz = ori.get("z", 0.0)
        qw = ori.get("w", 1.0)
        raw_yaw = math.atan2(2*(qw*qz), 1 - 2*(qz*qz))
        # Negate because odom and lidar have opposite rotation conventions
        # Then subtract measured offset (167.7deg) to align forward direction
        robot_yaw = -raw_yaw - math.radians(167.7)
        last_odom_time = time.time()
    except (json.JSONDecodeError, KeyError):
        pass


def subscribe_thread(topic, callback):
    """Run gz topic -e --json in background, call callback per line."""
    cmd = ["gz", "topic", "-e", "--json-output", "-t", topic]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True)
    try:
        for line in proc.stdout:
            line = line.strip()
            if line:
                callback(line)
    except Exception as e:
        print(f"[subscriber {topic}] error: {e}")
    finally:
        proc.terminate()


def lidar_callback(line):
    global last_scan_time
    # Skip scan if odom is stale (older than 0.5s) — avoids wrong position mapping
    if last_odom_time > 0 and (time.time() - last_odom_time) > 0.5:
        print("[mapper] WARNING: stale odom, skipping scan")
        return
    ranges, angle_min, angle_step, lidar_x, lidar_y = parse_lidar_json(line)
    if ranges is not None:
        last_scan_time = time.time()
        update_map_from_scan(ranges, angle_min, angle_step, lidar_x, lidar_y)


def render_map():
    """Convert log-odds grid to a colour OpenCV image."""
    with lock:
        lo = log_odds.copy()

    # Probability from log-odds
    prob = 1.0 - 1.0 / (1.0 + np.exp(lo))

    # BGR image: unknown=grey, free=white, occupied=black
    img = np.full((MAP_CELLS, MAP_CELLS, 3), 128, dtype=np.uint8)
    free_mask = lo < -0.1
    occ_mask  = lo >  0.1
    img[free_mask] = [240, 240, 240]
    img[occ_mask]  = [30,  30,  30]

    # Draw robot position (blue dot) at lidar location
    LIDAR_OFFSET = 1.45
    lidar_wx = robot_x + LIDAR_OFFSET * math.cos(robot_yaw)
    lidar_wy = robot_y + LIDAR_OFFSET * math.sin(robot_yaw)
    rx, ry = world_to_grid(lidar_wx, lidar_wy)
    if 0 <= rx < MAP_CELLS and 0 <= ry < MAP_CELLS:
        cv2.circle(img, (rx, ry), 5, (255, 80, 0), -1)
        # Draw heading arrow
        arrow_len = 12
        ex = int(rx + arrow_len * math.cos(robot_yaw))
        ey = int(ry - arrow_len * math.sin(robot_yaw))
        cv2.arrowedLine(img, (rx, ry), (ex, ey), (255, 80, 0), 2, tipLength=0.4)

    return img


def save_map(img, path="map.png"):
    cv2.imwrite(path, img)
    print(f"[mapper] Map saved to {path}")


def main():
    parser = argparse.ArgumentParser(description="Gazebo standalone LiDAR mapper")
    parser.add_argument("--lidar", default="/lidar",  help="LiDAR topic")
    parser.add_argument("--odom",  default="/model/Flip/odometry",
                        help="Odometry topic (leave blank to use dead-reckoning)")
    parser.add_argument("--save",  action="store_true", help="Press s to save map")
    parser.add_argument("--no-odom", action="store_true",
                        help="Disable odometry (robot stays at origin)")
    args = parser.parse_args()

    print(f"[mapper] Starting — lidar={args.lidar}  odom={args.odom}")
    print(f"[mapper] Map: {MAP_CELLS}x{MAP_CELLS} cells @ {RESOLUTION}m/cell = {MAP_SIZE_M}m")
    print("[mapper] Keys: 's' = save map   'r' = reset map   'q' = quit")

    # Start lidar subscriber thread
    t_lidar = threading.Thread(target=subscribe_thread,
                               args=(args.lidar, lidar_callback), daemon=True)
    t_lidar.start()

    # Start odom subscriber thread (optional)
    if not args.no_odom:
        t_odom = threading.Thread(target=subscribe_thread,
                                  args=(args.odom, parse_odom_json), daemon=True)
        t_odom.start()

    win = "Gazebo Occupancy Map (q=quit, s=save, r=reset)"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win, 700, 700)

    while True:
        img = render_map()

        # Status overlay
        age = time.time() - last_scan_time if last_scan_time else 999
        status = f"Robot: ({robot_x:.1f}, {robot_y:.1f})  yaw: {math.degrees(robot_yaw):.0f}deg  scan age: {age:.1f}s"
        cv2.putText(img, status, (10, MAP_CELLS - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 0), 1)

        cv2.imshow(win, img)
        key = cv2.waitKey(100) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s'):
            save_map(img)
        elif key == ord('r'):
            with lock:
                log_odds[:] = 0
            print("[mapper] Map reset.")

    cv2.destroyAllWindows()
    print("[mapper] Done.")


if __name__ == "__main__":
    main()