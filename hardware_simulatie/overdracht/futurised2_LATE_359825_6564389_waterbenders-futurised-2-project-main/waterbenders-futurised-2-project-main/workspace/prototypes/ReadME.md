## Context
This is where individual features were built and tested in isolation before integration into the main simulation. Each subfolder is a standalone prototype with its own README documenting the reasoning behind it, implementation details, usage instructions, advice for future developers, and contributor information. Prototypes that proved successful were later integrated into the models folder.


## Overview
Below is a table for a clear overview of who helped with which prototype, if that prototype was implemented and short notes on what that prototype does.
| Prototype | Contributor | Implemented | Notes|
| --------- | ----------- | ----------- | ---- |
| [2d-cartographer-demo](./2d-cartographer-demo/) | Django Manders | No | 2D mapping using Cartographer, used as a basis for implementing 3d-cartographer mapping |
| [3d-cartographer](./3d-cartographer/) | Radeiaan Nandoe | No | 3D mapping using Cartographer, explored as an alternative mapping approach|
| [3D-Lidar-Mapping-RTAB](./3D-Lidar-Mapping-RTAB/) | Radeiaan Nandoe | **Yes** | 3D mapping using RTAB-Map — the main LiDAR 3D-mapping implementation |
| [3D-Octomap](./3D-Octomap/) | Radeiaan Nandoe | No | 3D occupancy mapping using OctoMap, explored as an alternative mapping approach |
| [airpressure-sensor](./airpressure-sensor/) | Freya van den Berg | **Yes** | Air pressure sensor integration for detecting different air pressures in the environment |
| [altimeter](./altimeter/) | Sarah Gbagi | No | Altimeter sensor integration for altitude measurement |
| [camera](./camera/) | Django Manders | **Yes** | Ultra-wide camera implementation for a live-feed of the environment |
| [dijkstra-algorithm](./dijkstra-algorithm/) | Sarah Gbagi | **Yes** | Dijkstra pathfinding algorithm as a back-up algorithm for autonomous navigation |
| [environment-with-obstacles](./environment-with-obstacles/) | Radeiaan Nandoe, Django Manders | **Yes** | Test simulation environment with obstacles, used for testing other prototypes |
| [frontier-clusters-demo](./frontier-clusters-demo/) | Django Manders | **Yes** | Frontier-based exploration clustering for autonomous pathfinding and environment exploration |
| [LiDAR-sensor-environment](./LiDAR-sensor-environment/) | Radeiaan Nandoe | **Yes** | LiDAR sensor environment setup used for testing and developing LiDAR integration |
| [logical-audio-sensor](./logical-audio-sensor/) | Sarah Gbagi | **Yes** | Logical audio sensor integration for receiving and sending audio data |
| [object-detection-opencv](./object-detection-opencv/) | Maud Waasdorp, Radeiaan Nandoe | **Yes** | Object detection using OpenCV |
| [object-human-detection](./object-human-detection/) | Maud Waasdorp, Radeiaan Nandoe | **Yes** | Combined object & human detection implementation |
| [path-finding-demo](./path-finding-demo/) | Django Manders | **Yes** | Autonomous pathfinding demo, used as a basis for the final pathfinding implementation |
| [thermal-camera](./thermal-camera/) | Maud Waasdorp | **Yes** | Thermal camera implementation for visualizing temperatures inside an environment |
| [YOLO-human-detection](./YOLO-human-detection/) | Maud Waasdorp, Radeiaan Nandoe | **Yes** | Human detection using the YOLO model |

# Note
Some of the paths in these prototypes may be broken since we were continuously working on and developing our project. We have tried to clean up all the mess before submission but it is still possible that we missed some things so please keep that in mind.