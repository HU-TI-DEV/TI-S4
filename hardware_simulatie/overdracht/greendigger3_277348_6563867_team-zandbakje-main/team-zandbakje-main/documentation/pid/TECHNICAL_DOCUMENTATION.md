# PID Technical Documentation

`Author: Ocarian`

## Overview

This document describes the implementation details behind `src/drive_pid.py` and how it integrates with the POI navigation module in `src/drive_poi.py`.

The PID controller is used to rotate the digger toward a desired heading while the POI navigator calculates the target heading from the current position and destination coordinates.

---

## Controller responsibilities

`drive_pid.py` is responsible for:

* extracting yaw from IMU quaternion data
* maintaining the current heading state
* computing a steering command to reduce yaw error
* supporting a deadband and a fast-rotation mode

The controller does not compute forward speed. That responsibility belongs to the POI navigation module.

---

## Key variables

| Variable | Purpose |
|----------|---------|
| `proportional_gain` | Scales the yaw error in the P term |
| `integral_gain` | Scales accumulated error in the I term |
| `derivative_gain` | Scales the yaw rate in the D term |
| `max_integral_error` | Clamps the integral error for anti-windup |
| `max_angular_velocity` | Caps the commanded angular velocity |
| `yaw_deadband` | Defines the range where no rotation is required |
| `fast_rotate_threshold` | Defines when to use a full-speed turn |
| `current_yaw` | Latest yaw estimate from the IMU |
| `current_yaw_rate` | Latest rotational speed around Z |
| `integral_error` | Accumulated yaw error over time |

---

## Sensor input

The controller expects `sensor_state` to contain an `imu` dictionary with quaternion orientation fields and z-axis angular velocity:

```python
state["imu"] = {
    "orientation_x": ...,
    "orientation_y": ...,
    "orientation_z": ...,
    "orientation_w": ...,
    "angular_velocity_z": ...,
}
```

`update_current_heading(sensor_state)` extracts these values and updates `current_yaw` and `current_yaw_rate`. If any quaternion component is missing, heading data is set to a not-ready state.

---

## Yaw extraction and normalization

### Quaternion to yaw

The yaw angle is derived from the quaternion using:

```python
math.atan2(
    2 * (w * z + x * y),
    1 - 2 * (y**2 + z**2),
)
```

This returns yaw in radians, suitable for 2D heading control.

### Angle normalization

Yaw error is normalized to the range `[-pi, pi]` using:

```python
(angle + math.pi) % (2 * math.pi) - math.pi
```

This ensures the controller always chooses the shortest rotational direction.

---

## Control logic

### Deadband

If the yaw error is smaller than `yaw_deadband`, the controller returns zero angular velocity:

```python
if abs(yaw_error) < yaw_deadband:
    return 0.0
```

This avoids small oscillations around the target heading.

### Fast rotation

When the yaw error exceeds `fast_rotate_threshold`, the controller uses a full-speed turn:

```python
if abs(yaw_error) > fast_rotate_threshold:
    return math.copysign(max_angular_velocity, yaw_error)
```

This quickly aligns the digger when the target heading is far from the current heading.

### PID calculation

For smaller errors, the controller computes a command using:

```python
proportional_gain * yaw_error
+ integral_gain * integral_error
- derivative_gain * current_yaw_rate
```

The integral term is accumulated as:

```python
integral_error += yaw_error * control_loop_interval_s
integral_error = max(-max_integral_error, min(max_integral_error, integral_error))
```

Because `integral_gain` and `max_integral_error` are currently set to `0.0`, the integral term does not affect the output in the default configuration. These values can be changed if the future state of the system requires the integral term to be used within the PID controller.

### Velocity correction

The resulting angular velocity is clamped to the configured maximum:

```python
return max(-max_angular_velocity, min(max_angular_velocity, angular_velocity_command))
```

This makes sure that the velocity can never go past speeds considered unsafe or too slow. In short, when the velocity goes past or below maximum configured levels, it get corrected to the the maximum of the velocity it's currently on.

---

## Main public function

`compute_heading_command(sensor_state, target_heading_degrees, control_loop_interval_s)` is the external API for the heading controller.

It performs the following steps:

1. converts `target_heading_degrees` to radians
2. updates the current heading from the IMU
3. computes `angular_velocity_command`
4. assesses whether the target heading is reached using the deadband
5. returns `(linear_velocity, angular_velocity, target_reached)`

The linear velocity is always `0.0` from this function because rotation-only control is expected.

---

## Navigation integration

`src/drive_poi.py` uses `drive_pid.compute_heading_control()` when moving toward a POI.

The POI navigator:

* computes the heading to the target coordinate with `atan2(dy, dx)`
* updates the IMU-derived heading state
* uses the PID controller to generate `angular_cmd`
* sets the linear speed based on heading alignment and remaining distance

Linear speed is scaled down when the digger is not well aligned with the target heading and again when the target is within 4 meters.

Distance based slowdown is with a minimum factor of 0.25.

---

## Tuning guidance

### Proportional gain

Increasing `proportional_gain` makes the digger turn more aggressively toward the target heading, but too high a value can cause overshoot.

### Derivative gain

`derivative_gain` damps rotational motion by reacting to the current yaw rate. It helps prevent overshoot.

### Deadband and fast rotate threshold

* `yaw_deadband` should be large enough to avoid constant small corrections but small enough to preserve acceptable heading accuracy.
* `fast_rotate_threshold` defines when the controller should stop using PID blending and instead turn at maximum angular velocity.

### Integral term

The integral term can be enabled by increasing `integral_gain` and a non-zero `max_integral_error`. This will increase the rate of which the accumulated error gets reduced to the set target.

---

## Notes and extension points

* `reset_pid()` resets the accumulated integral state when a new heading target is selected.
* This controller only manages orientation, not position. Other navigation modules can reuse it for heading control without changing position logic.
