# RoboSub Gazebo Simulation
_Brought to you by team Nautilus_

## Introduction
This repository offers all the code and documentation to set up and run a robotic arm simulation in Gazebo, commissioned by [RoboSub](https://robosub.nl/en). Each module of the repository has a README file within it that contains a brief overview of the code, design choices, research, a setup guide, and recommendations for further improvement. 

This project was developed by team Nautilus, consisting of members Luuc Wingelaar, David Sigmund, Ying Tang, Aya Brocatus and Jorn Bransen. Delivered to us through college, the project follows a set of requirements from college itself, and from our client. 

Team Nautilus' Gazebo simulation is a robotic arm, specifically the robotic arm that's mounted on the real life RoboSub submarine. It is fully modeled with the same limitations and section sizes, and tries to be as accurate as possible to the real life counterpart. The goal of the simulation is to detect an orange valve, reach the arm over to it, grab the handle, and turn it 90 degrees into the open or closed position. Note that the only thing simulated is the robotic arm, the base of the AUV was ignored, in line with RoboSubs requirements. In order to achieve its goal, the arm currently uses a combination of computer vision with OpenCV, PID and Inverse Kinematics to reach its target. A more detailed description of each section can be found in the READMEs within their respective folders, found by navigating the table of contents.

## Table of contents

<!-- TOC -->
* [RoboSub Gazebo Simulation](#robosub-gazebo-simulation)
  * [Introduction](#introduction)
  * [Table of contents](#table-of-contents)
  * [Setup Guide](#setup-guide)
  * [Implementation choices](#implementation-choices)
  * [Links to modules](#links-to-modules)
  * [Limitations & Recommendations](#limitations--recommendations)
 * [Technical Contributions](#technical-contributions)
<!-- TOC -->

## Setup Guide
This section offers a step by step guide on how to properly set up and run the simulation.

1. The simulation will not work without a docker container with Gazebo installed, and MobaXterm to run the Gazebo environment. You can install docker [here](https://www.docker.com/products/docker-desktop/). You can install MobaXterm [here](https://mobaxterm.mobatek.net/download-home-edition.html).

2. Follow the steps in the [devcontainer README](.devcontainer/README.md). This will install all the required dependencies, and allows Gazebo to run on your GPU instead of your CPU, massively boosting runtime speed and overall performance. MobaXterm is still used for a fallback, in case WSLg doesn't work.

3. Build the simulation by pressing right click on the [CMakeLists.txt file](module_dev/CMakeLists.txt) inside of the module_dev folder, and pressing build file.

4. After building, go to the terminal within your code editor and run ```gz sim SubSimV4.sdf&```. Once Gazebo is opened, navigate to the robotic arm located under the block in the middle, and press the run button in Gazebo.

5. Go back to your code editor and run camera.py.

6. Run the main.cpp file. If the valve is within detection range of the camera, the arm should automatically move over to it and try to grab it. 

## Implementation choices
- The whole project was written in C++ (except for tests that require plotting, those utilize matplotlib). C++ was the language of choice for our team, since that is the coding language that our college focuses on, and it is faster compared to Python. <br>
- Each function of the arm is separated into its own folder. This is for organization purposes, allowing users to easily navigate the repository and locate aspects of the simulation that they potentially want to change, or learn more about. In addition to this, each function also has its own README file, encouraging readability, and easy to locate guides and explanations on each section. This is to prevent users from having to scroll all the way through a massive README file in order to locate a specific section they want to read up on, and is also done for organization purposes. <br>



## Links to modules

Here you can find the modules themselves, along with their respective READMEs or other documents. 
- [Dev Container](.devcontainer/README.md)
  - [Gazebo Test](.devcontainer/TestGazebo/README.md)
  - [Python Test](.devcontainer/TestPython/main.py)
- [Development Module](module_dev/README.md)
  - [Arm Coordinate Movement](module_dev/ArmCoordinatenMovement/README.md)
  - [Common](module_dev/common/README.md)
  - [Gripper](module_dev/gripper/README.md)
  - [IK Solver](module_dev/IKSolver/README.md)
  - [Robot Arm](module_dev/RobotArm/README.md)
  - [Submarine Sim](module_dev/subSim/README.md)


## Limitations & Recommendations
- The simulation currently uses Gazebo. Gazebo is very limiting in that it's very slow to run, and quickly begins struggling when doing anything that requires large amount of calculation or detail. For further expansion of the simulation and more realistic modeling, we highly recommend using a different simulation software that is more suited for the job. 
- The body of the RoboSub is unable to move in the simulation. For further advancement, we recommend at least allowing basic navigation, either through pathfinding or manual control (or both) to better simulate what happens when it runs into the valve.
- The simulation currently isn't true to real life. Things like water resistance and light distortion effects that occur in an underwater environment aren't modeled. To allow for more a more representative simulation, we recommend implementing this in the future.
- The gripper of the arm does not yet rotate to align with the angle of the valve handle. The handle angle detection itself, however, is already implemented and published to a topic.
- The gripper doesn't approach the handle in a straight line yet, this can be achieved by continously adjusting the target position in a straight line towards the valve, ideally also implementing a Slow in and Slow out effect.
- Currently a depth camera is used to determine the distance to the valve, this is however not true to the actual model, which merely has possession over a regular camera. In order to make the simulation more in line with the actual robosub it is advisable to also switch to a regular camera and use the (known) actual size of the valve, the perceived size of the valve and the field of view to calculate the distance.
- The gripper at [Gripper](module_dev/gripper/README.md) that was made was not implemented in the final version of the sdf model so the current gripper of the robosub is a simple box, the [Gripper](module_dev/gripper/README.md) is a more realistic version that could be implemented.

# Technical Contributions
| Technical module  | Description | Contributors |
|---|---|---|
| [ArmCoordinatenMovement](module_dev/ArmCoordinatenMovement/README.md) | Background loop running low-level joint PID velocity controls. | David, Luuc|
| [Common](module_dev/common/README.md) | Single source of truth containing static joint parameters and kinematic specs. | Luuc |
| [ComputerVision](module_dev/computerVision/README.md) | OpenCV object tracking and depth-camera transforms for world 3D vectors. | Ying, Aya|
| [Gripper](module_dev/gripper/README.md) | URDF finger geometry implementation handling asymmetric revolute joint workarounds. | David |
| [IKSolver](module_dev/IKSolver/README.md)| Forward (FK) and Inverse Kinematics (IK) coordinate processing. | Luuc, Jorn |
| [RobotArm](module_dev/RobotArm/README.md)| Top-level node linking CV targets, IK solvers, and low-level joint loops. | David, Luuc |
| [SubSim](module_dev/subSim/README.md) | Gazebo `.sdf` world templates with underwater physics and plugins. | David |
| [PID](module_dev/ArmCoordinatenMovement/PIDTest.md)| PID configuration and PID tuning with a simple python script | David |
