# Fire detection with a thermal camera sensor
This module handles fire detection in a Gazebo environment using a thermal camera. The thermal camera measures the temperature per pixel. The hot pixels that belong to a fire are processed via ROS2. After that the robot determines the direction and distance to the fire and a goal + marker is placed in Rviz for visualisation

---

## How does it work?
The system follows the data flow below to transform raw thermal sensor input into navigation goals:

Gazebo (thermal camera) → ros_gz_bridge → ROS2 → fire_navigator → /goal_pose + /fire_marker → RViz

1. **Simlation:** Gazebo simulates a parking garage with a burning car that emits a heat signature, and a thermal camera on the robot.
2. **Bridge:** ros_gz_bridge converts the Gazebo camera gz.msgs.Image into a ROS2 sensor_msgs/msg/Image, published on the /thermal_camera_8bit/image topic.
3. **Detection** fire_navigator node subscribes to /thermal_camera_8bit/image topic, Identifies the fire pixels and calculates the fire. It then cross-references this with LiDAR data to get an estimate of the distance of the fire from the robot.
4. **Output:** The node publishes the calculated destination to the /goal_pose topic for the path planner and show a visualization marker on /fire_marker for monitoring in Rviz.
5. **thermal_relay** The thermal_relay node sends the thermal image to /camera/image_raw, allowing the thermal camera feed to be viewed in Rviz.

### Technologies used
- **Gazebo** - simulation of the environment, the fire and the thermal camera
- **gz-sim-thermal-system** - Gazebo plugin that gives objects a temperature
- **ROS2 (Jazzy)** - data transport between components
- **ros_gz_bridge** - bridge between Gazebo and ROS2
- **RViz** - live visualization of the detected heat source

---

## How is the fire detected?
The thermal camera creates an 8-bit grayscale image (L8), where each pixel value (0-255) is a temperature. The hotter the object, the higher the pixel value. The detection happens in fire_navigator.cc through the following steps:

1. **Finding hot pixels:** all pixels above the threshold FIRE_THRESHOLD of 180/255, ~450 C are seen as fire. Hotter pixels count more than barely warm pixels.
2. **Determining direction:** from the weighted center of the hot pixels cx the angle to the fire is calculated relative to the center of the camera: (CAM_W / 2 - cx) / CAM_W * CAM_HFOV.
3. **Determining distance:** the camera only gives a direction, not a distance. Using the LiDAR the nearest point in that direction is found. If the LiDAR sees nothing, 8m is used as an estimate.
4. **Calculating world position:** using the tanks position /odom, the direction and the distance, the position of the fire in the world is calculated.
5. **Smoothing:** the fire position is averaged over multiple frames so that the goal does not jump around while the robot turns.
6. **Goal + marker:** a goal is placed 2m in front of the fire /goal_pose and an orange sphere with the label "VUUR" is shown in RViz /fire_marker.

### Why a threshold value?
In the simulation the environment has a background temperature (~300 K) and the burning car has a much higher temperature (up to 673 K, ~400 C). By only including pixels above the threshold value, normal colder objects are ignored and only the fire remains making it so that only the fire and potentially other heat sources remain. This prevents ambient objects at normal temperatures from being falsely detected as fire.

The full detection and navigation code is in
[ros2/tonk_mapping/src/fire_navigator.cc](../../../ros2/tonk_mapping/src/fire_navigator.cc).

---

## Display in RViz

The detection is made visible in two ways:

- **Marker:** fire_navigator publishes an orange sphere at the calculated position of the fire, plus a text label "VUUR" above it. The marker is in the odom frame and has a lifetime of 3 seconds, so it disappears by itself when the fire is no longer seen.
- **Thermal image:** this node subscribes to /thermal_camera_8bit/image and republishes it on /camera/image_raw. This allows the thermal image to be viewed in the same image viewer as the regular camera, without extra configuration.

In RViz, add a **Marker** display on topic /fire_marker (with fixed frame odom) to see the heat source on the map. For the thermal camera image, add an **Image** display on /camera/image_raw or it can be directly on /thermal_camera_8bit/image.

[ros2/person_detection/person_detection/thermal_relay.py](../../../ros2/person_detection/person_detection/thermal_relay.py).

---

## Configuration
The thermal camera is defined in model.sdf as a sensor of the type thermal. The most important settings:

| Setting | Value | Description |
| --- | --- | --- |
| width × height | 320 × 240 | resolution of the image |
| format | L8 | 8-bit grayscale |
| update_rate | 30 | frames per second |
| topic | thermal_camera_8bit/image | ROS2 topic with the thermal image |
| min_temp | 253.15 K | lowest temperature the sensor displays |
| max_temp | 673.15 K | highest temperature the sensor displays |
| resolution | 3.0 | temperature steps per pixel value |

The temperatures of objects are set in [parking_garage.world](../../../Gazebo/worlds/parking_garage.world) via the gz-sim-thermal-system plugin. The burning car has of multiple parts each with its own temperature:

| Part | Temperature | Converted |
| --- | --- | --- |
| Body | 673 K | ~400 C |
| Roof | 623 K | ~350 C |
| Wheels | 473 K | ~200 C |

The environment has a background temperature of 300 K with a temperature_gradient of 0.1. This creates a clear contrast between the fire and the rest of the world and objects.

---

Related files:

| Path | Description |
| --- | --- |
| ros2/tonk_mapping/src/fire_navigator.cc | detects the fire and steers the robot towards the fire |
| ros2/person_detection/person_detection/thermal_relay.py | sends the thermal camera image to /camera/image_raw |
| Gazebo/worlds/parking_garage.world | contains the burning car and atmosphere settings |

<details>
<summary>Links to the source code</summary>

- [thermal_camera_test.cc](../../../Gazebo/models/thermal_camera/thermal_camera_test.cc) - test program
- [fire_navigator.cc](fire_navigator.cc) - fire detection and navigation
- [thermal_relay.py](../../person_detection/person_detection/thermal_relay.py) - sends thermal image
- [parking_garage.world](../../../Gazebo/worlds/parking_garage.world) - world with the burning car

</details>

---

## Recommendation
This part is intended for the follow-up team that continues building on the fire detection. The current system detects fire based on a fixed temperature threshold and steers the robot towards it. Below are suggestions to further expand and improve it.

### Improving fire detection
- **Tuning the threshold value:** the current FIRE_THRESHOLD (180/255) is fixed. A dynamic threshold based on the hottest pixels in the image, makes the detection more robust with changing temperatures.
- **Multiple heat sources:** the current logic assumes a single fire. By clustering the hot pixels, multiple fires can be recognized at the same time.

### New functionalities to build on
- **Sensor fusion:** combine the thermal detection with the YOLO person detection so that the robot distinguishes between people and fire.
- **Logging temperature:** publish the measured maximum temperature as a ROS2 topic for monitoring or alerting.

---

# Sources

Gazebo. (n.d.). Thermal camera in Gazebo. [https://gazebosim.org/api/sensors/7/thermalcameraigngazebo.html](https://gazebosim.org/api/sensors/7/thermalcameraigngazebo.html)

Ros2 Docs. (n.d.). RViz User Guide. [https://docs.ros.org/en/rolling/Tutorials/Intermediate/RViz/RViz-User-Guide/RViz-User-Guide.html](https://docs.ros.org/en/rolling/Tutorials/Intermediate/RViz/RViz-User-Guide/RViz-User-Guide.html)

Ros2 Docs. (n.d.). ros_gz_bridge Bridge communication between ROS and Gazebo. [https://docs.ros.org/en/jazzy/p/ros_gz_bridge/](https://docs.ros.org/en/jazzy/p/ros_gz_bridge/)