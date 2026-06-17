# RTAB-Map 3D LiDAR Mapping
*09/06/2026*<br>
*Radeiaan Nandoe*

# Table of Contents
- [Context](#context)
- [Structure](#structure)
  - [Description](#description)
- [Reasoning](#reasoning)
- [Implementation](#implementation)
  - [1. ICP odometry](#1-icp-odometry)
  - [2. Topic bridges](#2-topic-bridges)
  - [3. Launch file](#3-launch-file)
  - [Conclusion](#conclusion)
- [Setup](#setup)
  - [Installation](#installation)
  - [Running files](#running-files)
  - [Visualizing map in RViz](#visualizing-map-in-rviz)
- [Advice](#advice)
- [Sources](#sources)



# Context
This folder was created for prototyping 3D LiDAR mapping using RTAB-Map inside a ROS2 + Gazebo environment. It builds upon the sensor and environment setup from [lidarSensorOmgeving](../LiDAR-sensor-environment/). The goal was to find a mapping algorithm that works with only a 3D LiDAR — no IMU and no RGB-D camera — to keep the simulation representative of the real FLIP hardware. After evaluating several options (see [Reasoning](#reasoning)) and consulting Bart Bozon who suggested ICP (iterative Closest Point), RTAB-Map with ICP odometry was selected as the approach that best matched these constraints. The first version which can be seen [here](./liveUpdatingRTABmap.mp4) could only show a live mapped environment as the robot moved and could not retain data points so a map could be generated. After trying [3d-cartographer](../3d-cartographer/) and [3D-Octomap](../3D-Octomap/) and booking no success the choice was made to continue with the live updating RTAB map and find a solution to build upon the scanned and mapped datapoints and save it so that Futurised could load this map in to interact with it for further analysis if necessary. That was relatively easily achieved by using ICP as a solution for providing odometry without using an IMU or RGB-D camera. Check this [video](./rtab3D.mp4) to see it yourself!

# Structure
```md
3D-Lidar-Mapping-RTAB/
├── databaseFiles/
│   ├── fullScan1.db
│   └── fullScan2.db
├── Screenshots/
│   ├── add.png
│   ├── fixedFrameOdom.png
│   ├── map.png
│   ├── markerArray.png
│   ├── odometry.png
│   ├── pointcloud2.png
│   └── tf.png
├── teleop/
│   ├── CMakeLists.txt
│   ├── CMakeTeleopGuide.md
│   ├── teleop
│   └── teleop.cc
├── HumanMappingTest.mp4
├── lidarRoomScan.sdf
├── liveUpdatingRTABmap.mp4
├── ReadME.md
├── rosBridge.yaml
├── rtab3D.mp4
├── rtabmap_gazebo.launch.py
├── rtabmap_mapping.rviz
└── viewMap.launch.py
```

## Description

- **databaseFiles/:** saved RTAB-Map `.db` map files from completed scans
- **Screenshots/:** RViz screenshots showing map output and display configuration
- **teleop/:** custom C++ teleop node and its CMake build files. This was shortly used for steering the robot up until the switch was made to diffdrive and eventually the automated driving via pathfinding.
- **HumanMappingTest.mp4:** recording of a mapping run with a human walking the environment
- **lidarRoomScan.sdf:** Gazebo world SDF used for prototype testing
- **liveUpdatingRTABmap.mp4:** the first working 3D mapping of RTAB even though it did not retain data and build a map
- **ReadME.md:** this file
- **rosBridge.yaml:** bridges Gazebo topics to ROS2 topics (including PointCloud2)
- **rtab3D.mp4:** recording of the successful 3D mapping output in RViz
- **rtabmap_gazebo.launch.py:** main launch file for the bridge, ICP odometry, RTAB-Map, and RViz
- **rtabmap_mapping.rviz:** RViz configuration for visualizing the 3D map which is automatically launched by rtabmap_gazebo.launch.py or viewMap.launch.py. This was aquired by exporting the rviz config after launching and setting up rviz.
- **viewMap.launch.py:** copy of the launch file for viewing a saved `.db` without overwriting it



# Reasoning
Several 3D mapping algorithms were considered before settling on RTAB-Map:

1. **Octomap** — a voxel-based 3D occupancy map. Useful as a map representation layer but not a full SLAM solution on its own; it requires an odometry source to be combined with.
2. **LIO-SAM** (LiDAR Inertial Odometry via Smoothing And Mapping) — requires an IMU, which was ruled out to stay true to the real hardware.
3. **LOAM** (LiDAR Odometry and Mapping) — a research-grade system with limited ROS2 support and complex setup.
4. **LeGO-LOAM** — a lightweight version of LOAM, but similarly constrained by poor ROS2 support.
5. **Cartographer** (Google) — supports both 2D and 3D mapping; tested in [3d-cartographer](../3d-cartographer/), but 3D mode required an IMU and had very little documentation. See [3d-cartographer's README](../3d-cartographer/README.md) for the full account.
6. **RTAB-Map** — a graph-based SLAM system with strong ROS2 support, capable of running on LiDAR-only setups via ICP odometry, and well-documented for Jazzy. This made it the best fit.



# Implementation
RTAB-Map itself was straightforward to integrate thanks to its ROS2 package (`rtabmap_ros`). The main challenges were producing reliable odometry without an IMU or RGB-D camera, and correctly bridging the Gazebo topics.

## 1. ICP odometry
To keep the simulation realistic, the robot has no IMU sensor and no RGB-D camera — matching the real hardware which only carries a 3D LiDAR. SLAM requires a continuous pose estimate (odometry) to track the robot's position and orientation. Gazebo wheel odometry drifts significantly due to wheel slip and simulation inaccuracies, making it unreliable for 3D mapping.

Two sensor-based alternatives were ruled out on realism grounds:
- **IMU** — measures raw acceleration and angular velocity. It cannot produce a pose estimate on its own without double-integrating its signal, which accumulates drift rapidly, and always needs to be fused with another source.
- **RGB-D camera** — can produce odometry via visual feature tracking (RGB-D odometry), but the real robot has no depth camera.

To solve this using only the LiDAR already on the robot, **ICP (Iterative Closest Point) odometry** was used. ICP aligns consecutive LiDAR point clouds to estimate the pose delta (translation + rotation) between frames directly from scan data, replacing wheel odometry without requiring any additional sensor.

## 2. Topic bridges
The [rosBridge.yaml](./rosBridge.yaml) file bridges the following Gazebo topics to ROS2:

### PointCloud2 (LiDAR data)
```yaml
- ros_topic_name: "/points2"
  gz_topic_name: "/lidar"
  ros_type_name: "sensor_msgs/msg/PointCloud2"
  gz_type_name: "gz.msgs.PointCloudPacked"
  direction: GZ_TO_ROS
```

### Odometry
```yaml
- ros_topic_name: "/odom"
  gz_topic_name: "/model/FLIP/odometry"
  ros_type_name: "nav_msgs/msg/Odometry"
  gz_type_name: "gz.msgs.Odometry"
  direction: GZ_TO_ROS
```

### TF, clock, and cmd_vel (carried over from previous setup)
```yaml
- ros_topic_name: "/tf"
  gz_topic_name: "/model/FLIP/tf"
  ros_type_name: "tf2_msgs/msg/TFMessage"
  gz_type_name: "gz.msgs.Pose_V"
  direction: GZ_TO_ROS

- ros_topic_name: "/clock"
  gz_topic_name: "/clock"
  ros_type_name: "rosgraph_msgs/msg/Clock"
  gz_type_name: "gz.msgs.Clock"
  direction: GZ_TO_ROS

- ros_topic_name: "/cmd_vel"
  gz_topic_name: "/model/FLIP/cmd_vel"
  ros_type_name: "geometry_msgs/msg/Twist"
  gz_type_name: "gz.msgs.Twist"
  direction: ROS_TO_GZ
```

## 3. Launch file
[rtabmap_gazebo.launch.py](./rtabmap_gazebo.launch.py) launches the full pipeline in one command:
- `ros_gz_bridge` — using the `rosBridge.yaml` topic config
- Static TF publisher — for the LiDAR sensor link (`FLIP/lidar_link/gpu_lidar`)
- `icp_odometry` node — computes odometry from consecutive LiDAR scans
- `rtabmap` node — performs graph-based SLAM and builds the 3D map
- `rviz2` — with the `rtabmap_mapping.rviz` config for live visualization

A `db_name` launch argument controls the output database file name so different runs can be saved separately.

**Note on the `static_laser_tf` topic:** when the LiDAR sensor has a link joined to the main robot model (as in the `workspace/models/` version), the topic must be updated from `FLIP/lidar_link/gpu_lidar` to `FLIP/3D_LidarSensor/lidar_sensor_link/gpu_lidar` in both [rtabmap_gazebo.launch.py](../../models/scripts/rtabmap_gazebo.launch.py) and [viewMap.launch.py](../../models/scripts/viewMap.launch.py). Keep this in mind when adapting the launch files to a modular robot model.

## Conclusion
RTAB-Map with ICP odometry successfully produced 3D maps of the simulated environment using only the 3D LiDAR, with no IMU or RGB-D camera required. This made it the most realistic and practical solution among all the options evaluated. The approach was subsequently integrated into the main workspace (`workspace/models/`) as the final 3D mapping pipeline for the FLIP robot.



# Setup
## Installation
1. Setup the container by following the steps in [setup](../../../setup/ROS2/README.md) to **update the container** and **add the necessary repositories** . You may also follow all the steps in that readme so you do not miss any setups.

2. Install RTAB-Map for ROS2 Jazzy:
```bash
source /opt/ros/jazzy/setup.bash
apt update
apt install -y ros-jazzy-rtabmap-ros
```

3. Verify the installation:
```bash
ros2 pkg prefix rtabmap_launch
ros2 pkg executables rtabmap_slam
ros2 pkg executables rtabmap_odom
```

You should see output like:
```
/opt/ros/jazzy
rtabmap_slam rtabmap
rtabmap_odom icp_odometry
rtabmap_odom rgbd_odometry
rtabmap_odom stereo_odometry
```


## Running files
### Prototype folder (3D-Lidar-Mapping-RTAB)

Open three terminals and run:

**Terminal 1 — start Gazebo**
```bash
cd /workspace/prototypes/3D-Lidar-Mapping-RTAB/
gz sim lidarRoomScan.sdf
```

**Terminal 2 — start bridge + ICP odometry + RTAB-Map**
```bash
cd /workspace/prototypes/3D-Lidar-Mapping-RTAB/
source /opt/ros/jazzy/setup.bash
ros2 launch rtabmap_gazebo.launch.py db_name:=nameYouWishToGiveTheDbFile.db
```

**Terminal 3 — drive the robot**
There are two ways you can drive the robot in this protoype since pathfinding has not been implemented yet for auto drive.

## teleop_twist_keyboard
The first way is by using `teleop_twist_keyboard` given that you have followed the installation steps in [ROS2/README.md](../../../setup/ROS2/README.md)
```bash
cd /workspace/prototypes/3D-Lidar-Mapping-RTAB/
source /opt/ros/jazzy/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/cmd_vel
```
Use the **key publisher** in Gazebo to drive the robot with the arrow keys if you have not generated the teleop file according to [CMakeTeleopGuide.md](./teleop/CMakeTeleopGuide.md).


If the bridge is not configured to remap `/cmd_vel` to `/model/FLIP/cmd_vel`, use:
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r /cmd_vel:=/model/FLIP/cmd_vel
```

## diffdrive gazebo plugin
To drive the robot using the `DiffDrive` plugin from gazebo itself two conditions must be met. You must have the DiffDrive plugin implemented in your .sdf file like:
```xml
      <!-- Diff Drive Plugin -->
      <plugin
      filename="gz-sim-diff-drive-system"
      name="gz::sim::systems::DiffDrive">

      <!-- all 6 wheels driven -->
      <left_joint>left_back_wheel_joint</left_joint>
      <left_joint>left_middle_wheel_joint</left_joint>
      <left_joint>left_front_wheel_joint</left_joint>

      <right_joint>right_back_wheel_joint</right_joint>
      <right_joint>right_middle_wheel_joint</right_joint>
      <right_joint>right_front_wheel_joint</right_joint>

      <wheel_separation>0.95</wheel_separation>
      <wheel_radius>0.242</wheel_radius>

      <topic>/model/FLIP/cmd_vel</topic>
      <odom_topic>/model/FLIP/odometry</odom_topic>
      <tf_topic>/model/FLIP/tf</tf_topic>

      <frame_id>odom</frame_id>
      <child_frame_id>chassis</child_frame_id>

      </plugin>
```

And secondly you must "turn on" [Key Publisher](./Screenshots/diffdrive/keyPublisher.png) in your running Gazebo environment through the [3 dots](./Screenshots/diffdrive/3dots.png) at the top right.

---

### Models folder (workspace/models)

**Terminal 1 — start Gazebo**
```bash
cd /workspace/models/gazebo
gz sim environment.sdf
```

**Terminal 2 — start bridge + ICP odometry + RTAB-Map**
```bash
cd /workspace/models/scripts
source /opt/ros/jazzy/setup.bash
ros2 launch rtabmap_gazebo.launch.py db_name:=nameYouWishToGiveTheDbFile.db
```

Use the **key publisher** in Gazebo to drive the robot with the arrow keys if necessary. It won't be necessary since pathfinding should so this automatically.


## Visualizing map in RViz
### Viewing a saved `.db` map file

If the RViz session from the launch file is closed, a saved map can be reloaded without overwriting it using `viewMap.launch.py`. This is a copy of `rtabmap_gazebo.launch.py` with the `-d` flag commented out on line 100, which prevents RTAB-Map from deleting and recreating the database on startup.

**Terminal 1 — launch RTAB-Map in view mode**
```bash
cd /workspace/prototypes/3D-Lidar-Mapping-RTAB
source /opt/ros/jazzy/setup.bash
ros2 launch viewMap.launch.py db_name:=nameOfDbFileYouWishToView.db
```

**Terminal 2 — publish the saved map**
```bash
cd /workspace/prototypes/3D-Lidar-Mapping-RTAB
source /opt/ros/jazzy/setup.bash
ros2 service call /rtabmap/rtabmap/publish_map rtabmap_msgs/srv/PublishMap "{global_map: true, optimized: true, graph_only: false}"
```

### RViz display setup (if the config file does not load)
| RViz display  | Topic / frame                     | Purpose                                     |
| ------------- | --------------------------------- | ------------------------------------------- |
| `TF`          | all frames                        | Check `map`, `odom`, `chassis`, LiDAR frame |
| `MapCloud`    | `/rtabmap/mapData`                | Main 3D RTAB-Map map                        |
| `PointCloud2` | `/points_colored`                 | Live colored LiDAR scan                     |
| `PointCloud2` | `/rtabmap/cloud_map` if available | RTAB-Map assembled cloud                    |
| `Map`         | `/rtabmap/grid_map` if available  | 2D occupancy map                            |
| `Odometry`    | `/odom`                           | Robot pose estimate from ICP odometry       |
| `Path`        | `/rtabmap/mapPath` if available   | Estimated trajectory                        |



# Advice
Among all the options evaluated, RTAB-Map is the recommended choice for 3D LiDAR mapping in a ROS2 + Gazebo setup. It is the only algorithm in this list that combines solid ROS2 Jazzy support, LiDAR-only operation via ICP odometry, and sufficient documentation to get running without dead ends. Octomap is useful as a representation layer on top of RTAB-Map if a voxel occupancy map is needed. The IMU-dependent options (LIO-SAM, Cartographer 3D) should only be considered if an IMU is part of the real hardware setup. Cartographer's 3D mode in particular suffers from sparse and incomplete documentation — see [3d-cartographer](../3d-cartographer/) for a full account of the dead ends encountered there. RTAB-Map was ultimately integrated into the main workspace as the final mapping solution for FLIP, which reflects how well it performed relative to the alternatives.



# Sources
- RTAB-Map ROS2 documentation — http://wiki.ros.org/rtabmap_ros
- ChatGPT — RTAB-Map https://chatgpt.com/share/6a01f66b-6abc-83eb-a51f-6d78ea842b00
- ChatGPT — RTAB 3D mapping https://chatgpt.com/share/6a148d3a-b9c4-83eb-b04a-9cbd8caceb15
- ChatGPT — integration problems https://chatgpt.com/c/6a189349-6be0-83eb-a72c-b77ecc5af33a
- *Navigation in ROS2* by Hochschule Hamm-Lippstadt https://wiki.hshl.de/wiki/index.php/Navigation_in_ROS2
- ICP odometry in rtabmap_ros — https://github.com/introlab/rtabmap_ros
- 9、RTAB-Map 3D mapping navigation https://www.yahboom.net/public/upload/upload-html/1638953184/RTAB-Map%203D%20mapping%20navigation.html
- ROS.org https://wiki.ros.org/rtabmap_ros
- rtabmap_odom https://wiki.ros.org/rtabmap_odom#icp_odometry
- RTAB rviz https://wiki.ros.org/rtabmap_viz#rtabmap_viz-1
- [3D-mapping Research](../../../docs/onderzoek/3D-mapping/links.md)