""" PID control for rotating the GreenDigger to a target yaw (angle in degrees).

You can adjust the PID gains, maximum angular velocity, deadband, and other parameters at the top of the file to tune the behavior of the rotation. 
The compute_heading_command function takes in the latest sensor state and a target heading, and returns a drive command with linear and angular velocity along with a boolean indicating whether the target heading has been reached.

This PID has been changed to only use the proportional and derivative terms, with the integral term disabled (set to 0) and anti-windup limit set to 0, since we found that the integral term was not necessary for our use case and could lead to overshooting if not tuned carefully.
There are various features within this code that support integral control, such as the integral_error variable and the max_integral_error limit, which can be re-enabled if you want to experiment with adding integral control back in.

    Author: Ocarian
    Contributors: GrijzePanda, Replitard
 """
import math

proportional_gain = 2.0
integral_gain = 0.0
derivative_gain = 0.6
max_integral_error = 0.0
max_angular_velocity = 2.0

# Deadband around the target yaw where no rotation command is sent.
yaw_deadband = math.radians(10.0)

# Error larger than this threshold will use an aggressive full-speed turn.
fast_rotate_threshold = math.radians(35.0)

# Global state updated from the interface sensor data.
current_yaw = 0.0
current_yaw_rate = 0.0
heading_data_ready = False
integral_error = 0.0

def normalize_angle(angle):
    """Normalize an angle to the range [-pi, pi]."""
    return (angle + math.pi) % (2 * math.pi) - math.pi

def quat_to_yaw(x, y, z, w):
    """Extract yaw in radians from a quaternion."""
    return math.atan2(
        2 * (w * z + x * y),
        1 - 2 * (y**2 + z**2),
    )

def update_current_heading(sensor_state):
    """Update PID state from the interface IMU values."""
    global current_yaw, current_yaw_rate, heading_data_ready

    imu = sensor_state.get("imu", {})
    orientation_values = (
        imu.get("orientation_x"),
        imu.get("orientation_y"),
        imu.get("orientation_z"),
        imu.get("orientation_w"),
    )

    if any(value is None for value in orientation_values):
        heading_data_ready = False
        return False

    current_yaw = quat_to_yaw(*orientation_values)
    current_yaw_rate = imu.get("angular_velocity_z") or 0.0
    heading_data_ready = True
    return True


def reset_pid():
    """Reset accumulated PID state."""
    global integral_error
    integral_error = 0.0


def compute_heading_control(target_yaw, control_loop_interval_s):
    """Return angular velocity for the current yaw and target yaw."""
    global integral_error

    yaw_error = normalize_angle(target_yaw - current_yaw)

    # If within the deadband, stop rotating.
    if abs(yaw_error) < yaw_deadband:
        return 0.0

    # If the error is large, use direct maximum-turn command for fast in-place rotation.
    if abs(yaw_error) > fast_rotate_threshold:
        return math.copysign(max_angular_velocity, yaw_error)

    # Integral term is kept for reference but contributes nothing while integral_gain = 0.
    integral_error += yaw_error * control_loop_interval_s
    integral_error = max(-max_integral_error, min(max_integral_error, integral_error))

    angular_velocity_command = (
        proportional_gain * yaw_error
        + integral_gain * integral_error
        - derivative_gain * current_yaw_rate
    )

    return max(
        -max_angular_velocity,
        min(max_angular_velocity, angular_velocity_command),
    )


def compute_heading_command(
    sensor_state,
    target_heading_degrees=90,
    control_loop_interval_s=0.02,
):
    """Return one drive command for rotating to the target heading."""
    target_yaw = math.radians(target_heading_degrees)

    if not update_current_heading(sensor_state):
        return 0.0, 0.0, False

    angular_velocity_command = compute_heading_control(
        target_yaw,
        control_loop_interval_s,
    )
    yaw_error = normalize_angle(target_yaw - current_yaw)
    target_reached = abs(yaw_error) < yaw_deadband

    return 0.0, angular_velocity_command, target_reached
