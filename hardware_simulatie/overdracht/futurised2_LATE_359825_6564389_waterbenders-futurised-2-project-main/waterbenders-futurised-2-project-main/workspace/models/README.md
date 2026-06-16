# Product FLIP
*11/06/2026*  
*Maud Waasdorp*

# Table of Contents

- [Product FLIP](#product-flip)
- [Table of Contents](#table-of-contents)
- [Project Overview](#project-overview)
- [Folder Structure](#folder-structure)
- [ROS Packages](#ros-packages)
- [Scripts](#scripts)
- [Mapping Databases](#mapping-databases)
- [Gazebo Environment](#gazebo-environment)
  - [Obstacles](#obstacles)
  - [FLIP Robot](#flip-robot)
  - [Plugins](#plugins)
- [Running the Simulation](#running-the-simulation)
  - [To run the complete simulation:](#to-run-the-complete-simulation)
    - [1. Open terminal in VS Code](#1-open-terminal-in-vs-code)
    - [2. Start the Docker container](#2-start-the-docker-container)
    - [3. Navigate to the simulation folder](#3-navigate-to-the-simulation-folder)
    - [4. Source ROS2](#4-source-ros2)
    - [4. Build Colcon](#4-build-colcon)
    - [6. Source the workspace](#6-source-the-workspace)
    - [7. Launch the simulation](#7-launch-the-simulation)
- [Simulation Architecture](#simulation-architecture)


# Project Overview
This repository contains the final simulation environment for **Product FLIP**.

The project is built around a ROS2 + Gazebo simulation where the FLIP robot operates inside a custom virtual environment. The simulation contains the robot model, environment, sensors, ROS2 communication nodes, and additional processing scripts required for tasks such as:

- Robot simulation
- Sensor visualization
- LiDAR mapping
- Camera processing
- Thermal image processing
- SLAM and navigation experiments
- Fire detection
- Object detection
- Human detection

The simulation is launched through the ROS2 launch file:
```
simulation.launch.py
```

*This file starts the required Gazebo environment, loads the robot, starts the sensor plugins, and connects the simulation to ROS2.*


# Folder Structure

The main structure of this project is:
```
models/
├── ros/
├── scripts/
├── databases/
├── environment.sdf
├── Obstacles/
├── flip/
└── plugins/
```

Each folder has a specific purpose within the simulation.


# ROS Packages
Location:
```
/ros
```

The `ros` folder contains all custom ROS2 packages used by the simulation.

These packages are built using **Colcon** and provide the communication layer between Gazebo, sensors, and custom processing nodes.

The packages can contain:

- ROS2 nodes
- Publishers and subscribers
- Launch files
- Configuration files
- Custom robot behavior

Before running ROS nodes, the workspace needs to be built:
```bash
colcon build
```

After building, the workspace must be sourced:
```bash
source install/setup.bash
```

The ROS packages allow the simulation to communicate through topics such as:

- Camera images
- LiDAR scans
- Heatmap images
- Detection images
- Mapping data


# Scripts
Location:
```
/scripts
```

The `scripts` folder contains Python scripts used for additional processing outside of the default ROS/Gazebo functionality.

Examples of tasks performed by scripts:

- Processing camera streams
- Generating thermal camera outputs
- Object detection
- Human detection
- Fire detection
- Publishing processed sensor data
- Running custom algorithms

Python scripts may require the **virtual environment** to be activated:
```bash
source /workspace/venv/bin/activate
```

Example:
```bash
python script_name.py
```


# Mapping Databases
Location:
```
/databases
```

This folder contains saved mapping databases.

The simulation uses mapping tools such as SLAM to create and store environmental information.

The database files can contain:

- 3D point cloud information
- Robot poses
- Mapping data
- Sensor observations

*These files allow previous mapping sessions to be restored without needing to rebuild the entire map.*

# Gazebo Environment
Main file:
```
environment.sdf
```

The `.sdf` file defines the Gazebo world.

It contains the complete simulation environment including:

- Environment layout
- Walls and obstacles
- Lighting
- Physics settings
- Sensor placement
- Robot spawn location

*Gazebo loads this file to create the virtual world in which the FLIP robot operates.*

The environment can be started manually using:
```bash
gz sim environment.sdf
```


## Obstacles
Location:
```
/Obstacles
```

This folder contains all additional Obstacles used inside the simulation environment.

Obstacles can represent:
- Obstacles
- Furniture
- Test Obstacles
- Environmental elements

Each object normally contains its own Gazebo model description, including:
- Mesh files
- Collision geometry
- Visual appearance
- Physical properties

*Obstacles can be added to `environment.sdf` to extend the simulation world.*

## FLIP Robot
Location:
```
/flip
```

The `flip` folder contains the complete robot model.

This includes:
- Robot description files
- Visual meshes
- Collision models
- Sensor mounting locations
- Robot configuration

The FLIP model is loaded into Gazebo and connected to ROS2.

*The robot contains multiple sensors, which communicate through ROS2 topics.*


## Plugins
Location:
```
/plugins
```

The plugins folder contains custom Gazebo plugins used for the sensors.

**Plugins are responsible for connecting Gazebo simulation data to ROS2.**

These include:
- Camera plugins
- Thermal camera plugins
- LiDAR plugins
- Sensor bridges
- Logical Audio Sensor plugins

The plugins handle tasks such as:
- Reading simulated sensor data
- Publishing messages
- Converting Gazebo messages to ROS2 messages
- Providing sensor updates during simulation


# Running the Simulation
Before running the simulation, please check out the [setup](../../setup/README.md) guide to follow the needed instructions to setup the workspace environment.

## To run the complete simulation:
### 1. Open terminal in VS Code

Shortcut:
```bash
Ctrl + Shift + ~
```


### 2. Start the Docker container
Run:
```bash
./rungazebo.ps1
```

*This starts the configured Gazebo/ROS2 container. See [here](../../docker/setup/container-start/README.md) for explanation of this file*

### 3. Navigate to the simulation folder
Inside the container:
```bash
cd /workspace/models
```


### 4. Source ROS2
```bash
source /opt/ros/jazzy/setup.bash
```

### 4. Build Colcon
```bash
colcon build
```

**Note:**
It is possible that using old install artifacts from colcon can cause the simulation to collapse/self-terminate when trying to run it. If you encounter said problem, try removing the old installs made by colcon in the container and follow [step 3](#3-navigate-to-the-simulation-folder) to quickly rebuild new packages and run the simulation after. 

The command for removing old install artifacts along with its folders created is:
```bash
rm -rf install/ build/ log/
```

### 6. Source the workspace
```bash
source install/setup.bash
```

### 7. Launch the simulation
```bash
ros2 launch simulation.launch.py
```


**After launching, Gazebo will open with the FLIP robot inside the environment and all configured sensors will start publishing data.**


# Simulation Architecture

The simulation works through the following flow:

```
Gazebo Environment
        |
        |
        v
 FLIP Robot + Sensors
        |
        |
        v
 Gazebo Plugins
        |
        |
        v
 ROS2 Topics
        |
        |
        +----------------+
        |                |
        v                v
 ROS Packages       Python Scripts
        |
        |
        v
 Mapping / Visualization / Processing
```

**Notes:**
- Gazebo is responsible for physics and simulation.
- Plugins connect the simulated hardware to ROS2.
- ROS packages handle communication and robot functionality.
- Python scripts provide additional processing and AI-based functionality.
- Together these components create the complete FLIP simulation environment.