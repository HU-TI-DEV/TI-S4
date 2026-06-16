#!/bin/bash
export GZ_SIM_RESOURCE_PATH=/workspace/src/Futurised/models
gz sim /workspace/src/Futurised/worlds/robot_world.world &
ros2 launch launch.py
