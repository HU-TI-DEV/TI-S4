# Test codebase

`Author: Ocarian`

## Overview
This folder contains simple scripts and debugging tools for validating the Green Digger simulation and control stack.
The tests are not full automated unit tests, but they are useful for checking whether the camera, manual drive input, heading control, and navigation components are working correctly.

## Usage
1. Start the Gazebo world from `code/environment/`.
2. Open a terminal in the `code/` directory.
3. Run one of the test scripts with Python, for example:
   - `python3 tests/camera_test.py`
   - `python3 tests/keyboard_publisher.py`
   - `python3 tests/navigate_to_point.py`

## Scripts

### `camera_test.py`
- Purpose: subscribe to the digger camera feed and display live frames.
- What it does: listens on `/digger/camera`, converts the incoming image messages to OpenCV frames, and opens a window to show the current camera view.
- When to use: verify that the camera topic is publishing correctly and that the image feed is available in the simulation.

### `keyboard_publisher.py`
- Purpose: provide manual keyboard control for the simulated digger.
- What it does: reads arrow keys and publishes `Twist` messages to `/model/digger/cmd_vel`.
- Controls:
  - Arrow up / down: move forward / backward
  - Arrow left / right: turn left / right
  - Space or `s`: stop
  - `q`: quit
- When to use: test manual drive commands and verify that the digger responds to velocity commands.

### `navigate_to_point.py`
- Purpose: drive the robot to a target coordinate inside the Gazebo world.
- What it does: reads the current pose from the interface layer, computes a target heading using `pid_heading`, and publishes velocity commands until the robot reaches the target.
- When to use: verify navigation, pose data, and integration between the interface and heading controller.
- Notes: this script depends on the `interface` module and the IMU topic, so it should be used when the whole simulation stack is running.

### `pid_heading.py`
- Purpose: provide yaw control logic and IMU data handling.
- What it does: subscribes to `/digger/imu`, computes heading error, and returns angular velocity commands using a PID-like controller.
- When to use: test yaw control behavior or reuse the heading controller from other scripts.
- Features: includes `compute_heading_control()` and `rotate_to_target_yaw()` helper functions.

## Notes
- These scripts are intended as debug tools, not as the main behaviour manager.
- `camera_test.py` requires OpenCV (`cv2`) to be installed.
- `keyboard_publisher.py` uses terminal raw input and works best in a Linux-compatible terminal.
- `navigate_to_point.py` is useful for manual verification of the robot's localization, heading, and commanded motion.
- If new test scripts are added later, add them to this document and describe the intended use case.

