# Cartographer
*09/06/2026*<br>
*Radeiaan Nandoe*

# Table of Contents
- [Context](#context)
- [Structure](#structure)
  - [Description](#description)
- [Reasoning](#reasoning)
- [Implementation](#implementation)
  - [1. Vertical scan code block](#1-vertical-scan-code-block)
  - [2. Topic bridges](#2-topic-bridges)
  - [3. Lua file](#3-lua-file)
  - [Conclusion](#conclusion)
- [Setup](#setup)
  - [Running files](#running-files)
  - [Installation](#installation)
  - [Visualizing map in RViz](#visualizing-map-in-rviz)
- [Advice](#advice)
- [Sources](#sources)



# Context
This folder builds upon [2d-cartographer-demo](../2d-cartographer-demo/). Since `2d-cartographer-demo` was used for testing the 2D-mapping this folder was created for transitioning the 2D-mapping files to 3D-mapping files.

# Structure
```md
3d-cartographer/
├── flip/
│   ├── model.config
│   └── model.sdf
├── my_robot_3d.lua
├── README.md
├── room-v2.sdf
├── rosBridge.yaml
└── 3dCartographer.launch.py
```

## Description

- **model.config:** model metadata for the FLIP robot
- **model.sdf:** SDF model definition for the FLIP robot (with 3D LiDAR config)
- **my_robot_3d.lua:** Lua script for building a 3D map
- **README.md:** this file
- **room-v2.sdf:** copy of the environment SDF for testing without modifying the main file
- **rosBridge.yaml:** bridges Gazebo topics to ROS2 topics
- **3dCartographer.launch.py:** launch file for ros_gz_bridge, static TF publishers, and cartographer_node




# Reasoning
After achieving partial success with [RTAB-mapping](../3D-Lidar-Mapping-RTAB/) ( please visit RTAB-mapping's [ReadME.md](../3D-Lidar-Mapping-RTAB/ReadME.md) for more info) and reaching a few blockages shortly after that Django and I brainstormed about which alternative should be used. After googling `ros2 mapping algorithms` and coming across [8.ROS2_Cartographer mapping algorithm](https://www.yahboom.net/public/upload/upload-html/1699598898/8.ROS2_Cartographer%20mapping%20algorithm.html) the decision was made that Cartographer should be used since it can be implemented for both 2D and 3D-mapping while taking the real hardware implementations of FLIP into account.


# Implementation
Even though being successful in [2d-cartographer-demo](../2d-cartographer-demo/) with generating a 2D map of the simulated environment, producing a 3D map using Cartographer proved difficult. The reason for this conclusion was because there was apparently also an IMU sensor necessary which went against keeping the implementation realistic (even though it was implemented to test and verify the functionality of Cartographer's 3D-mapping) and also mainly because even though there was documentation on 2D-mapping using Cartographer, there was very little documentation on how to implement 3D-mapping. So based on the little documentation found, changes were made to the following accordingly:

## 1. Vertical scan code block
In [flip/model.sdf](./flip/model.sdf) the following code block was added to the `gpu_lidar` sensor as vertical scans are required for 3D scanning:
```xml
            <vertical>
              <samples>12</samples>
              <resolution>1</resolution>
              <min_angle>-0.261779</min_angle>
              <max_angle>0.261779</max_angle>
            </vertical>
```

An IMU sensor was also added to the `chassis` link of the model, as Cartographer's 3D mode requires IMU data:
```xml
      <sensor name="imu_sensor" type="imu">
        <always_on>1</always_on>
        <update_rate>20</update_rate>
        <visualize>true</visualize>
        <topic>imu</topic>
      </sensor>
```


## 2. Topic bridges
In the [rosBridge.yaml](./rosBridge.yaml) file the following was updated:
### Lidar topic & data
From
```yaml
- ros_topic_name: "/scan"
  gz_topic_name: "/lidar"
  ros_type_name: "sensor_msgs/msg/LaserScan"
  gz_type_name: "gz.msgs.LaserScan"
  direction: GZ_TO_ROS
```

to 

```yaml
# CHANGED: was LaserScan, now PointCloud2 for 3D mapping
- ros_topic_name: "/points2"
  gz_topic_name: "/lidar"
  ros_type_name: "sensor_msgs/msg/PointCloud2"
  gz_type_name: "gz.msgs.PointCloudPacked"
  direction: GZ_TO_ROS
```


### Added imu data topic block for testing success with IMU
```yaml
- ros_topic_name: "/imu"
  gz_topic_name: "/imu"
  ros_type_name: "sensor_msgs/msg/Imu"
  gz_type_name: "gz.msgs.IMU"
  direction: GZ_TO_ROS
```

### Uncommented odom topic bridge as odometry was also necessary for cartographer
```yaml
- ros_topic_name: "/odom"
  gz_topic_name: "/model/FLIP/odometry"
  ros_type_name: "nav_msgs/msg/Odometry"
  gz_type_name: "gz.msgs.Odometry"
  direction: GZ_TO_ROS
```

### Unchanged bridges carried over from the 2D demo
The following bridges were already present and were not modified:
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

## 3. Lua file
In [my_robot_3d.lua](./my_robot_3d.lua) `num_point_clouds` was set to 1 (enabled) so that point cloud data is used, and `num_laser_scans` was set to 0 (disabled) so scan data is not used to prevent conflicts.
```lua
num_laser_scans = 0,
```

The following was also altered from 

```lua
MAP_BUILDER.use_trajectory_builder_2d = true
TRAJECTORY_BUILDER_2D.min_range = 0.3
TRAJECTORY_BUILDER_2D.max_range = 8.0
TRAJECTORY_BUILDER_2D.missing_data_ray_length = 5.0
TRAJECTORY_BUILDER_2D.use_imu_data = false
TRAJECTORY_BUILDER_2D.use_online_correlative_scan_matching = true
-- TRAJECTORY_BUILDER_2D.motion_filter.max_angle_radians = math.rad(0.1)
-- TRAJECTORY_BUILDER_2D.motion_filter.max_distance_meters = 0.2

return options
```


to 

```lua
MAP_BUILDER.use_trajectory_builder_2d = false  -- switch to 3D
MAP_BUILDER.use_trajectory_builder_3d = true

TRAJECTORY_BUILDER_3D.min_range = 0.3
TRAJECTORY_BUILDER_3D.max_range = 8.0
TRAJECTORY_BUILDER_3D.num_accumulated_range_data = 1

-- IMU is required for 3D cartographer
TRAJECTORY_BUILDER_3D.use_online_correlative_scan_matching = false


return options
```


## Conclusion
After multiple tweaks and testing based on little and poor documentation, the choice was made to try to improve [RTAB-3D-mapping](../3D-Lidar-Mapping-RTAB/) which was already partially functional instead of wasting time on a prototype which didn't have sufficient documentation and examples.



# Setup
## Installation
1. Setup the container by following the steps in [setup](../../../setup/ROS2/README.md) to **update the container** and **add the necessary repositories** . You may also follow all the steps in that readme so you do not miss any setups. 

2. Install the necessary packages by running:
```bash
apt update && apt install  python3-rosdep  ros-jazzy-cartographer ros-jazzy-cartographer-ros  ros-jazzy-cartographer-rviz -y
```


## Running files
Open terminals and run:

1. One-liner
```bash
# Change directory
cd /workspace/prototypes/3d-cartographer/
# Launch Gazebo simulation
gz sim room-v2.sdf &
# Source ROS2
source /opt/ros/jazzy/setup.bash
# Launch .launch.py file
ros2 launch 3dCartographer.launch.py &
```

2. Give command for test movement and mapping
```bash
gz topic -t "/model/FLIP/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.5}, angular: {z: 0.05}"
```


## Visualizing map in RViz
**Note:** `cartographer_occupancy_grid_node` is not launched for the 3D setup (it only works with 2D submaps), so the `/map` topic is **not** available. Use the topics below instead.

Open a terminal and run:
1. Source the environment:
```bash
source /opt/ros/jazzy/setup.bash
```

2. Open RViz:
```bash
rviz2
```

3. In RViz click `Add` and add:
   - **PointCloud2** with topic `/points2` — shows the raw 3D LiDAR data
   - **MarkerArray** (or **SubmapList**) with topic `/submap_list` — shows Cartographer's 3D submaps


# Advice
It would have been ideal to use Cartographer to do both 2D and 3D-mapping for our project but it was not worth the time and effort to try to get Cartographer working as there is little documentation available. This is not entirely true as there is some documentation on 3D-mapping using Cartographer but the limitations are completeness of said documentation or incompatibility with the Gazebo version used for this project. If you like a challenge and wish to do so anyway then good luck! The final advice given would be to check what version has the most documentation online for your specific project before using that version for the project. Or use some other simulation software than Gazebo.



# Sources
- cartographer-project/cartographer_ros by [wally-the-cartographer](https://github.com/wally-the-cartographer) and [gaschler](https://github.com/cartographer-project/cartographer_ros/commits?author=gaschler) https://github.com/cartographer-project/cartographer_ros/blob/master/cartographer_ros/configuration_files/backpack_3d.lua
- *Navigation in ROS2* by Hochschule Hamm-Lippstadt https://wiki.hshl.de/wiki/index.php/Navigation_in_ROS2
- *Cartographer* by Cartographer-project https://github.com/cartographer-project/
- *Building Maps Using Google Cartographer and the OS1 Lidar Sensor* - By Wil Selby
Oct 09, 2019 https://ouster.com/insights/blog/building-maps-using-google-cartographer-and-the-os1-lidar-sensor
- 8.ROS2_Cartographer mapping algorithm https://www.yahboom.net/public/upload/upload-html/1699598898/8.ROS2_Cartographer%20mapping%20algorithm.html
- cartographer_ros - bochen87 https://github.com/cartographer-project/cartographer_ros
- The International Archives of the Photogrammetry, Remote Sensing and Spatial Information Sciences, Volume XLII-2/W3, 2017 3D Virtual Reconstruction and Visualization of Complex Architectures, 1–3 March 2017, Nafplio, Greece https://isprs-archives.copernicus.org/articles/XLII-2-W3/543/2017/isprs-archives-XLII-2-W3-543-2017.pdf
- Setting Up Cartographer with ROS2 and Gazebo for SLAM Using a LIDAR Sensor Plugin Without Odometry, Nex-dynamics robot, Jun 29, 2024 https://www.youtube.com/watch?v=CeaW8WG7Z8g
- [3D-mapping Research](../../../docs/onderzoek/3D-mapping/links.md)