# Simulation Setup Guide

This documentation explains how to setup, run and extend the ROS2 Gazebo simulation. It is **neccesary** to follow the full installation process in order to create a working environment to run the simulation. 

The only thing that could be skipped is the Using Cuda part, this might be nice for those with dedicated graphics cards when having trouble running the simulation.

## Installation

1. [Container Creation](../docker/README.md) -> Starting the container with the correct image.
2. [Build Workspace with Colcon](colcon/README.md) -> Building the workspace using Colcon.
3. [Python Environment (Virtual Environment)](../docker/setup/container-venv/README.md) -> Creating a venv and installing the correct versions of packages.
4. [Using Cuda](../docker/setup/using-cuda/README.md) -> Guide to using Cuda (the dedicated GPU on the pc instead of CPU) for better performance.
5. [Installing ROS2, Slam and Packages](ROS2/README.md) -> Installation of ROS2 including Slam and creating Packages with Colcon in the workspace.

## Running
- [Start Container with .ps1](../docker/setup/container-start/README.md) -> Easy way to start and enter the workspace container.
- [RViz Setup](RViz-visualisation/README.md) -> Setting up RViz for visualisation of all data.
- [Running Scripts](running-scripts/README.md) -> Without using `simulation.launch.py` to run all the scripts.