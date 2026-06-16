"""
    Author: Ocarian
    Contributors: GrijzePanda
"""
import math
import time
from gz.transport import Node
from gz.msgs.twist_pb2 import Twist
from gz.msgs.imu_pb2 import IMU

# PID gains for yaw control.
# proportional_gain = proportional gain, integral_gain = integral gain, derivative_gain = derivative gain.
proportional_gain, integral_gain, derivative_gain = 2.0, 0.0, 0.6

# Maximum angular velocity command sent to the robot.
max_angular_velocity = 2.0

# Anti-windup limit for the integral term.
max_integral_error = 0.0

# Deadband around the target yaw where no rotation command is sent.
yaw_deadband = math.radians(2.0)

# Error larger than this threshold will use an aggressive full-speed turn.
fast_rotate_threshold = math.radians(35.0)

# Global state updated by IMU callback.
current_yaw = 0.0
current_yaw_rate = 0.0
imu_data_ready = False

# PID state
integral_error = 0.0

# Normalize an angle to the range [-pi, pi].
def normalize_angle(angle):
    return (angle + math.pi) % (2 * math.pi) - math.pi


# Convert a quaternion to yaw angle in radians.
def quat_to_yaw(q):
    return math.atan2(
        2 * (q.w * q.z + q.x * q.y),
        1 - 2 * (q.y**2 + q.z**2),
    )


# IMU callback updates the current yaw and yaw rate state.
def imu_callback(msg: IMU):
    global current_yaw, current_yaw_rate, imu_data_ready
    current_yaw = quat_to_yaw(msg.orientation)
    current_yaw_rate = msg.angular_velocity.z
    imu_data_ready = True


# PID heading controller for external scripts. (extracted from rotate_to_target_yaw)
def compute_heading_control(
    target_yaw,
    control_loop_interval_s,
):
    global integral_error

    yaw_error = normalize_angle(target_yaw - current_yaw)

    # If within the deadband, stop rotating.
    if abs(yaw_error) < yaw_deadband:
        return 0.0

    # If the error is large, use direct maximum-turn command for fast in-place rotation.
    if abs(yaw_error) > fast_rotate_threshold:
        return math.copysign(max_angular_velocity, yaw_error)

    # PID on the remaining error.
    integral_error += yaw_error * control_loop_interval_s

    integral_error = max(-max_integral_error, min(max_integral_error, integral_error))

    angular_velocity_command = (
        proportional_gain * yaw_error
        + integral_gain * integral_error
        - derivative_gain * current_yaw_rate
    )

    angular_velocity_command = max(
        -max_angular_velocity,
        min(max_angular_velocity, angular_velocity_command),
    )

    return angular_velocity_command


# Rotate the robot to a target yaw using PID control.
def rotate_to_target_yaw(
    target_heading_degrees=90,
    max_duration_s=12,
    control_loop_interval_s=0.02,
):
    node = Node()
    pub = node.advertise("/model/digger/cmd_vel", Twist)
    node.subscribe(IMU, "/digger/imu", imu_callback)

    target_yaw = math.radians(target_heading_degrees)
    integral_error = 0.0
    start_time = time.time()

    # Ensure the vehicle is not carrying any linear motion before rotating.
    zero_msg = Twist()
    zero_msg.linear.x = 0.0
    zero_msg.linear.y = 0.0
    zero_msg.linear.z = 0.0
    zero_msg.angular.x = 0.0
    zero_msg.angular.y = 0.0
    zero_msg.angular.z = 0.0
    for _ in range(10):
        pub.publish(zero_msg)
        time.sleep(0.02)

    while time.time() - start_time < max_duration_s:
        if not imu_data_ready:
            time.sleep(0.01)
            continue

        yaw_error = normalize_angle(target_yaw - current_yaw)

        # Uses the PID controller that got moved to a separate function
        angular_velocity_command = compute_heading_control(
            target_yaw,
            control_loop_interval_s,
        )

        msg = Twist()
        msg.linear.x = 0.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = angular_velocity_command
        pub.publish(msg)

        print(
            f"yaw={math.degrees(current_yaw):.1f}° err={math.degrees(yaw_error):.1f}° "
            f"cmd={angular_velocity_command:.2f}"
        )

        time.sleep(control_loop_interval_s)

    # stop
    pub.publish(Twist())

    return {
        "final_yaw_deg": math.degrees(current_yaw),
        "final_error_deg": math.degrees(normalize_angle(target_yaw - current_yaw)),
        "duration_s": time.time() - start_time,
    }
