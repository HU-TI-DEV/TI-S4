<img src = ../../images/teamlogo.png align="right" width="135">

# Other
In this folder, any files can be found which do not belong to a different category but are still part of the end product. These files are files such as Gazebo specific files, a main file and a terrain file. 

None of the files had been of previous knowledge to us before this project. This means that they contained quite a learning curve.
## Choices & Clarification
### [.sdf](demoEnvironment.sdf) & [.stl](DrivableTerrain.stl)
`.stl made by: Samuel Epp, .sdf coded by: Samuel Epp, Ryan Smit & Yannick Hogetoorn`

The choice to work with these files has not been fully up to the development team. Since the school required us to work with Gazebo we were bound to work with .sdf files. These files were completely new to all of us but became a new normal. This file format makes it possible to work with simulation sensors, plugins or physics. A lot of the things learnt throughout the production of this document can still be found in the file. 

The .stl format was chosen because a terrain needed to be simulated in Gazebo. This terrain could be implemented in multiple ways such as a heightmap or by importing more plugins. In the end we decided to use stl files since these could be created with ease. Stl files can be created by using Fusion 360 or Blender as a GUI.

### Physics settings
In order to not complicate the process too much, the choice was made to use the default physics engine.

### DiffDrive
Stated by the requirements from GreenDigger, the Autonomous Mobile Platform needs to have 4 fully independent wheels. Limited by this requirement, the choice was made to use a DiffDrive system. This system is highly capable of moving the car in all directions using only 4 independent wheels. 

### Depth Camera
The decision to use a depth camera is elaborated upon in the [object recognition readme](../ObjectRecognition/README.md). Its FOV is set to 60° because this is a default value.

### Simplified vehicle
The chassis is kept simple as this was not the purpose of our project. There are some limitations set by GreenDigger in how big the chassis should be. These limitations are: 4,5 meter length, 2 meter width and a wheel radius of 0,8 meter. 

### Pose Publisher
To obtain the position and orientation of the Autonomous Mobile Platform, the system subscribes to a Gazebo topic. A topic functions similarly to an API endpoint. The topic is hardcoded into the PosePublisher and is currently specified as: /model/vehicle/pose. The pose data received from this topic is used by multiple functions throughout the program. It is used by object recognition for a lot of the calculations but the pose data is also used by the driving algorithm. Because multiple classes use this data the subscriber has been transformed into a class.

As will be discussed in the problems sections the only combination of gyroscope and GPS in Gazebo was to make use of the PosePublisher. This then also concluded our choice for this software.

## [main.cc](main.cc)
`Coded by: Samuel Epp. Improved by: Yannick Hogetoorn & Ryan Smit`
### Central ProcessController
The Autonomous Mobile Platform is controlled by the central ProcessController. This controller is implemented because all of the other technologies were kept pretty generic. This way all other classes can be used in a different project. The ProcessController class combines path planning, driving, and obstacle detection all into one controller. 

### Improvement to A*
While using the full path received from the A* algorithm provides full step by step key points to drive through, most of these key points are not of much importance. Removing points in between the start and end point of a straight line, results in a path which can be driven with more speed and less mechanical wear. 

Previous explained process is wrapped inside the simplifyPath() function which gets called once after every planning has concluded. 

### Grid Size
Deciding how big the A* grid should be was one of multiple possible approaches. The choice ended up settling on generating one big grid for an entire area. This had been done because we are not working on an embedded controller so we have the working space to save all node data.

### Points of Interest (POI's)
In order to drive from predetermined point to predetermined point, a function was made which takes two variables. This function makes sure the Autonomous Mobile Platform can drive the pattern required by GreenDigger requirements. 

### Obstacle retention
Since the choice had been made to store one big grid, all obstacles previously detected are still stored in the A* algorithm. Doing this makes sure no resetting of old obstacles is necessary.

## Problems
### .sdf & .stl
#### First contact
As previously mentioned this was our first time working with SDF files. This meant that we needed to learn a lot of new functions and other possibilities. It could be that some of these inaccuracies have snuck into the final product. We have tried to fix this as much as possible by using documentation and other resources such as chatbots.

### main.cc
The main controller contained very little problems.

### PosePublisher
#### Orientation in Gazebo
As mentioned above there are very few actually working solutions to get the orientation and coordinates of an object in Gazebo. The option of the GPS has been developed but could not be executed without error messages. Why these error messages kept popping up is still not clear to us and neither is it to chatbots. The sensor does exist but might not be worth investigating further. It can be found on the [sdfFormat site](https://sdformat.org/spec/1.12/sensor/#sensor_gps). In the end the PosePublisher [(Gazebo SIM, n.d.)](https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1PosePublisher.html) proved to be the best solution. In reality a combination of a gps and a gyroscope can mimic the performance of the posePublisher very closely. This behaviour meant to us that it would be safe to use this plugin.

In order to do calculations on the posepublisher data however, the orientation did need to be transformed from quaternions to degrees. Later when the data needed to be uploaded quaternions were again needed to publish the movement [(Gazebo SIM, n.d.)](https://gazebosim.org/api/math/7/rotation_example.html).

## Advice
### .sdf & .stl
In contrast to other parts of the project the chassis received very few programming hours. If any following group would need to implement a full excavation tool on this chassis we recommend them to first work on the chassis and upgrade the full design.

Working with one new technology is hard. Working with two is even more difficult. This is why we chose to use Fusion 360 as an editing tool. Some of us had prior experience with this profile. If you are more capable with a different program which can export files in stl format, we strongly recommend you to use that one.

### main.cc
No advice

## Bronnen
Gazebo SIM. (n.d.). PosePublisher Class Reference. https://gazebosim.org/api/sim/8/classgz_1_1sim_1_1systems_1_1PosePublisher.html
Gazebo SIM. (n.d.). Rotation example. https://gazebosim.org/api/math/7/rotation_example.html
OSRS. (n.d.). Specification. https://sdformat.org/spec/1.12/sensor/#sensor_gps
Wikipedia. (n.d.). PID controller. https://en.wikipedia.org/wiki/PID_controller
Wikipedia. (n.d.). PID regelaar. https://nl.wikipedia.org/wiki/PID-regelaar