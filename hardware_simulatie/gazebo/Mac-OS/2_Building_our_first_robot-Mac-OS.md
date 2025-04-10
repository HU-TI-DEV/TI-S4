### Gazebo build your first robot using gazebo ionic on Mac OS

Make a new folder for the project in your workspace.

```bash
mkdir ~/gz_transport_tutorial
cd ~/gz_transport_tutorial
```

Create our robot.sdf file. SDF is used to specify the contents of the simulation.

```bash
nano robot.sdf
```

Insert xml content of your robot.sdf. Save and quit. Start the server.

```bash
. ~/workspace/install/setup.zsh
gz sim -v 4 robot.sdf -s
```

And in another terminal start the GUI.

```bash
. ~/workspace/install/setup.zsh
gz sim -v 4 -g
```

Now you have a robot.

Quit and update the robot.sdf to add a drive system.

```xml
<plugin
    filename="gz-sim-diff-drive-system"
    name="gz::sim::systems::DiffDrive">
    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint</right_joint>
    <wheel_separation>1.2</wheel_separation>
    <wheel_radius>0.4</wheel_radius>
    <odom_publish_frequency>1</odom_publish_frequency>
    <topic>cmd_vel</topic>
</plugin>
```

Add this below:

```xml
      <model name='vehicle_blue' canonical_link='chassis'>
         <pose relative_to='world'>0 0 0 0 0 0</pose>
```

I have closed all terminals then opened two new ones. In our folder I will run. 

```bash
. ~/workspace/install/setup.zsh
gz sim -v 4 robot.sdf -s
```

Start GUI in the other terminal

```bash
gz topic -t "/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.5}, angular: {z: 0.05}"
gz sim -v 4 -g
```

Hit the play button and my robot is moving! It makes a circle.

## We will now add a sensor

Add another plugin for the sensor

```xml
<plugin filename="gz-sim-imu-system"
        name="gz::sim::systems::Imu">
</plugin>
```

And below </collision> (this tag has multiple entries!)

```xml
<sensor name="imu_sensor" type="imu">
    <always_on>1</always_on>
    <update_rate>1</update_rate>
    <visualize>true</visualize>
    <topic>imu</topic>
</sensor>
```

I needed a hard reboot for Mac OS X to get it working. Then start the server.

```bash
. ~/workspace/install/setup.zsh
gz sim -v 4 robot.sdf -s
```

In another terminal. Move your robot and start the GUI.

```bash
. ~/workspace/install/setup.zsh
gz topic -t "/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.5}, angular: {z: 0.05}"
gz sim -v 4 -g
```

In yet another terminal je can monitor topics. With gz topic -l  you can see what topics are available. To monitor your IMU sensor:

```bash
. ~/workspace/install/setup.zsh
gz topic -e -t /imu
```