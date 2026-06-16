# Viewing multiple sensor outputs

Below is a guideline for running the Gazebo simulation and using RViz together with ROS2 to get the output from different sensors. It is required to use multiple terminals at the same time within the docker container. 

***For some sensors there might be more steps, this is just a guideline.***


# 4-Terminal setup

ROS2 + Gazebo + Thermal Pipeline Startup

| Terminal | Purpose                                |
| -------- | -------------------------------------- |
| 1        | Gazebo simulation (`gz sim`)           |
| 2        | ROS ↔ Gazebo bridge                    |
| 3        | Python thermal + YOLO + RViz publisher |
| 4        | [RViz visualization](../RViz-visualisation/README.md)                     |

---
## Running programs

**TERMINAL 1** — Gazebo Simulator

```bash
cd modelsworkspace/models
gz sim room-v2.sdf
```
*This runs the world + thermal camera plugin.*

---

**TERMINAL 2** — ROS ↔ Gazebo Bridge
```bash
source /opt/ros/jazzy/setup.bash

ros2 run ros_gz_bridge parameter_bridge \
/camera/image@sensor_msgs/msg/Image@gz.msgs.Image \
/FLIP/thermal_camera@sensor_msgs/msg/Image@gz.msgs.Image \
/front/image@sensor_msgs/msg/Image@gz.msgs.Image \
/rear/image@sensor_msgs/msg/Image@gz.msgs.Image
```
*This exposes Gazebo topics to ROS 2.*

---

**TERMINAL 3** — Python Processing Node
```bash
source /workspace/venv/bin/activate
source /opt/ros/jazzy/setup.bash
cd <pythonfile-location>
python <pythonfile>
```
*This runs the Python scripts inside a `venv`*

---
 **TERMINAL 4** — RViz2 Visualization
```bash
source /opt/ros/jazzy/setup.bash
rviz2
```
*This starts RViz*

## Camera's + Lidar 2D Example

**TERMINAL 1** — Gazebo Simulator

```bash
cd models
gz sim room-v2.sdf
```

---
**TERMINAL 2** — ROS2 Bridge

Instead of the regular **terminal 2** prompt as above, if we want **multiple** sensors to show in Rviz we need to make sure we're **bridging ROS2 with Rviz**. Use this prompt for both camera and thermal camera in **terminal 2**:
```bash 
source /opt/ros/jazzy/setup.bash

ros2 run ros_gz_bridge parameter_bridge \
/camera/image@sensor_msgs/msg/Image@gz.msgs.Image \
/FLIP/thermal_camera@sensor_msgs/msg/Image@gz.msgs.Image \
/front/image@sensor_msgs/msg/Image@gz.msgs.Image \
/rear/image@sensor_msgs/msg/Image@gz.msgs.Image
```
---
**TERMINAL 3** — Python Processing Node
```bash
source /workspace/venv/bin/activate
source /opt/ros/jazzy/setup.bash
cd /workspace/models/scripts/thermal-camera
python thc-rviz.py
```
---
 **TERMINAL 4** — RViz2 Visualization
```bash
source /opt/ros/jazzy/setup.bash
rviz2
```
---

**TERMINAL 5:** - Lidar Python launch

```bash
cd /workspace/models/scripts/lidar-2d-rviz
source /opt/ros/jazzy/setup.bash
ros2 launch /workspace/models/scripts/lidar-2d-rviz/slam_gazebo.launch.py
```

## What to do in Rviz

---

#### Thermal camera output from Python file
*In RViz UI:*
1. Click **Add**
2. Select **Image**
3. Set topic to:
    `/thermal/heatmap_image/image`

---
#### Front & rear camera
*In RViz UI:*
1. Click **Add**
2. Select **Image**
3. Set topic to:
    `/front/image/image`
4. Set topic to:
    `/rear/image/image`

To keep things clear, after adding the first camera *rename* them for clear view.

---
#### Lidar 2D mapping
1. set **Fixed Frame** to `map`
2. Click **Add**
3. Select **Image**
4. Set topic to:
    `/map/map`
5. Set topic to:
    `/scan/LaserScan`
6. Set topic to:
    `/odom/Odometry`
7. Set **Display Type** to:
    `/TF`
