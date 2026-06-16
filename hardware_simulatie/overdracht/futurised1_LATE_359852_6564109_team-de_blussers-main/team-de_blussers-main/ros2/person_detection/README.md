# person_detection (ROS2 package) + Thermal camera
ROS2 package that detects people in the camera images from Gazebo using a retrained YOLO model and visualizes the result live in RViz.

This package forms the **ROS2 part** of the vision pipeline. The training of the model and the dataset are in the [vision/](../../vision/README.md) folder.

```
Gazebo (camera) → ros_gz_bridge → ROS2 → cv_bridge → YOLO → /person_detection/image → RViz
```

---

## Nodes

The package contains three ROS2 nodes (person_detection/):

### detector.py → person_detector
The main node that performs the person detection.

- **Subscribe:** /camera/image_raw (sensor_msgs/Image) - the RGB camera stream.
- **Publish:** /person_detection/image (sensor_msgs/Image) - the annotated image with bounding boxes.

How it works:
1. The incoming ROS2 Image message is converted to an OpenCV frame using cv_bridge.
2. The frame goes through the YOLO model, which detects **only class 0 (person)** with a confidence of at least 0.5.
3. The bounding boxes are drawn on the frame and published as a new Image topic, so that RViz can display it.

### thermal_relay.py → thermal_relay
A simple relay node that forwards the thermal camera to the standard camera topic, so that the same detector can also run on thermal images.
- **Subscribe:** /thermal_camera_8bit/image
- **Publish:** /camera/image_raw

### make_screenshot.py → make_screenshot
A tool to collect training data by saving screenshots of the camera stream.

- **Subscribe:** /camera/image_raw
- Saves frames to vision/dataset/images/unlabeled/.
- **Controls:** press ENTER for a single screenshot, or SPACE to automatically take a screenshot every 2 seconds (toggle).

---

## Launch

launch/detection.launch.py starts the detector and RViz at the same time:

- person_detector node
- rviz2 with the config rviz/person_detection.rviz

```bash
ros2 launch person_detection detection.launch.py
```

---

## Building and running

### 1. Build the package
From the ROS2 workspace:

```bash
cd ~/ros2
colcon build --packages-select person_detection
source install/setup.bash
```

### 2. Start standalone person detection in RViz

**Terminal 1 - Gazebo:**

```bash
gz sim Gazebo/worlds/parking_garage.world &
```

**Terminal 2 - ROS2 bridge (Gazebo → ROS2):**

```bash
ros2 run ros_gz_bridge parameter_bridge \
/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image
```

**Terminal 3 - Detection + RViz:**

```bash
cd ros2
source install/setup.bash
ros2 launch person_detection detection.launch.py
```
---

## Result in RViz

The launch starts RViz automatically with the correct config. The annotated image is visible through an **Image** display on the topic /person_detection/image.

---

## Folder structure

| Path | Description |
| --- | --- |
| person_detection/detector.py | YOLO person detection node |
| person_detection/make_screenshot.py | Take screenshots for training data |
| launch/detection.launch.py | Start detector + RViz |
| rviz/person_detection.rviz | RViz configuration |
| setup.py | Package definition and entry points |
| package.xml | ROS2 package manifest |

---

## Dependencies

- ROS2 (Jazzy), rclpy, sensor_msgs
- cv_bridge (requires **NumPy 1.x**)
- ultralytics (YOLOv8), opencv-python
- ros_gz_bridge (for the Gazebo → ROS2 connection)

# Functions in detector.py
The node reads in the camera images, detects people with the YOLO model and draws the bounding boxes on the image. It also combines the detection with the lidar and odometry data to determine the distance to the person and their world position, and publishes both the annotated image and a marker for use in RViz. The functions are described below.

### detector.py

The node consists of a function find_model_path() and the class
PersonDetector, which loads the YOLO model and processes the camera images.

#### find_model_path()

Looks for the trained model file in several places. This ensures the node works both in a container and locally. The search order is first the environment variable TONK_REPO, then the fixed docker container location /workspace/vision/models/, and finally it looks from the script directory in each parent directory for vision/models/. The first location where the file is found is used. If the model file is not found anywhere, a FileNotFoundError follows with all the searched paths.

This function was implemented because during training the model may be placed in a different location and so that users without a docker container can also run it.

#### \_\_init\_\_
The constructor sets up the node: it registers the node under the name person_detector, loads the YOLO model via the found path and creates a CvBridge for the conversion between ROS2 and OpenCV. It then creates three subscribers: on /camera/image_raw (calls callback for each camera image), on /lidar/pointcloud (for the distance to the person) and on /odom (for the position of the robot). Finally it creates two publishers: on /person_detection/image for the annotated image with bounding boxes, and on /person_marker for the marker that shows the person on the lidar map in RViz.

#### odom_callback
The robot uses odometry to keep track of its location. It saves the current X and Y coordinates and uses its orientation readings to figure out which location it is facing. This data is needed to convert the detected person to a world position on the map.

#### lidar_callback
This function stores the latest lidar scan with a lock for thread safety so that object_distance_from_lidar() can later extract the distance from it. This distance is important for measuring the distance to the robot.

#### callback
Runs for each incoming camera image. The ROS2 Image message is converted to an OpenCV frame and the model detects only class 0 (person) with a minimum confidence of 50% (conf=0.5). For each detected person the confidence is tracked and the center of the bounding box (cx) is determined, with which publish_person_marker places a marker on the lidar map. The bounding boxes are then drawn on the frame and the result is published back to Rviz.

#### object_distance_from_lidar
Calculates how far the person is from the robot. From the stored lidar scan it looks for the nearest point in the direction of the person. Points that are too close to the robot itself are ignored. If the lidar sees nothing in that direction, 8m is returned as an estimate. This is the same approach as in fire_navigator.cc for the fire.

#### publish_person_marker
Places the detected person as a marker on the lidar map. First it calculates from the center of the bounding box (cx) the angle to the person relative to the camera. Using the lidar distance and the position + heading of the robot it calculates the world position of the person. There it publishes two markers on /person_marker: a green bar and a text label with "PERSOON" above it.

#### main
The entry point of the node: initializes ROS2, creates the PersonDetector and keeps it running with rclpy.spin() so that the callbacks keep processing. On shutdown the node is cleaned up properly.

## thermal_relay.py
The node consists of the class ThermalRelay. It forwards the images from the thermal camera to the standard camera topic.

#### init
The constructor sets up the node: it registers the node under the name thermal_relay and creates a publisher on /camera/image_raw. It then creates a subscriber on /thermal_camera_8bit/image, where each incoming message is forwarded via self.pub.publish to /camera/image_raw. The node only links the thermal camera topic to the topic the detector listens to.

#### main
The entry point of the node:
initializes ROS2, creates the ThermalRelay and keeps it running with rclpy.spin() so that the messages keep being forwarded.