# Altimeter Sensor
*13/06/2026* <br>
*Sarah Gbagi*

## Table of contents
- [Decisions](#descisionsdescisions)
- [Implementation](#implementation)
- [Advice](#advice)
- [Source](#source)

# Descisions
The altimeter sensor was **not** integrated into the final product. 

The reasoning behind this decision is that Flip (the robot) does not navigate across varying altitudes within the simulation. Because of this the altimeter would constantly return a value of 0.

# Implementation
Although it is not in the final product, there has already been laid groundwork for this sensor. The altimeter has been successfully implemented in the *altimeter_prototype.sdf* and the *altimeter_prototype.cc* file within this folder.

To verify that the altimeter measures values correctly you can manually control the cube component equipped with the altimeter directly via the terminal.

# Testing via the Terminal
To verify that the altimeter measures values correctly you can manually control the cube component equipped with the altimeter directly via the terminal.

Move up:
```
gz topic -t /model/cube_with_thruster/joint/thruster_joint/cmd_thrust \
  -m gz.msgs.Double \
  -p "data: 3.0"
```

Stop:
```
gz topic -t /model/cube_with_thruster/joint/thruster_joint/cmd_thrust \
  -m gz.msgs.Double \
  -p "data: 0.0"
```

# Advice
If the project is expanded in the future to include environments with varying heights/altitudes, the altimeter sensor can be fully utilized and integrated into the main navigation system using the existing codes.

# Source
Gazebo Gazebo: Altimeter class reference. (n.d.). https://gazebosim.org/api/gazebo/6/classignition_1_1gazebo_1_1Altimeter.html