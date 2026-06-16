"""
Calculate drive commands to move the digger toward a target point.

    Author: GrijzePanda
    Contributors: Replitard
"""
import math
import drive_pid

POSITION_TOLERANCE = 2.0
MAX_LINEAR_SPEED = 2.5
CONTROL_INTERVAL = 0.1


def compute_poi_command(
    sensor_state,
    target_x,
    target_y,
    control_loop_interval_s=CONTROL_INTERVAL,
):
    """Return one drive command for moving toward a point of interest."""
    pose = sensor_state.get("pose", {})
    current_x = pose.get("current_x")
    current_y = pose.get("current_y")

    if current_x is None or current_y is None:
        return 0.0, 0.0, False

    dx = target_x - current_x
    dy = target_y - current_y
    distance = math.sqrt(dx * dx + dy * dy)

    if distance < POSITION_TOLERANCE:
        return 0.0, 0.0, True

    if not drive_pid.update_current_heading(sensor_state):
        return 0.0, 0.0, False

    target_yaw = math.atan2(dy, dx)
    yaw_error = drive_pid.normalize_angle(target_yaw - drive_pid.current_yaw)
    angular_cmd = drive_pid.compute_heading_control(
        target_yaw,
        control_loop_interval_s,
    )

    heading_scale = max(0.0, 1.0 - abs(yaw_error) / math.radians(90))
    linear_cmd = MAX_LINEAR_SPEED * heading_scale

    if distance < 4.0:
        linear_cmd *= max(0.25, distance / 4.0)

    return linear_cmd, angular_cmd, False
