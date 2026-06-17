# Project Team WaterBenders
*15/06/2026*<br>

Team Waterbenders<br>
Hogeschool Utrecht<br>
Futurised 

# Table of Contents
- [Project Team WaterBenders](#project-team-waterbenders)
- [Table of Contents](#table-of-contents)
- [Project authors](#project-authors)
- [Connections](#connections)
- [Repository Structure](#repository-structure)
- [Important Folders](#important-folders)
  - [models folder](#models-folder)
  - [prototypes folder](#prototypes-folder)
- [Introduction](#introduction)
- [Assignment](#assignment)
  - [Main implementations](#main-implementations)
  - [Other implementations](#other-implementations)
  - [Software](#software)
- [Futurised](#futurised)
- [Instructions](#instructions)
  - [Step-by-step](#step-by-step)
- [Conclusion and Recommendations](#conclusion-and-recommendations)

# Project authors
- **Django Manders:** Software Developer <br>
  - worked on: Global structure of Pathfinding, Camera
- **Freya van den Berg:** Software Developer <br>
  - worked on: Airpressure sensor, Explosion detection, Object detection
- **Maud Waasdorp:** Software Developer <br>
  - worked on: Object detection, Thermal camera, Camera, Fire detection, Human detection
- **Radeiaan Nandoe:** Technical Lead <br>
  - worked on: LiDAR implentation, 2D and 3D mapping, Object detection, Human detection
- **Sarah Gbagi:** Scrum Master <br>
  - worked on: Logical audio sensor, Pathfinding Dijkstra Algorithm

All of the authors have worked on the structure and documentation of this Repository.

# Connections
- Robbert Heinecke
- Juliette Kraal
- Bart Bozon
- Hasan Kurt



---

# Repository Structure

Below is an overview of the folder structure of this repository.

> Each prototype in [`/workspace/prototypes/`](/workspace/prototypes/) has its own detailed README with implementation details, usage instructions, advice for future developers, and notes on who contributed to it.

```
waterbenders-futurised-2-project/
│
├── docker/                                        # Everything needed to set up the Docker environment
│   └── setup/
│       ├── container-creation/                    # Instructions for creating the Docker container (Windows & Ubuntu)
│       ├── container-start/                       # Instructions for starting the container
│       ├── container-venv/                        # Instructions for setting up the Python virtual environment
│       └── using-cuda/                            # Optional: instructions for enabling CUDA GPU support
│
├── docs/                                          # Project documentation
│   ├── flip/                                      # Specifications and technical details of the FLIP robot
│   ├── images/                                    # Some images used throughout the documentation
│   ├── onderzoek/                                 # Research documents made and referred to in some README's
│   │   ├── 3D-mapping/                            # Research on 3D mapping techniques
│   │   ├── object-herkenning/                     # Research on object recognition
│   │   └── ROS2/                                  # Research on ROS2
│   ├── uml/                                       # UML diagrams
│   │   ├── activity-diagrammen/                   # Activity diagrams
│   │   └── use-case-diagram/                      # Use-case diagrams
│   └── Ontwikkeldocument-futurised-2.md           # Development document
│
├── img/                                           # Image used in the root README
│
├── setup/                                         # Setup guides for the simulation environment
│   ├── ROS2/                                      # Installing ROS2
│   ├── colcon/                                    # Building Colcon packages
│   ├── running-scripts/                           # Running individual Python scripts
│   └── RViz-visualisation/                        # Visualizing the simulation in RViz
│
└── workspace/                                     # Main working directory for the simulation
    ├── models/                                    # Gazebo/ROS simulation models and (launch)scripts
    │   ├── gazebo/                                # Gazebo world and model files
    │   ├── ros/                                   # ROS2 packages, nodes, bridges, etc.
    │   └── scripts/                               # Python (launch) scripts used in the simulation
    │
    └── prototypes/                                # All prototypes built during the project. Each folder has its own README with details, advice, implementation notes, and contributors.
        │
        ├── 2d-cartographer-demo/                  # 2D mapping prototype using Cartographer, used as a basis for implementing 3d-cartographer mapping
        ├── 3d-cartographer/                       # 3D mapping using Cartographer, explored as an alternative approach
        .
        .
        .
```
---


# Important Folders
The most important folders besides the [setup folder](/setup/) and the [docker folder](/docker/) are the folders where our main implementation and prototypes reside. These are:

## [models folder](/workspace/models/) 
This is the folder containing the final, integrated simulation environment for the FLIP robot. It combines the Gazebo world (environment layout, obstacles, the FLIP robot model), custom ROS2 packages (sensor communication and robot behavior), Python scripts (AI-based processing such as object, human, and fire detection), Gazebo plugins (bridging simulated sensors to ROS2 topics), and saved mapping databases. The full simulation is launched via [simulation.launch.py](./workspace/models/simulation.launch.py).

## [prototypes folder](/workspace/prototypes/)
This is where individual features were built and tested in isolation before integration into the main simulation. Each subfolder is a standalone prototype with its own README documenting the reasoning behind it, implementation details, usage instructions, advice for future developers, and contributor information. Prototypes that proved successful were later integrated into the models folder.

Below is a table for a clear overview of who helped with which prototype, if that prototype was implemented and short notes on what that prototype does.
| Prototype | Contributor | Implemented | Notes|
| --------- | ----------- | ----------- | ---- |
| [2d-cartographer-demo](./workspace/prototypes/2d-cartographer-demo/) | Django Manders | No | 2D mapping using Cartographer, used as a basis for implementing 3d-cartographer mapping |
| [3d-cartographer](./workspace/prototypes/3d-cartographer/) | Radeiaan Nandoe | No | 3D mapping using Cartographer, explored as an alternative mapping approach|
| [3D-Lidar-Mapping-RTAB](./workspace/prototypes/3D-Lidar-Mapping-RTAB/) | Radeiaan Nandoe | **Yes** | 3D mapping using RTAB-Map — the main LiDAR 3D-mapping implementation |
| [3D-Octomap](./workspace/prototypes/3D-Octomap/) | Radeiaan Nandoe | No | 3D occupancy mapping using OctoMap, explored as an alternative mapping approach |
| [airpressure-sensor](./workspace/prototypes/airpressure-sensor/) | Freya van den Berg | **Yes** | Air pressure sensor integration for detecting different air pressures in the environment |
| [altimeter](./workspace/prototypes/altimeter/) | Sarah Gbagi | No | Altimeter sensor integration for altitude measurement |
| [camera](./workspace/prototypes/camera/) | Django Manders | **Yes** | Ultra-wide camera implementation for a live-feed of the environment |
| [dijkstra-algorithm](./workspace/prototypes/dijkstra-algorithm/) | Sarah Gbagi | **Yes** | Dijkstra pathfinding algorithm as a back-up algorithm for autonomous navigation |
| [environment-with-obstacles](./workspace/prototypes/environment-with-obstacles/) | Radeiaan Nandoe, Django Manders | **Yes** | Test simulation environment with obstacles, used for testing other prototypes |
| [frontier-clusters-demo](./workspace/prototypes/frontier-clusters-demo/) | Django Manders | No | Frontier-based exploration clustering for autonomous pathfinding and environment exploration |
| [LiDAR-sensor-environment](./workspace/prototypes/LiDAR-sensor-environment/) | Radeiaan Nandoe | **Yes** | LiDAR sensor environment setup used for testing and developing LiDAR integration |
| [logical-audio-sensor](./workspace/prototypes/logical-audio-sensor/) | Sarah Gbagi | **Yes** | Logical audio sensor integration for receiving and sending audio data |
| [object-detection-opencv](./workspace/prototypes/object-detection-opencv/) | Maud Waasdorp, Radeiaan Nandoe | **Yes** | Object detection using OpenCV |
| [object-human-detection](./workspace/prototypes/object-human-detection/) | Maud Waasdorp, Radeiaan Nandoe | **Yes** | Combined object & human detection implementation |
| [path-finding-demo](./workspace/prototypes/path-finding-demo/) | Django Manders | **Yes** | Autonomous pathfinding demo, used as a basis for the final pathfinding implementation |
| [thermal-camera](./workspace/prototypes/thermal-camera/) | Maud Waasdorp | **Yes** | Thermal camera implementation for visualizing temperatures inside an environment |
| [fire-detection](./workspace/prototypes/fire-detection/) | Maud Waasdorp | Yes | Fire detection implementation using RGB and thermal camera to detect fires. |
| [YOLO-human-detection](./workspace/prototypes/YOLO-human-detection/) | Maud Waasdorp, Radeiaan Nandoe | **Yes** | Human detection using the YOLO model |

# Introduction
Welcome to the Hogeschool Utrecht project for the TI-students, Team Waterbenders. During this project the team developed, researched, tested, implemented and created a Digital Twin for the client, Futurised. The Digital Twin is based on their real-life robot FLIP, FLIP is a robot that can navigate and scan an environment and even extinguish fires. 

In order to satisfy the clients' needs, the team did research and created multiple prototypes to come to the concluding product for Futurised. By communicating frequently and showcasing multiple prototypes with the client, the team was able to fullfill the clients' requirements and wishes.

This repository is a transfer website for future project teams and Futurised to continue building and improving on this Digital Twin. 

# Assignment
## Main implementations
The most important requirement for FLIP from the client was **autonomus driving** and e**xploring environments**. Besides those, the team also implemented a few other things to bring the Digital Twin to the next level:
- **LiDAR 3D-mapping** including saved scans, in order te revisit the environment later on.
- **Object, human and fire detection**, in order to correctly assess situaitions in the environment.
- **Pathfinding algorithm**, in order to autonomusly manouvre and explore the environment in an effective way.

## Other implementations
Besides those main implementations, other sensors were implemented in FLIP:
- **Logical Audio Sensor:** in order to receive and send audio data.
- **Airpressure sensor:** in order to detect different airpressures in the environment.
- **Dijkstra Algorithm:** in order to have a back-up algorithm for FLIP to manouvre and explore autonomusly.
- **Ultra-wide camera:** in order to see a live-feed of the environment.
- **Thermal camera:** in order to see a live-feed of different temperatures inside an environment.

--- 
## Software
This Digital Twin is made using the following software:
- Python
- ROS2
- RViz
- Colcon
- Docker
- Gazebo

Please read the [navigation](#navigation) chapter below to learn how to navigate, read and use this repository accordingly.


# Futurised
Futurised is a private first responder organization operating 24/7 to support first responders during incidents. They enhance situational awareness through the use of smart technologies such as digital applications, drones, sensors, and robots. 

They help organizations operate in a future-proof, safe, and efficient way. Futurised turns ideas into results, from operational concepts and AI tools to project support and strategic guidance.

Futurised also develops innovative (digital) products that support first responders in operating more safely and efficiently. They also provide a platform where innovations come together, making it easy for first responders to find what they need.

**Communication with Futurised was always with Robbert Heinecke and Juliette Kraal, both co-founders of Futurised.**

Check out the [Futurised Website](https://www.getfuturised.com/), also check out their article on [Crisimanager](https://crisismanager.nl/drones-en-grondrobotica-digitale-verkenning-krijgt-europees-perspectief) to see FLIP in action.

![alt text](img/image.png)

# Instructions

Since the project is quite large and the setup isn't always straighforward, below is an overview of all of the different steps ordered in order of execution. Before running any code inside this repository make sure you've completed all of the below steps first.

## Step-by-step

- **1.** [Docker setup](/docker/README.md): Setup the Docker container, which the environment relies on to work.
  - **1.1.** Container creation
    - Windows:
      - [Using CMD](/docker/setup/container-creation/Windows/usingCMD.md)
      - [Using PowerShell](/docker/setup/container-creation/Windows/usingPowershell.md)
    - Ubuntu:
      - [Using dedicated graphics](/docker/setup/container-creation/Ubuntu/forDedicatedGraphics.md)
      - [Using integrated graphics](/docker/setup/container-creation/Ubuntu/forIntegratedGraphics.md)
  - **1.2.** [Starting the container](/docker/setup/container-start/README.md)
  - **1.3.** [Setting up Python venv](/docker/setup/container-venv/README.md)
  - **1.4. (optional)** [Using CUDA](/docker/setup/using-cuda/README.md)
- **2.** [Simulation setup](/setup/README.md): Install different software like ROS2, Colcon, RViz.
  - **2.1.** [Install required software](/setup/ROS2/README.md)
  - **2.2.** [Build Colcon packages](/setup/colcon/README.md)
- **3.** [Running the simulation](/workspace/README.md): Guide on how to run the full simulation.
  - **3.1.** [Visualization with RViz](/setup/RViz-visualisation/README.md)
  - **3.2.** [Running Python scripts](/setup/running-scripts/README.md)
  - **3.3.** [Running the full simulation](/workspace/models/README.md#to-run-the-complete-simulation)

# Conclusion and Recommendations

One of the main challenges encountered during the project was the integration of all prototypes into a single simulation environment. While most components functioned correctly on their own, combining all systems into one complete Digital Twin introduced performance issues and increased complexity within the simulation environment. Due to time constraints and the complexity of integration, a fully optimized combined implementation could not be completed within the project period.

For future project teams, we strongly recommend integrating completed prototypes into the main project as early as possible rather than waiting until the end of development. Continuous integration allows performance bottlenecks, compatibility issues and resource limitations to be identified and addressed earlier in the development process. This approach will make it easier to monitor system performance, maintain stability and achieve a fully integrated Digital Twin.

We hope this repository, documentation and collection of prototypes provide a strong foundation for future development and further improvements of the FLIP robot.
