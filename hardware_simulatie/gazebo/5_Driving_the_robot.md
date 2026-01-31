# 5. Driving the robot

As we have seen in [building our first robot](./2_Building_our_first_robot.md) we can move the robot with the following instructions:

~~~
export GZ_PARTITION=test
gz topic -t "/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.5}, angular: {z: 0.05}"
~~~

As you can see the topic we are publishing to has a certain number of changes:
- the topic is /cmd_vel in stead of /foo or /imu
- the message type is of the form gz.msgs.Twist
- the message consist of several sub messages 

We will try to make the robot move with our own .cc code. For this you have to change the publisher.cc code to enable above changes. The first two are trivial. The last one is rather tricky. Study the DiffDrive.cc file in the [gz sim repo](https://github.com/gazebosim/gz-sim/blob/gz-sim10/src/systems/diff_drive/DiffDrive.cc) to understand how the messages need to be build up (tip: search for mutable_linear in the .cc file). 
