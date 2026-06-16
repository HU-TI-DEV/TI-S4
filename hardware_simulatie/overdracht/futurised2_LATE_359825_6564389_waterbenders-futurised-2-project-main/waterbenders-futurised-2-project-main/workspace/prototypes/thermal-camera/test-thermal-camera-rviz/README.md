# Python VENV + ROS2 Guide

# Contents
- [Python VENV + ROS2 Guide](#python-venv--ros2-guide)
- [Contents](#contents)
  - [Big picture (what went wrong)](#big-picture-what-went-wrong)
    - [1. ROS package not found](#1-ros-package-not-found)
    - [2. Python package not found](#2-python-package-not-found)
    - [3. Pip install blocked](#3-pip-install-blocked)
- [Correct architecture](#correct-architecture)
  - [Setup Guide (Step-by-step)](#setup-guide-step-by-step)
    - [Check:](#check)
  - [Daily workflow](#daily-workflow)
  - [Debugging Guide](#debugging-guide)
    - [Wrong Python being used](#wrong-python-being-used)
- [Running GZ and Python file](#running-gz-and-python-file)
  - [FULL START SEQUENCE (IMPORTANT ORDER)](#full-start-sequence-important-order)
  - [Debug topic list](#debug-topic-list)

## Big picture (what went wrong)
You hit three different classes of problems:

### 1. ROS package not found
```bash
ModuleNotFoundError: No module named 'rclpy'
```

Cause: You didn’t source ROS
```bash
source /opt/ros/jazzy/setup.bash
```
- rclpy comes from ROS 2 Jazzy
- It is NOT installed via pip
- It only exists after sourcing ROS


### 2. Python package not found
```bash
ModuleNotFoundError: No module named 'ultralytics'
```

Cause: Installed in the wrong environment
- Ultralytics YOLO is a pip package
- Installing it on Windows ≠ installing it in Docker


### 3. Pip install blocked
```bash
error: externally-managed-environment
```

Cause: Ubuntu blocks global pip installs (PEP 668)

# Correct architecture

The setup inside your Docker container:
```bash
ROS (apt) → provides rclpy
venv (python) → provides ultralytics + vision libraries
```
## Setup Guide (Step-by-step)
1. Enter the container
```bash
./rungazebo.ps1
```
1. Install venv support (once)
```bash
apt update
apt install -y python3-venv python3-full
```
1. Create a virtual environment
```bash
python3 -m venv /workspace/venv --system-site-packages
```
Why `--system-site-packages`?
So your venv can still access:
- ROS packages like rclpy
- System-installed dependencies
4. Activate the venv
```bash
source /workspace/venv/bin/activate
```

### Check:
```bash
which python
which pip
```
Expected:
```bash
/workspace/venv/bin/python
/workspace/venv/bin/pip
```

5. Install Python dependencies
```bash
pip install --upgrade pip
pip install ultralytics opencv-python torch torchvision
```
6. Source ROS (VERY IMPORTANT)
```bash
source /opt/ros/jazzy/setup.bash
```
If using a workspace:
```bash
source install/setup.bash
```
7. Run your script
```bash
python thermal-camera-RGBtest.py
```

## Daily workflow

Every time you open the container:
```bash
source /workspace/venv/bin/activate
source /opt/ros/jazzy/setup.bash
```
Run python file:
```bash
python3 <filename>
```
## Debugging Guide
```bash
ModuleNotFoundError: No module named 'rclpy'
```
Fix:
```bash
source /opt/ros/jazzy/setup.bash
```
---
---
```bash
ModuleNotFoundError: No module named 'ultralytics'
```
Fix:
```bash
source /workspace/venv/bin/activate
pip install ultralytics
```
---
---
```bash
error: externally-managed-environment
```
Fix: Use a virtual environment
```bash
python3 -m venv /workspace/venv --system-site-packages
```

### Wrong Python being used
Check:
```bash
which python
which pip
```
If not pointing to /workspace/venv/...:

Fix:
```bash
source /workspace/venv/bin/activate
ROS works but pip packages don’t (or vice versa)
```
Cause: Wrong order

Correct order:
```bash
source /workspace/venv/bin/activate
source /opt/ros/jazzy/setup.bash
```


# Running GZ and Python file

ROS2 + Gazebo + Thermal Pipeline Startup (4-Terminal Setup)
| Terminal | Purpose                                |
| -------- | -------------------------------------- |
| 1        | Gazebo simulation (`gz sim`)           |
| 2        | ROS ↔ Gazebo bridge                    |
| 3        | Python thermal + YOLO + RViz publisher |
| 4        | RViz visualization                     |

**TERMINAL 1** — Gazebo Simulator

```bash
cd models
gz sim room-v2.sdf
```
 This runs your world + thermal camera plugin.

---

**TERMINAL 2** — ROS ↔ Gazebo Bridge
```bash
source /opt/ros/jazzy/setup.bash
ros2 run ros_gz_bridge parameter_bridge \
/camera/image@sensor_msgs/msg/Image@gz.msgs.Image \
/FLIP/thermal_camera@sensor_msgs/msg/Image@gz.msgs.Image
```

 This exposes Gazebo topics to ROS 2.

---

**TERMINAL 3** — Python Processing Node
```bash
source /workspace/venv/bin/activate
source /opt/ros/jazzy/setup.bash
cd /workspace/models/scripts/thermal-camera
python thc-rviz.py
```
⚠️**IMPORTANT (before running Terminal 3)**

*Make sure NumPy is fixed:*
```bash
pip install "numpy==1.26.4"
```
---
 **TERMINAL 4** — RViz2 Visualization
```bash
source /opt/ros/jazzy/setup.bash
rviz2
```
---

In RViz UI:
1. Click Add
2. Select Image
3. Set topic to:
    `/thermal/heatmap_image`
(Optional) also add:
/camera/image

## FULL START SEQUENCE (IMPORTANT ORDER)

Run in this exact order:

Terminal **1** → gz sim room-v2.sdf<br>
Terminal **2** → ros_gz_bridge<br>
Terminal **3** → python node<br>
Terminal **4** → rviz2<br>

## Debug topic list
```bash
source /opt/ros/jazzy/setup.bash
ros2 topic list
```