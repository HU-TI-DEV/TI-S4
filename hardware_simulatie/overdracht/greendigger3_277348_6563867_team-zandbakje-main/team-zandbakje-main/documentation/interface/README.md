# Digger Interface

`Author: Replitard`

## Overview
The interface is the bridge between Gazebo and the logic layer. It subscribes to raw Gazebo topics, stores the latest values in a shared state dictionary using plain Python types, and exposes functions for publishing drive and arm commands. The logic layer never touches Gazebo message types directly, it only calls interface functions.

It sits in `src/interface/` and is used by the behaviour manager and any other script that needs sensor data or needs to send commands.

---

## How It Works
### Sensor State
Call `start_subscribers()` once at startup to subscribe to all topics. After that, call `get_state()` anywhere to get a copy of the latest values.

The state dictionary contains the following entries:

| Key | Fields | Source |
|-----|--------|--------|
| `imu` | `orientation_x/y/z/w`, `angular_velocity_x/y/z`, `linear_acceleration_x/y/z` | IMU sensor |
| `lidar` | `first_range`, `range_count` | LIDAR scan |
| `camera` | `width`, `height`, `pixel_format_type` | Camera (metadata only) |
| `contact` | `chassis_touching` | Chassis contact sensor |
| `pose` | `current_x`, `current_y` | World dynamic pose |
| `arm` | `shoulder_pan_joint`, `shoulder_lift_joint`, `elbow_joint`, `wrist_1_joint`, `wrist_2_joint`, `wrist_3_joint` | Arm joint states |
| `bucket_contact` | `touching`, `x`, `y` | Bucket end-effector contact |
| `last_update_time` | float (epoch seconds) | Updated on every callback |

---

### Drive Commands
| Function | Description |
|----------|-------------|
| `publish_drive_command(linear_x, angular_z)` | Send a velocity command to the digger. |
| `stop_drive()` | Publish zero velocity. shorthand for `publish_drive_command()`. |

---

### Arm Commands (forward kinematics)
| Function | Description |
|----------|-------------|
| `publish_arm_command(shoulder_pan_joint=..., ...)` | Publish individual joint targets. Omit joints to leave them unchanged. |
| `publish_arm_targets(dict)` | Same as above but takes a joint-name keyed dictionary. |
| `publish_arm_pose(pose_name)` | Publish a named pose from `arm_helper.py`. |

Named poses available: `neutral`, `dig`, `arm_up`, `arm_down`, `rotate_left`, `right_sweep`, `arm_up_high`, `arm_out_of_the_way`.  
Pose names are case- and whitespace-insensitive. Common aliases like `"up"` and `"arm up"` also work.

---

### Terrain Spawn / Despawn
| Function | Description |
|----------|-------------|
| `despawn(model_name)` | Remove a model from the world by name. Used for terrain refreshing. |
| `spawn(model_name, sdf_filename)` | Spawn a model into the world from an SDF file. Used for terrain refreshing. |

---

## Running the Interface
The interface has a small built-in test that prints a state summary every second. Run it from the project root directory.

```bash
python3 src/interface/interface.py
```

Gazebo must already be running with the digger world loaded and playing, otherwise no sensor data will arrive.

---

## Important Files

| File | Purpose |
|------|---------|
| [interface.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/interface/interface.py) | Subscriptions, state dictionary, and command publishers |
| [arm_helper.py](https://github.com/2025-TICT-TV2SE4-24-3-V/team-zandbakje/blob/main/src/interface/arm_helper.py) | Named arm poses and alias resolution |

---

## Current Assumptions
* `start_subscribers()` is called before any `get_state()` reads, meaning first few states will be empty.
* Gazebo is already running and the world is playing when the interface starts.
* One interface instance per process. The Gazebo node and publishers are module-level globals.

---

## Known Limitations
* LIDAR only stores the first range value and the total count. Full scan processing is not implemented.
* Camera stores metadata only (width, height, format), no pixel data.
* Bucket contact only stores the first contact point per tick.
* No reconnect logic if Gazebo restarts while the interface is running.

---

## Additional Documentation
For a detailed explanation of the project layer architecture and how the interface fits into the rest of the system, see: [Architecture](../../docs/project-items/project-style/architecture.md)

For behaviour manager details, see: [Behaviour Manager](../behaviour_manager/README.md)

---

## Sources used:
- Gazebo transport: Python support. (n.d.). https://gazebosim.org/api/transport/15/python.html
- subprocess — Subprocess management. (n.d.). Python Documentation. https://docs.python.org/3/library/subprocess.html
- W3Schools.com. (n.d.-b). https://www.w3schools.com/python/ref_module_subprocess.asp
- GeeksforGeeks. (2026a, April 4). Python subprocess module. GeeksforGeeks. https://www.geeksforgeeks.org/python/python-subprocess-module/
- dataclasses — Data Classes. (n.d.). Python Documentation. https://docs.python.org/3/library/dataclasses.html
- Osrf. (n.d.). SDFormat Specification. https://sdformat.org/spec/1.11/sdf/
- Gazebo MSGs: Gazebo MSgs. (n.d.). https://gazebosim.org/api/msgs/9/index.html