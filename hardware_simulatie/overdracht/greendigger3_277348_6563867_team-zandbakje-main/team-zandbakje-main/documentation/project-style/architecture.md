# Gazebo Project Layers
The separation is done for modularity. 

`Author: Replitard`

---
## Simulation Layer
This layer is just gazebo. This layer only contains **.sdf files and model data**. In the project this is everything under the `src/environment` directory.
- Contains the world, terrain, obstacles, digger body, wheels, arm, and sensors.
- Publishes raw sensor data on Gazebo topics.
- Receives actuator commands on command topics.
- This is where physics and collisions happen.

Core tasks:
- Simulates env.
- Publish raw data.
- Executes commands.

---
## Interface Layer
This is the software bridge between Gazebo topics and the python/C++ logic. It makes the output from the topics usable and it is responsible for handling commands to gazebo. Treat this like an interpreter. This layer is **exclusively made in Python**.
The interface layer is under `src/interface`
- Subscribes to raw topics like IMU, lidar, GPS, camera, contact.
- Publishes commands like wheel velocity, arm movement.
- Converts raw Gazebo messages into a simpler internal format.
- Can also log data for debugging.

Core tasks:
- Reads Gazebo topics.
- Stores current robot state.
- Publish commands back to Gazebo.

Important note:
- One Python script is fine for now, but later we might want to split this up if there is time.

---
##  Logic Layer
This is the head of the project. Here the decisions are made. This layer does not communicate directly to gazebo. It only talks to the interface layer to get the clean data from. The logic layer is exclusively **Python**. Nothing else. There should be no .sdf or model data here. This folder is `src/`.  
Suitable dig locations (Points of Interest) are defined as world coordinates in `src/poi_route.json`. The behaviour manager loads this file at startup and drives the digger through each location in sequence. The file can be updated manually or with GPS data later with minimal change required to the behaviour manager.

### Perception
- Input: lidar, contact, maybe camera later.
- Output: obstacle detected, free path, object estimate.
*Perception asks the question of 'Is there something in the way?', 'What's in the way?' and 'Can I get around it?'*.
### Localization
- Input: Odometry, IMU, maybe GPS (not really).
- Output: current position of the digger in the diggable world.
*The purpose of knowing where the digger is at any given time helps with later POI.*
### Locomotion control
- Input: target direction, avoidance decision.
- Output: drive commands.
*Simple drive command output based on localization and perception.*
### Digging control
- Input: dig target, arm state, terrain state.
- Output: arm movement sequence.
*Module checks the current terrain state, checks where the arm is, and checks where to dig. If any of these are missing the digger will not dig.*
### Behavior manager
- Coordinates all of the above.
- Operates in states based on the information available.
- States: 
	- `manual`; Prevents active decision making and turns off the collission detection. Starts the keyboard publisher.
	- `idle`; Stops the digger and resets the arm to its out-of-the-way pose.
	- `drive`; Navigates to a target using POI driving, heading PID, or raw speed.
	- `dig`; Executes the full dig sequence at the current location, then advances to the next POI.
	- `error`; Stops all movement when a blocking condition is detected (e.g. chassis contact).
	- `avoid`; Stop, scan, drive, rotate in a loop until the obstable is out of range. Not yet implemented.

Core tasks:
- Makes decisions.
- Uses processed sensor data.
- Chooses what the digger should do next.

---
## Operator / Debug Layer
For the humans. This should be written in **python**, since unit tests are easier to make in python. This is in the `src/tests` directory.
Tests do *not* use the interface, and must work as a stand-alone from the rest unless it's to test the functionality of the interface. Nothing in `/src` must be dependent on anything in `/tests`.

- Manual keyboard control.
- Logging topic values.
- Visual checks during demos.
- Testing individual subsystems without running the behavioral manager.
- Testing functionality of the interface.
- Debugging the pipeline.
- Bypassing the interface entirely.

Core tasks:
- Manual override
- Debugging
- Storing values
- Demo support

---
# Dataflow
Pipeline:
1. Gazebo publishes raw sensor topics.
2. Python interface node reads them.
3. Interface layer builds `DiggerState`. (Name pending)
4. Logic layer decides next action.
5. Controller publishes command topics.
6. Gazebo moves the digger.
7. Gazebo publishes new raw sensor data -> step 1

---
## Interface
### Important topics
**Control Topics**  
From Interface -> To Gazebo (Sending commands).
- Drive command
- Arm shoulder pan
- Arm shoulder lift
- Arm elbow
- Arm wrist 1
- Arm wrist 2
- Arm wrist 3

**Feedback Topics**  
From Gazebo -> To Interface (Recieving validation data).
- Digger odometry
- Digger transforms
- Arm joint states

**Sensor Data Topics**  
From Gazebo -> To Interface (Recieving sim state data).
- IMU
- Camera stream
- LIDAR
- Chassis contact sensor

---