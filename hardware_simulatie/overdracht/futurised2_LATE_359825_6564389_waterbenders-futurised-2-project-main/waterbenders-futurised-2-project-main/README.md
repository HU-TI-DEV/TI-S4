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
- [Introduction](#introduction)
- [Assignment](#assignment)
  - [Main implementations](#main-implementations)
  - [Other implementations](#other-implementations)
  - [Software](#software)
- [Futurised](#futurised)
- [Instructions](#instructions)
  - [Step-by-step](#step-by-step)
  - [Other useful links](#other-useful-links)

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

- **1.** [Docker setup](/docker): Setup the Docker container, which the environment relies on to work.
  - **1.1.** [Container creation](/docker/setup/container-creation/README.md)
    - [Windows](/docker/setup/container-creation/Windows/)
    - [Ubuntu](/docker/setup/container-creation/Ubuntu/)
  - **1.2.** [Starting the container](/docker/setup/container-start/README.md)
  - **1.3.** [Setting up Python venv](/docker/setup/container-venv/README.md)
  - **1.4. (optional)** [Using CUDA](/docker/setup/using-cuda/README.md)
- **2.** [Simulation setup](/setup): Install different software like ROS2, Colcon, RViz.
  - **2.1.** [Install required software](/setup/ROS2/README.md)
  - **2.2.** [Build Colcon packages](/setup/colcon/README.md)
- **3.** [Running the simulation](/workspace): Guide on how to run the full simulation.
  - **3.1.** [Visualization with RViz](/setup/RViz-visualisation/README.md)
  - **3.2.** [Running Python scripts](/setup/running-scripts/README.md)
  - **3.3.** [Running the full simulation](/workspace/models/README.md#to-run-the-complete-simulation)


## Other useful links

- [Documentation](/docs): Files like the specifications of FLIP, research documents, development documents and proptypes. 
- [Protopytes](/workspace/prototypes/): A collection of prototypes that were used in the development of the **Digital Twin** (very useful for future students that might build on this projects code)

# Conclusion and Recommendations

One of the main challenges encountered during the project was the integration of all prototypes into a single simulation environment. While most components functioned correctly on their own, combining all systems into one complete Digital Twin introduced performance issues and increased complexity within the simulation environment. Due to time constraints and the complexity of integration, a fully optimized combined implementation could not be completed within the project period.

For future project teams, we strongly recommend integrating completed prototypes into the main project as early as possible rather than waiting until the end of development. Continuous integration allows performance bottlenecks, compatibility issues and resource limitations to be identified and addressed earlier in the development process. This approach will make it easier to monitor system performance, maintain stability and achieve a fully integrated Digital Twin.

We hope this repository, documentation and collection of prototypes provide a strong foundation for future development and further improvements of the FLIP robot.
