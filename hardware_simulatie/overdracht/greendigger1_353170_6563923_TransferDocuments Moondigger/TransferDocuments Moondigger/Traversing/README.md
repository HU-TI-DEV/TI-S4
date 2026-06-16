<img src="../../images/teamlogo.png" align="right" width="135">

# Contributions
`Coded by: Ryan Smit & Samuel Epp`

The code is programmed by Ryan and Samuel. Samuel has also made a lot of improvements to Ryan his code in order to make it attachable to the main code.
# Traversing
A large part of the Autonomous Mobile Platform is the Mobile part. This makes it very important that the Autonomous Mobile Platform is able to traverse from one spot to the other. Since one of the first lessons of the semester covered PID controllers, we decided to add one to our driving algorithm.

The result is the code which can be found in this [file](./driving.cc).

## Choices & Clarifications
`Coded by: Samuel Epp & Ryan Smit`

### Turning then driving
Since all of the code has been in development throughout the project, the decision was made to drive to a point and then first orientate the Autonomous Mobile Platform before starting to traverse the route. When the Autonomous Mobile Platform is within a threshold for the turn it can start the driving PID controller.

### PID controller for speed
As mentioned above, a PID controller has been chosen to move the Autonomous Mobile Platform around the environment ([Wikipedia, n.d.](https://en.wikipedia.org/wiki/PID_controller)). This is the most future proof method and will be able to stop the Autonomous Mobile Platform exactly at the right place even when sudden changes are detected.

### P controller for rotation
Adding more values to a controller costs time and can influence the performance of a controller negatively. This meant that when using only the p value for the orientation worked well, it became unnecessary to implement other values.

### PoseCallback
In order to accurately know where the Autonomous Mobile Platform is located, the pose publisher from gazebo is accessed (More about this [here](../Other/README#pose-publisher.md)). This choice was made because using one constant measurement mechanic makes sure no misalignment issues occur.


## Problems 
The PID controller can give quite strong power to the wheels when left unrestricted. This prompted a maximum speed limit.

## Advice

- Change the PID from a Speed to a Power controller

The speed controller can give some odd results and may break harder than wanted. This can be solved by writing extra code but can also be solved by taking the actual sensor into account. Since the Autonomous Mobile Platform contains IMU's at this stage, a power controller may fit better.


# Sources:
Wikipedia. (n.d.). PID controller. https://en.wikipedia.org/wiki/PID_controller