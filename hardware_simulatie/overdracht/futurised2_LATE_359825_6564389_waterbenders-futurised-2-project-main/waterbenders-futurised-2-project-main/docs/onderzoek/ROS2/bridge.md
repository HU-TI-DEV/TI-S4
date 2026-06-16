# Links
- [gazebosim.org](https://gazebosim.org/docs/latest/ros2_integration/)


# [Message types for bridging](https://github.com/gazebosim/ros_gz/blob/ros2/ros_gz_bridge/README.md#bridge-communication-between-ros-and-gazebo)
The following message types can be bridged for topics:

| ROS type                                       | Gazebo Transport Type               |
| ---------------------------------------------- | :------------------------------:    |
| actuator_msgs/msg/Actuators                    | gz.msgs.Actuators                   |
| builtin_interfaces/msg/Time                    | gz.msgs.Time                        |
| geometry_msgs/msg/Point                        | gz.msgs.Vector3d                    |
| geometry_msgs/msg/Pose                         | gz.msgs.Pose                        |
| geometry_msgs/msg/PoseArray                    | gz.msgs.Pose_V                      |
| geometry_msgs/msg/PoseStamped                  | gz.msgs.Pose                        |
| geometry_msgs/msg/PoseWithCovariance           | gz.msgs.PoseWithCovariance          |
| geometry_msgs/msg/PoseWithCovarianceStamped    | gz.msgs.PoseWithCovariance          |
| geometry_msgs/msg/Quaternion                   | gz.msgs.Quaternion                  |
| geometry_msgs/msg/Transform                    | gz.msgs.Pose                        |
| geometry_msgs/msg/TransformStamped             | gz.msgs.Pose                        |
| geometry_msgs/msg/Twist                        | gz.msgs.Twist                       |
| geometry_msgs/msg/TwistStamped                 | gz.msgs.Twist                       |
| geometry_msgs/msg/TwistWithCovariance          | gz.msgs.TwistWithCovariance         |
| geometry_msgs/msg/TwistWithCovarianceStamped   | gz.msgs.TwistWithCovariance         |
| geometry_msgs/msg/Vector3                      | gz.msgs.Vector3d                    |
| geometry_msgs/msg/Wrench                       | gz.msgs.Wrench                      |
| geometry_msgs/msg/WrenchStamped                | gz.msgs.Wrench                      |
| gps_msgs/msg/GPSFix                            | gz.msgs.NavSat                      |
| marine_acoustic_msgs/msg/Dvl                   | gz.msgs.DVLVelocityTracking         |
| nav_msgs/msg/Odometry                          | gz.msgs.Odometry                    |
| nav_msgs/msg/Odometry                          | gz.msgs.OdometryWithCovariance      |
| rcl_interfaces/msg/ParameterValue              | gz.msgs.Any                         |
| ros_gz_interfaces/msg/Altimeter                | gz.msgs.Altimeter                   |
| ros_gz_interfaces/msg/Contact                  | gz.msgs.Contact                     |
| ros_gz_interfaces/msg/Contacts                 | gz.msgs.Contacts                    |
| ros_gz_interfaces/msg/Dataframe                | gz.msgs.Dataframe                   |
| ros_gz_interfaces/msg/Entity                   | gz.msgs.Entity                      |
| ros_gz_interfaces/msg/EntityWrench             | gz.msgs.EntityWrench                |
| ros_gz_interfaces/msg/Float32Array             | gz.msgs.Float_V                     |
| ros_gz_interfaces/msg/GuiCamera                | gz.msgs.GUICamera                   |
| ros_gz_interfaces/msg/JointWrench              | gz.msgs.JointWrench                 |
| ros_gz_interfaces/msg/Light                    | gz.msgs.Light                       |
| ros_gz_interfaces/msg/LogicalCameraImage       | gz.msgs.LogicalCameraImage          |
| ros_gz_interfaces/msg/LogPlaybackStatistics    | gz.msgs.LogPlaybackStatistics       |
| ros_gz_interfaces/msg/ParamVec                 | gz.msgs.Param                       |
| ros_gz_interfaces/msg/ParamVec                 | gz.msgs.Param_V                     |
| ros_gz_interfaces/msg/SensorNoise              | gz.msgs.SensorNoise                 |
| ros_gz_interfaces/msg/StringVec                | gz.msgs.StringMsg_V                 |
| ros_gz_interfaces/msg/TrackVisual              | gz.msgs.TrackVisual                 |
| ros_gz_interfaces/msg/VideoRecord              | gz.msgs.VideoRecord                 |
| ros_gz_interfaces/msg/WorldStatistics          | gz.msgs.WorldStatistics             |
| rosgraph_msgs/msg/Clock                        | gz.msgs.Clock                       |
| sensor_msgs/msg/BatteryState                   | gz.msgs.BatteryState                |
| sensor_msgs/msg/CameraInfo                     | gz.msgs.CameraInfo                  |
| sensor_msgs/msg/FluidPressure                  | gz.msgs.FluidPressure               |
| sensor_msgs/msg/Image                          | gz.msgs.Image                       |
| sensor_msgs/msg/Imu                            | gz.msgs.IMU                         |
| sensor_msgs/msg/JointState                     | gz.msgs.Model                       |
| sensor_msgs/msg/Joy                            | gz.msgs.Joy                         |
| sensor_msgs/msg/LaserScan                      | gz.msgs.LaserScan                   |
| sensor_msgs/msg/MagneticField                  | gz.msgs.Magnetometer                |
| sensor_msgs/msg/NavSatFix                      | gz.msgs.NavSat                      |
| sensor_msgs/msg/PointCloud2                    | gz.msgs.PointCloudPacked            |
| sensor_msgs/msg/Range                          | gz.msgs.LaserScan                   |
| std_msgs/msg/Bool                              | gz.msgs.Boolean                     |
| std_msgs/msg/ColorRGBA                         | gz.msgs.Color                       |
| std_msgs/msg/Empty                             | gz.msgs.Empty                       |
| std_msgs/msg/Float32                           | gz.msgs.Float                       |
| std_msgs/msg/Float64                           | gz.msgs.Double                      |
| std_msgs/msg/Header                            | gz.msgs.Header                      |
| std_msgs/msg/Int32                             | gz.msgs.Int32                       |
| std_msgs/msg/String                            | gz.msgs.StringMsg                   |
| std_msgs/msg/UInt32                            | gz.msgs.UInt32                      |
| tf2_msgs/msg/TFMessage                         | gz.msgs.Pose_V                      |
| trajectory_msgs/msg/JointTrajectory            | gz.msgs.JointTrajectory             |
| vision_msgs/msg/Detection2D                    | gz.msgs.AnnotatedAxisAligned2DBox   |
| vision_msgs/msg/Detection2DArray               | gz.msgs.AnnotatedAxisAligned2DBox_V |
| vision_msgs/msg/Detection3D                    | gz::msgs::AnnotatedOriented3DBox    |
| vision_msgs/msg/Detection3DArray               | gz::msgs::AnnotatedOriented3DBox_V  |



# Bridge
## Setup
1. Start a bridge between ROS and Ignition
    ```bash
    . /opt/ros/foxy/setup.bash
    ```

2. Install bridge workspace?
    ```bash
    . /bridge_ws/install/setup.bash
    ```


3. Open the bridge
    ```bash
    ros2 run ros_ign_bridge parameter_bridge /topic/at/which/data/will/be/sent@rosMessageType@ignitionMessageType
    ```

- **Controlling robot using Twist mesages for Ackermann steering example**
    ```bash
    ros2 run ros_gz_bridge parameter_bridge /model/FLIP/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist
    ```

- Ignition example
    ```bash
    ros2 run ros_ign_bridge parameter_bridge /keyboard/keypress@std_msgs/msg/Int32@ignition.msgs.Int32
    ```

- GZ example 1
    ```bash
    ros2 run ros_gz_bridge parameter_bridge /scan@sensor_msgs/msg/LaserScan@gz.msgs.LaserScan
    ```



## Symbols and meaning after `/topic/at/which/data/will/be/sent@ROSMessageType`
- `@` : bidirectional communication between ROS <-> Ignition/Gazebo 
- `[` : bridge Ignition/Gazebo -> ROS
- `]` : bridge ROS -> Ignition/Gazebo  


# Test
1. Run sdf file in a terminal

2. Open a new terminal and listen to the messages sent by the key publisher
    ```bash
    # Source ROS distro first
    . /opt/ros/foxy/setup.bash

    # Listen to messages sent
    ros2 topic echo /name/of/the/topic
    ```

- **example ros/jazzy**:
    ```bash
    # Source ROS distro first
    . /opt/ros/jazzy/setup.bash

    # Listen to messages sent
    ros2 topic echo /keyboard/keypress
    ```

- example ros/foxy:
    ```bash
    # Source ROS distro first
    source /opt/ros/foxy/setup.bash

    # Listen to messages sent
    ros2 topic echo /model/FLIP/cmd_vel
    ```

3. Open the Gazebo app/GUI and send data for example with keypresses

4. Check second terminal where you did step 2 for echoed data.