# Cartographer
*13/06/2026*<br>
*Django Manders*

# Table of Contents
- [Context](#context)
- [Structure](#structure)
  - [Description](#description)
- [Reasoning](#reasoning)
- [Implementation](#implementation)
  - [1. Lua file](#1-lua-file)
  - [2. Topic bridges](#2-topic-bridges)
  - [3. 2dCartographer.launch.py](#3-2dcartographerlaunchpy)
  - [Conclusion](#conclusion)
- [Setup](#setup)
  - [Running files](#running-files)
  - [Installation](#installation)
  - [Visualizing map in RViz](#visualizing-map-in-rviz)
- [Advice](#advice)
- [Sources](#sources)



# Context
This is the folder used prior to [3d-cartographer](../3d-cartographer/) to test cartographer's 2D-mapping so Cartographer's mapping functionality and performance could be evaluated which was then used to determine if cartographer would still be used for 3D-mapping.

# Structure
```md
2d-cartographer-demo/
├── flip/
│   ├── model.config
│   └── model.sdf
├── 2dCartographer.launch.py
├── my_robot_2d.lua
├── README.md
├── room-v2.sdf
└── rosBridge.yaml
```

## Description

- **model.config:** model metadata for the FLIP robot
- **model.sdf:** SDF model definition for the FLIP robot (with GPU LiDAR sensor)
- **my_robot_2d.lua:** Lua configuration script for Cartographer 2D SLAM
- **README.md:** this file
- **room-v2.sdf:** copy of the environment SDF for testing without modifying the main file
- **rosBridge.yaml:** bridges Gazebo topics to ROS2 topics
- **2dCartographer.launch.py:** launch file for ros_gz_bridge, static TF publishers, cartographer_node, and cartographer_occupancy_grid_node




# Reasoning
After achieving partial success with [RTAB-mapping](../3D-Lidar-Mapping-RTAB/) ( please visit RTAB-mapping's [ReadME.md](../3D-Lidar-Mapping-RTAB/ReadME.md) for more info) and reaching a few blockages shortly after that Django and I brainstormed about which alternative should be used. After googling `ros2 mapping algorithms` and coming across [8.ROS2_Cartographer mapping algorithm](https://www.yahboom.net/public/upload/upload-html/1699598898/8.ROS2_Cartographer%20mapping%20algorithm.html) the decision was made that Cartographer should be used since it can be implemented for both 2D and 3D-mapping while taking the real hardware implementations of FLIP into account.


# Implementation
This 2D-mapping was implemented using various [sources](#sources) online. There were different files needed for a functional 2D cartographer such as seen above in the [structure](#structure). The main addition was my_robot_2d.lua and the main files changed/adjusted were: 2dCartographer.launch.py which was a copy of [/lidarSensorOmgeving/slam_gazebo.launch.py](../lidarSensorOmgeving/slam_gazebo.launch.py) and rosBridge.yaml which is located at [lidarSensorOmgeving/rosBridge.yaml](../lidarSensorOmgeving/rosBridge.yaml):


## 1. Lua file
In [my_robot_2d.lua](./my_robot_2d.lua) Cartographer is configured for 2D SLAM. The key settings are:
- `MAP_BUILDER.use_trajectory_builder_2d = true` — enables the 2D trajectory builder instead of 3D
- `num_laser_scans = 1`, `num_point_clouds = 0` — uses a single 2D laser scan input (the `/scan` topic) rather than 3D point clouds
- `tracking_frame = "chassis"`, `published_frame = "chassis"` — Cartographer tracks and publishes pose relative to the robot chassis frame
- `use_imu_data = false` — no IMU available, scan matching handles pose estimation
- `use_online_correlative_scan_matching = true` — improves robustness by correlating scans before graph optimization
- `min_range = 0.3`, `max_range = 8.0` — valid LiDAR range in metres for this environment


## 2. Topic bridges
In the [rosBridge.yaml](./rosBridge.yaml) file four Gazebo–ROS2 bridges are defined:

| ROS2 topic | Gazebo topic | Direction |
|---|---|---|
| `/scan` | `/lidar` | GZ → ROS (LaserScan) |
| `/tf` | `/model/FLIP/tf` | GZ → ROS (TFMessage) |
| `/clock` | `/clock` | GZ → ROS (Clock) |
| `/cmd_vel` | `/model/FLIP/cmd_vel` | ROS → GZ (Twist) |

The `/scan` bridge feeds LiDAR data into Cartographer. The `/tf` bridge forwards the robot's pose transforms from Gazebo. The `/clock` bridge keeps ROS2 nodes in sync with simulation time. The `/cmd_vel` bridge allows sending velocity commands to the robot from ROS2.


## 3. 2dCartographer.launch.py
In [2dCartographer.launch.py](./2dCartographer.launch.py) four nodes are launched:

1. **ros_gz_bridge** (`parameter_bridge`) — loads the rosBridge.yaml config to start all four topic bridges described above
2. **static_transform_publisher** — publishes a fixed TF between `chassis` and `FLIP/chassis/gpu_lidar` (offset: x=0.6, z=0.3) so Cartographer knows the LiDAR position relative to the robot body
3. **cartographer_node** — runs Google Cartographer using `my_robot_2d.lua` for 2D SLAM; `use_sim_time: True` keeps it in sync with Gazebo
4. **cartographer_occupancy_grid_node** — converts Cartographer's submaps into a standard `/map` occupancy grid topic for visualization in RViz


## Conclusion
After multiple tweaks and testing based on the found [sources](#sources) Cartographer's 2D-mapping was up and running, producing a live occupancy grid map of the simulated environment.



# Setup
## Installation
1. Setup the container by following the steps in [setup](../../../setup/ROS2/README.md) to **update the container** and **add the necessary repositories** . You may also follow all the steps in that readme so you do not miss any setups.

2. Install the necessary packages by running:
```bash
```bash
apt update && apt install  python3-rosdep  ros-jazzy-cartographer ros-jazzy-cartographer-ros  ros-jazzy-cartographer-rviz -y
```


## Running files
Open terminals and run:

1. One-liner
```bash
# Change directory
cd /workspace/prototypes/2d-cartographer-demo/
# Launch Gazebo simulation
gz sim room-v2.sdf &
# Source ROS2
source /opt/ros/jazzy/setup.bash
# Launch .launch.py file
ros2 launch 2dCartographer.launch.py &
```

2. Give command for test movement and mapping
```bash
gz topic -t "/model/FLIP/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.5}, angular: {z: 0.05}"
```


## Visualizing map in RViz
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
   - **Map** with topic `/map` — shows the live 2D occupancy grid produced by Cartographer
   - **LaserScan** with topic `/scan` — shows the raw 2D LiDAR data
   - **TF** — visualizes the coordinate frames (chassis, map, odom)


# Advice
It would have been ideal to use Cartographer to do both 2D and 3D-mapping for our project but it was not worth the time and effort to try to get Cartographer working as there is little documentation available. This is not entirely true as there is some documentation on 3D-mapping using Cartographer but the limitations are completeness of said documentation or incompatibility with the Gazebo version used for this project. If you like a challenge and wish to do so anyway then good luck! The final advice given would be to check what version has the most documentation online for your specific project before using that version for the project. Or use some other simulation software than Gazebo.



# Sources
- 2D Mapping using Google Cartographer and RPLidar with Raspberry Pi by Robotics Weekends, Oct 12, 2020 https://medium.com/robotics-weekends/2d-mapping-using-google-cartographer-and-rplidar-with-raspberry-pi-a94ce11e44c5
- Cartographer Map Building https://www.waveshare.com/wiki/Cartographer_Map_Building
- *Lua configuration reference documentation* by Google https://google-cartographer-ros.readthedocs.io/en/latest/configuration.html
- *Navigation in ROS2* by Hochschule Hamm-Lippstadt https://wiki.hshl.de/wiki/index.php/Navigation_in_ROS2
- *Cartographer* by Cartographer-project https://github.com/cartographer-project/
- *Building Maps Using Google Cartographer and the OS1 Lidar Sensor* - By Wil Selby, Oct 09, 2019 https://ouster.com/insights/blog/building-maps-using-google-cartographer-and-the-os1-lidar-sensor
- 8.ROS2_Cartographer mapping algorithm https://www.yahboom.net/public/upload/upload-html/1699598898/8.ROS2_Cartographer%20mapping%20algorithm.html
- cartographer_ros - bochen87 https://github.com/cartographer-project/cartographer_ros
- The International Archives of the Photogrammetry, Remote Sensing and Spatial Information Sciences, Volume XLII-2/W3, 2017 3D Virtual Reconstruction and Visualization of Complex Architectures, 1–3 March 2017, Nafplio, Greece https://isprs-archives.copernicus.org/articles/XLII-2-W3/543/2017/isprs-archives-XLII-2-W3-543-2017.pdf
- Setting Up Cartographer with ROS2 and Gazebo for SLAM Using a LIDAR Sensor Plugin Without Odometry, Nex-dynamics robot, Jun 29, 2024 https://www.youtube.com/watch?v=CeaW8WG7Z8g
