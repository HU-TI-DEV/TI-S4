# Fire Detection
*10/06/2026*<br>
*Maud Waasdorp*

# Table of Contents

- [Fire Detection](#fire-detection)
- [Table of Contents](#table-of-contents)
- [What's in this folder](#whats-in-this-folder)
- [Reasoning](#reasoning)
- [Implementation](#implementation)
  - [1. RGB and Thermal Subscription](#1-rgb-and-thermal-subscription)
  - [2. Thermal Fire Detection](#2-thermal-fire-detection)
  - [3. RGB Fire Colour Detection](#3-rgb-fire-colour-detection)
  - [4. Motion Detection](#4-motion-detection)
  - [5. Final Fire Decision](#5-final-fire-decision)
  - [6. Heatmap and Visualisation](#6-heatmap-and-visualisation)
  - [Conclusion](#conclusion)
- [Setup](#setup)
  - [4-Terminal setup](#4-terminal-setup)
  - [What to do in Rviz](#what-to-do-in-rviz)
  - [Errors \& Debug](#errors--debug)
- [Advice](#advice)
- [Sources](#sources)

# What's in this folder

In this folder is the complete process of implementing **fire detection** inside Gazebo using **ROS2, OpenCV and Python**. The node subscribes to both the **RGB camera** and the **thermal camera**, compares the incoming data and combines this with motion detection to determine if a fire is present inside the simulation.

The Python script subscribes directly to Gazebo camera topics through ROS2 and processes incoming images in **real-time**. The result is a multi-layer detection pipeline which uses several indicators before deciding that a fire is actually present.

The final result is a detection pipeline capable of:

* Detecting high temperatures using a thermal camera
* Detecting fire-like colours in RGB images
* Detecting movement between image frames
* Filtering false positives caused by robot movement
* Publishing fire status information to ROS2 topics
* Visualising detections live using OpenCV and Rviz

*The detection results are also published on a ROS2 topic and displayed directly inside the visualisation output for debugging and future robotics implementation.*

# Reasoning

Fire detection is one of the most important tasks in emergency-response robotics. The robot FLIP should be able to identify dangerous situations before entering an area or while exploring unknown environments.

A single sensor is often not enough to reliably determine if something is actually fire. For example:

* A thermal camera can detect hot objects that are not burning.
* An RGB camera can detect orange or red colours that are not fire.
* Motion can occur without a fire being present.

Because of this, the implementation combines **multiple detection** methods into a single decision-making process.

The thermal camera is used to detect temperatures above a specified threshold. The RGB camera is used to identify colours commonly associated with flames. Finally, motion detection is used to determine whether the detected object is actively changing over time, which is a common characteristic of fire.

*Combining these three detection methods significantly reduces false positives and creates a more reliable detection system for robotics applications.*

# Implementation

The implementation consists of several stages. Each stage contributes a different type of information which is later combined into the final fire detection result.

## 1. RGB and Thermal Subscription

The first step is subscribing to the required ROS2 topics.

The node subscribes to:

* `/front/image`
* `/FLIP/thermal_camera`
* `/cmd_vel`

The RGB camera is used for colour and motion analysis, while the thermal camera is used for temperature detection. The `/cmd_vel` topic is used to determine if FLIP is currently rotating.

```python
self.sub_rgb = self.create_subscription(
    Image,
    '/front/image',
    self.rgb_cb,
    10)

self.sub_thermal = self.create_subscription(
    Image,
    '/FLIP/thermal_camera',
    self.thermal_cb,
    10)
```

Before processing begins, the node waits until both camera frames are available.

```python
if self.rgb is None or self.thermal is None:
    return
```

*This prevents processing incomplete sensor data.*

## 2. Thermal Fire Detection

The thermal camera publishes **raw thermal** information which first needs to be converted into a **readable format**.

The thermal image arrives as a **buffer** containing temperature values. This data is converted into a `NumPy array` and reshaped into image dimensions.

```python
thermal_raw = np.frombuffer(
    self.thermal.data,
    dtype=np.uint16
).reshape((self.thermal.height, self.thermal.width))
```

The thermal camera stores temperatures in **Kelvin**. These values are converted into **Celsius**.

```python
temp_celsius = (
    thermal_raw.astype(np.float32) * 0.01
) - 273.15
```

After conversion, all pixels above a predefined temperature threshold are selected.

```python
thermal_fire_mask = (
    temp_celsius > self.fire_temp_threshold
).astype(np.uint8)
```

The number of hot pixels is counted and compared against a threshold.

```python
hot_pixels = np.sum(thermal_fire_mask)
thermal_fire_detected = hot_pixels > 500
```

Current settings:

* `fire_temp_threshold = 80°C`
* `min_temp = 0°C`
* `max_temp = 300°C`

These values can be adjusted depending on the environment being simulated.

## 3. RGB Fire Colour Detection

The thermal camera alone is not enough to determine if something is actually fire. Therefore the RGB image is analysed as well.

The RGB image is first converted to **HSV** colour space.

```python
hsv = cv2.cvtColor(
    rgb_image,
    cv2.COLOR_BGR2HSV
)
```

*HSV is used because colour filtering becomes significantly easier compared to standard RGB values.*

A colour range is defined which captures common flame colours (these can be easily adjusted if needed).

```python
lower_fire = np.array([5, 100, 100])
upper_fire = np.array([35, 255, 255])
```

Using this range, a fire colour mask is generated.

```python
rgb_fire_mask = cv2.inRange(
    hsv,
    lower_fire,
    upper_fire)
```

Noise is removed using **morphological operations**.

```python
kernel = np.ones((5, 5), np.uint8)

rgb_fire_mask = cv2.morphologyEx(
    rgb_fire_mask,
    cv2.MORPH_OPEN,
    kernel)

rgb_fire_mask = cv2.morphologyEx(
    rgb_fire_mask,
    cv2.MORPH_DILATE,
    kernel)
```

The amount of detected fire-coloured pixels is then calculated.

```python
fire_pixels = cv2.countNonZero(
    rgb_fire_mask)
rgb_fire_detected = fire_pixels > 300
```

**If enough fire-coloured pixels are present, the RGB detection stage reports a positive result.**

## 4. Motion Detection

Fire is dynamic and continuously changing shape. Because of this, motion detection is used as an additional validation step.

The RGB image is converted into grayscale.

```python
gray = cv2.cvtColor(
    rgb_image,
    cv2.COLOR_BGR2GRAY)
```

The current frame is compared against the previous frame.

```python
diff = cv2.absdiff(
    gray,
    self.previous_gray)
```

The difference image is thresholded to isolate significant changes.

```python
_, motion_mask = cv2.threshold(
    diff,
    25,
    255,
    cv2.THRESH_BINARY)
```

Noise is removed using another **morphological operation**.

```python
motion_mask = cv2.morphologyEx(
    motion_mask,
    cv2.MORPH_OPEN,
    kernel)
```

The amount of movement is then calculated.

```python
moving_pixels = cv2.countNonZero(
    motion_mask)
```

An important addition is checking whether FLIP is currently turning.

```python
if self.angular_velocity > 0.3:
    motion_detected = False
else:
    motion_detected = moving_pixels > 400
```

*Without this check, robot movement itself would generate large amounts of motion and produce **false positives**.*

## 5. Final Fire Decision

The final fire detection result combines **all** previous stages.

A fire is only detected when:
* Thermal detection is positive
* RGB colour detection is positive
* Motion detection is positive

```python
fire_detected = (
    thermal_fire_detected and
    rgb_fire_detected and
    motion_detected)
```

*This makes the system significantly more reliable than relying on a single sensor.*

When a fire is detected, a warning is displayed and a status message is published.

```python
status = String()
status.data = 'FIRE'
self.pub_status.publish(status)
```

If no fire is detected:

```python
status = String()
status.data = 'NO_FIRE'
self.pub_status.publish(status)
```

## 6. Heatmap and Visualisation
To improve readability for operators, the thermal data is converted into a colour heatmap.

The temperature values are first **normalised**.

```python
norm = (temp_celsius - self.min_temp) / (self.max_temp - self.min_temp + 1e-6)
norm = np.clip(norm, 0.0, 1.0)
```

The normalised values are converted into grayscale.

```python
heatmap_gray = (
    norm * 255
).astype(np.uint8)
```

OpenCV then converts the grayscale image into a heatmap.

```python
heatmap_color = cv2.applyColorMap(
    heatmap_gray,
    cv2.COLORMAP_TURBO)
```

The heatmap is resized to match the RGB camera resolution.

```python
heatmap_resized = cv2.resize(
    heatmap_color,
    (rgb_w, rgb_h))
```

Additional debugging information is drawn onto the RGB image:

* Fire status
* Centre temperature
* Hot pixel count
* Motion state
* RGB fire contours
* Motion contours

Finally, both images are combined into one output.

```python
combined = cv2.hconcat([
    debug,
    heatmap_resized])
```

**The combined image is then published to ROS2 for visualisation inside Rviz.**

## Conclusion

Using a combination of thermal detection, RGB colour detection and motion analysis creates a much more robust fire detection system than using a single sensor.

The final implementation provides clear visual feedback, publishes useful ROS2 topics and can easily be expanded for future robotics applications. The node performs all processing in real-time and integrates directly with the existing FLIP simulation environment.

# Setup
In order to be able to run these files, there are a few steps that need to be taken in order for it to work correctly with Gazebo, ROS2 and Rviz.

1. Create a Docker container -> [Docker container setup]()
2. Install ROS2 -> [Installing ROS2](../../models/README.md)
3. Create a venv inside the Docker container and install packages/libraries -> [venv setup](../../models/README.md)

If this setup is complete and functioning, the next step is to actually run this script. Important is that it is necessary to have **4 powershell terminals** open, because in every terminal something else must be ran.

## 4-Terminal setup

ROS2 + Gazebo + Fire Detection Startup

| Terminal | Purpose                      |
| -------- | ---------------------------- |
| 1        | Gazebo simulation (`gz sim`) |
| 2        | ROS ↔ Gazebo bridge          |
| 3        | Python fire detection node   |
| 4        | RViz visualisation           |

**TERMINAL 1** — Gazebo Simulator

```bash
cd prototypes/fire-detection
gz sim room-v2.sdf
```

*This runs the world and thermal camera plugin.*

---

**TERMINAL 2** — ROS ↔ Gazebo Bridge

```bash
source /opt/ros/jazzy/setup.bash

ros2 run ros_gz_bridge parameter_bridge \
/front/image@sensor_msgs/msg/Image@gz.msgs.Image \
/FLIP/thermal_camera@sensor_msgs/msg/Image@gz.msgs.Image \
/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist
```

*This exposes Gazebo topics to ROS2.*

---

**TERMINAL 3** — Python Processing Node

```bash
source /workspace/venv/bin/activate
source /opt/ros/jazzy/setup.bash

cd <pythonfile-location>
python fire_detection.py
```

*This runs the fire detection node.*

---

**TERMINAL 4** — RViz Visualisation

```bash
source /opt/ros/jazzy/setup.bash
rviz2
```

*This opens Rviz.*

## What to do in Rviz

**Fire detection output from Python file**

1. Click **Add**
2. Select **Image**
3. Set topic to:<br>
    `/thermal/heatmap_image`

**Fire detection status topic**

Monitor:

```bash
/fire_detection/status
```

## Errors & Debug

**ERROR: Wrong Numpy version:**

```bash
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.x
```

*Solution:*

```bash
pip uninstall numpy
pip install numpy==1.26.4
```

---

**ERROR: rclpy not found:**

```bash
ModuleNotFoundError: No module named 'rclpy'
```

*Solution:*

```bash
source /opt/ros/jazzy/setup.bash
```

---

**ERROR: cv_bridge not found:**

```bash
ModuleNotFoundError: No module named 'cv_bridge'
```

*Solution:*

```bash
source /opt/ros/jazzy/setup.bash
```

---

**ERROR: Pip install blocked:**

```bash
error: externally-managed-environment
```

*Solution:*

```bash
source /workspace/venv/bin/activate
pip install <package>
```

# Advice

This fire detection pipeline is a strong foundation for emergency-response robotics simulations like FLIP, because it combines multiple sources of information before making a decision.

Some important things to keep in mind:
* Thermal thresholds may need tuning per environment.
* RGB fire colours are sensitive to lighting conditions.
* Motion detection can produce false positives when the robot rotates.
* Topic names must exactly match the Gazebo bridge configuration.

A major advantage of this implementation is that every detection stage is visible inside the debug output, making troubleshooting and optimisation significantly easier.

**Future improvements could include:**

* Smoke detection
* Fire localisation and tracking
* Distance estimation
* Automatic robot response behaviour
* Multi-camera fire detection

**Overall, this implementation provides a reliable real-time fire detection system for Gazebo simulations and serves as a strong basis for future rescue and inspection robotics applications.**

# Sources

* *OpenCV Documentation. (z.d.). https://docs.opencv.org/*
* *ROS 2 Documentation. (z.d.). https://docs.ros.org/*
* *ROS2 sensor_msgs/Image Documentation. (z.d.). https://docs.ros2.org/*
* *cv_bridge Package Documentation. (z.d.). https://github.com/ros-perception/vision_opencv*
