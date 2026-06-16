# PID for locomotion

`Author: Ocarian`

## Overview

This feature provides yaw control for the GreenDigger using a PID-style heading controller.
The PID controller is responsible for rotating the digger toward a target heading while the point-of-interest module converts a destination coordinate into a desired heading.

---

## How It Works

### Core behaviour

`drive_pid.py` implements heading control in three steps:

1. Read IMU orientation and angular velocity from `sensor_state["imu"]`
2. Convert the quaternion into a yaw angle in radians
3. Compute angular velocity to minimize the yaw error relative to the target heading

The controller has two main functions:

* `update_current_heading(sensor_state)` — refreshes local heading state from IMU values
* `compute_heading_command(sensor_state, target_heading_degrees, control_loop_interval_s)` — returns a drive command for the current heading target

### Integration with POI navigation

`drive_poi.py` uses the PID controller as the steering component for point-to-point navigation.
The navigation flow is:

* calculate the target heading from the current position and POI coordinate
* update the current heading from IMU data
* compute steering angular velocity using `drive_pid.compute_heading_control()`
* reduce forward speed when the digger is close to the target

This workflow puts all the navigation procedures on `drive_poi.py` so that the PID controller only has to focus on turning.

---

## Important Files

| File                         | Purpose                                                                           |
| ---------------------------- | --------------------------------------------------------------------------------- |
| [drive_pid.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/drive_pid.py)           | PID controller and yaw command generation                                         |
| [drive_poi.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/drive_poi.py)           | Point-of-interest navigator that converts coordinates into yaw and speed commands |
| [interface/interface.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/interface/interface.py) | Provides IMU orientation and pose data from Gazebo                                |

---

## PID Behaviour Details

### Active terms

The current implementation uses:
* Proportional term (`proportional_gain`)
* Derivative term (`derivative_gain`)

The integral term was once used and built-in for future use but disabled by default:
* `integral_gain = 0.0`
* `max_integral_error = 0.0`

This avoids windup and overshoot while preserving the option to enable integral control later.

### Stability features

* `yaw_deadband` — no rotation command is issued when the yaw error is smaller than this threshold
* `fast_rotate_threshold` — large errors use a direct full-speed turn
* `max_angular_velocity` — angular velocity commands are capped for safe motion

---

## Current Assumptions

* IMU orientation is available in `sensor_state["imu"]`.
* Heading is represented as a quaternion and converted to yaw.
* Target headings are provided in degrees and converted to radians internally.
* The controller only manages rotation; forward motion is managed by the navigation layer.

---

## Possible Future Improvements

* Implement obstacle avoidance into the heading controller.
* Implement the integral term and use the already written code for it.
* The deadband may cause the digger to stop short of exact heading alignment, implement a fix for this.
* Add IMU yaw validation or alternate heading references so the controller does not assume IMU yaw is always the correct absolute heading.

---

## Additional Documentation

For a deeper explanation of the PID algorithm, yaw normalization, and tuning, see: [PID Technical Documentation](TECHNICAL_DOCUMENTATION.md)

## Sources used:

* GeeksforGeeks. Proportional Integral Derivative Controller in Control System. GeeksforGeeks. Published March 26, 2026. [https://www.geeksforgeeks.org/electronics-engineering/proportional-integral-derivative-controller-in-control-system/](https://www.geeksforgeeks.org/electronics-engineering/proportional-integral-derivative-controller-in-control-system/)
* ROS.org. Adding a PID to a realtime joint controller. ROS.org. Published October 4, 2011. [https://wiki.ros.org/pr2_mechanism/Tutorials/Adding%20a%20PID%20to%20a%20realtime%20joint%20controller](https://wiki.ros.org/pr2_mechanism/Tutorials/Adding%20a%20PID%20to%20a%20realtime%20joint%20controller)
* Wikipedia contributors. PID controller - Wikipedia. Published June 14, 2026. [https://en.wikipedia.org/wiki/PID_controller](https://en.wikipedia.org/wiki/PID_controller)
* Wikipedia contributors. Quaternion. Wikipedia. Published May 19, 2026. [https://en.wikipedia.org/wiki/Quaternion](https://en.wikipedia.org/wiki/Quaternion)
* Venatu. Extracting Yaw from a Quaternion. Stack Overflow. Published May 24 2022. [https://stackoverflow.com/questions/5782658/extracting-yaw-from-a-quaternion](https://stackoverflow.com/questions/5782658/extracting-yaw-from-a-quaternion)
* TroyDL. Has anyone seen this issue before? Massive twitching on yaw. Reddit.com. Published July 8, 2016. [https://www.reddit.com/r/Multicopter/comments/4rvd5n/has_anyone_seen_this_issue_before_massive/](https://www.reddit.com/r/Multicopter/comments/4rvd5n/has_anyone_seen_this_issue_before_massive/)
* Hu-Ti-Dev. Gazebo deel III. GitHub. Published March 5, 2026. [ https://github.com/HU-TI-DEV/TI-S4/blob/main/hardware_simulatie/gazebo/README.md#programma-gazebo-deel-iii]( https://github.com/HU-TI-DEV/TI-S4/blob/main/hardware_simulatie/gazebo/README.md#programma-gazebo-deel-iii)
