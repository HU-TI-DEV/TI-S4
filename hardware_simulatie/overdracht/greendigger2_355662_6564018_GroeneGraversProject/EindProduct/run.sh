#!/bin/bash

# Kill background processes on Ctrl+C
trap "kill 0" EXIT

echo ">>> Building controller..."
mkdir -p controller/build
cd controller/build
cmake ..
make -j4
cd ../..

echo ">>> Building vision..."
mkdir -p vision/build
cd vision/build
cmake ..
make -j4
cd ../..

echo ">>> Fixing Gazebo paths..."
export GZ_SIM_RESOURCE_PATH=$(pwd)/models

echo ">>> Starting Gazebo..."
gz sim desert.sdf &

echo ">>> Starting vision components..."
cd vision/build
./camera &
cd ..
python3 vision.py &
cd ..

echo ">>> Waiting for the simulation..."
sleep 5

echo ">>> Running main controller..."
./controller/build/main