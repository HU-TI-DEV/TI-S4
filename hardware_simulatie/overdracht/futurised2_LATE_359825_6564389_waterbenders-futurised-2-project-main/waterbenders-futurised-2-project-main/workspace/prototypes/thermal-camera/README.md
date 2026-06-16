# Thermal Camera
*08/06/2026*<br>
*Maud Waasdorp*

# Table of Contents
- [Thermal Camera](#thermal-camera)
- [Table of Contents](#table-of-contents)
- [What's in this folder](#whats-in-this-folder)
- [Reasoning](#reasoning)
- [Implementation](#implementation)
  - [1. Testing](#1-testing)
  - [2. Colormap](#2-colormap)
    - [1. Raw data conversion](#1-raw-data-conversion)
    - [2. Normalization](#2-normalization)
    - [3. Colormap Rendering](#3-colormap-rendering)
    - [4. Create legend](#4-create-legend)
  - [3. Rviz](#3-rviz)
- [Choices](#choices)
- [Conclusion](#conclusion)
- [Setup](#setup)
  - [4-Terminal setup](#4-terminal-setup)
  - [What to do in Rviz](#what-to-do-in-rviz)
  - [Errors \& Debug](#errors--debug)
- [Advice](#advice)
- [Sources](#sources)

# What's in this folder
In this folder is the whole process of implementing **YOLO** person/victim detection inside Gazebo using **OpenCV and Ultralytics YOLO models**. The Python script subscribes directly to a Gazebo camera topic and processes incoming images in real-time using AI-based object detection

In the [test](./test) folder is the first working prototype (more on that below), in the [thermal-camera-rviz](./test-thermal-camera-rviz) folder is where there was improved on the prototype to fit correctly with the client's needs..

The final result is a detection pipeline capable of:

- Detecting people/victims
- Drawing bounding boxes
- Calculating confidence values
- Estimating object center points
- Visualising detections live using OpenCV

The detection results are also printed directly inside terminal for debugging and future robotics implementation.

# Reasoning
The thermal camera is a sensor in Gazebo which can determine temperature of designed objects in a Gazebo World. It does this by using `emissive` and `temperature` of objects inside an `.sdf` (Making Sure You’re Not A Bot!, z.d.). The thermal camera's raw output is a gradient of black-grey-white where white is the **hottest** object and black is the **coldest**. 

The decision to use this sensor is to be able to detect hot and even burning objects inside the simulation. This is of importance as the robot FLIP needs to:
- Locate victims
- Detect human presence
- Gather environmental awareness

# Implementation
In order to be able to let FLIP detect different temperatures of the area it needs to explore, the thermal camera must translate it's raw data into something useful for the human eye. There were a few steps in implementing this sensor and it's end result:

## 1. Testing 
In the first fase it was important to test the thermal camera inside a prototype environment to be able to see the output. Inside the [test](./test/Tcamera.py) folder there is a first draft of Python code which creates an image using OpenCV to see the grayscale. This image is refreshed constantly for real-time data insights. What happens in this code:
- It converts the raw data into a `numpy array`
- Calculates the temperature
- Prints the centre pixel temperature inside terminal
- Scales for visualisation
- Show processed image live
- Subscribes to the thermal camera topic

## 2. Colormap
After showing this first prototype to the client, the next steps could be taken in mind with the given feedback. Adding a colormap helps with visibility for easy reading and gathering information. In order to do this, the greyscale image from the first step must be translated to a heatmap image. In [thc-rviz.py](./test-thermal-camera-rviz/thc-rviz.py) this heatmap was implemented. 

Processing the thermal-to-heatmap conversion happens in ObjectTemperature node, which subscribes to `/front/image`, `/FLIP/thermal_camera`, and publishes processed outputs on `/thermal/heatmap_image`. The pipeline consists of several steps designed for clarity when presenting to end user teams who may not work directly with raw sensor payloads:

### 1. Raw data conversion
The initial step in `try_process()` method converts the incoming thermal image *(which arrives as a string buffer containing integer values)* into a readable format suitable for further calculation and visualization. Also the data is reshaped into *height-by-width* dimension to match the camera resolution. The temperature for the thermal camera is in Kelvin, next up in the code this is calculated into Celsius.
```python
thermal_raw = np.frombuffer(
    self.thermal.data,
    dtype=np.uint16
).reshape((self.thermal.height, self.thermal.width))

temp_celsius = (thermal_raw.astype(np.float32) * 0.01) - 273.15
```

### 2. Normalization
In order to map temperatures onto a color gradient, all calculated Celsius values must be scaled from full physical range into unitless indices between [0–1] for colormap application.

```python
norm = (temp_celsius - self.min_temp) / (self.max_temp - self.min_temp + 1e-6)
normalised_data_clipped = np.clip(norm, 0.0, 1.0)
heatmap_gray_uint8 = (normalized_by *255).astype(np.uint8)
```

`min_temp = 0.0C`, `max_temp = 300.0C` can be adjusted for different environments where fires or objects are at higher or lower temperature.

### 3. Colormap Rendering
The last step now is to create a colormap using the processed data using OpenCV. Using `applyColorMap()` function, it takes the grayscale heat values and maps them into a color palette using `cv2.COLORMAP_TURBO` (other heatmaps are also possible, like `cv2.COLORMAP_AUTUMN` or `cv2.COLORMAP_HOT`).
```python
heatmap_gray = (norm * 255).astype(np.uint8)
heatmap_color = cv2.applyColorMap(heatmap_gray, cv2.COLORMAP_TURBO)
heatmap_resized = cv2.resize(heatmap_color, (self.rgb.width, self.rgb.height))
```
### 4. Create legend
In order to see the actual temperatures of objects and not just a gradient of the grayscale, a legend is created where the temperature is corresponding to the correct color, check out this [video](./test-thermal-camera-rviz/TEST2-ThC-werkt.mp4). 
```python
def create_legend(self, height=300, width=60):
    legend = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        ratio = 1.0 - (i / height)
        color = cv2.applyColorMap(np.uint8([[int(ratio * 255)]]), cv2.COLORMAP_TURBO)[0][0]
        legend[i, :] = color
        if i % (height // 5) == 0:
            val = self.min_temp + ratio * (self.max_temp - self.min_temp)
            cv2.putText(legend, f"{int(val)}C", (5, i + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    return legend
```

## 3. Rviz
In order to visualise all the data from all the different sensors used in this project, Rviz and ROS2 will be used. ROS2 bridges between OpenCV and Rviz in order to correctly visualise the data in Rviz. This is also implemented in [thc-rviz.py](./thc-rviz.py). First it's important to subscribe to a topic and publish the created topic inside the Python code, this happens in the initialisation of `class ObjectTemperature(Node)`. In order to publish, `msg.header.frame_id` gets set to *“camera_frame”* which tells any viewer (like Rviz) how to place this image in world coördinate space so overlays line up correctly with FLIP and the Gazebo World.
```python
msg = self.bridge.cv2_to_imgmsg(display, encoding='bgr8')
msg.header.stamp = self.get_clock().now().to_msg()
msg.header.frame_id = "camera_frame"
self.pub_heatmap.publish(msg)
```

Check out this [video](./test-thermal-camera-rviz/TEST3-ThC-Rviz.mp4)

# Choices
One of the main problems with this script was in which way to let the thermal camera collect data from different temperatures in objects and surroundings. There were many tests done as to how this would work accordingly, as to be seen in [implementation](#implementation). With the clients feedback the heatmap was introduces, but this had to be specified for the environment simulation. 

At first with running these scripts, `emissive` was used as the 'main' way of reading temperature data, yet this was very troublesome. Imagine having to change `emissive` in every `model.sdf` and not knowing what temperature is assigned to an object. And even besides that, the position of the sun and strength of light in `room-v2.sdf` had to be regulated and calculated too.

In order to fix this, the next step was figuring out how `<temperature>` could actually be implemented in the correct way and calculated back to celsius. Since .sdf files can be very picky, there was one way found that worked:
```xml
<?xml version="1.0" ?>
<sdf version="1.10">
    <model name="blueBox1x2x1">
      <static>true</static>
      <pose>3 -2 0.5 0 0 0</pose>
      <link name="link">
        <temperature>300.0</temperature>
        <collision name="collision">
          <geometry><box><size>1 2 1</size></box></geometry>
        </collision>
        <visual name="visual">
          <geometry><box><size>1 2 1</size></box></geometry>
          <material>
            <ambient>0 0 1 1</ambient>
            <diffuse>0 0 1 1</diffuse>
          </material>
          <plugin
            filename="gz-sim-thermal-system"
            name="gz::sim::systems::Thermal">
            <temperature>343.15</temperature>
          </plugin>
        </visual>
      </link>
    </model>
</sdf>
```
By putting `<temperature>` inside `<link>` the temperature seemed to be configured in to the world file accordingly. If this is moved to somewhere like inside `<visual>`, the temperature will not be seen and could give some Gazebo errors. 

# Conclusion
Using the most improved version of this code, the data of the thermal camera is exact and clearly visible to the human eye. Also with Rviz and ROS2 implementation, the heatmap image is visible while also seeing the output of other sensors. 


# Setup
In order to be able to run these files, there are a few steps that need to be taken in order for it to work correctly with Gazebo, ROS2 and Rviz (Using Gazebo — (Murilo’s) ROS2 Tutorial, z.d.).
1. Create a Docker container -> [Docker container setup](../../../docker/setup/container-creation/README.md)
2. Install ROS2 -> [Installing ROS2](../../../setup/ROS2/README.md)
3. Create a venv inside the Docker container and install packages/libraries -> [venv setup](../../../docker/setup/container-venv/README.md)

If this setup is complete and functioning, the next step is to actually run this script. Important is that it is neccesary to have **4 powershell terminals** open, because in every terminal something else must be ran. It's easy to open these terminals in VS Code, use the shortcut `Ctrl + Shift + ~` to open a terminal, use `Crtl + Shift + 5` to open a split terminal.

## 4-Terminal setup

ROS2 + Gazebo + Thermal Pipeline Startup

| Terminal | Purpose                                |
| -------- | -------------------------------------- |
| 1        | Gazebo simulation (`gz sim`)           |
| 2        | ROS ↔ Gazebo bridge                    |
| 3        | Python thermal + YOLO + RViz publisher |
| 4        | RViz visualization                     |

**TERMINAL 1** — Gazebo Simulator
```bash
cd cd prototypes/thermal-camera
gz sim room-v2.sdf
```
*This runs the world + thermal camera plugin.*

---

**TERMINAL 2** — ROS ↔ Gazebo Bridge
```bash
source /opt/ros/jazzy/setup.bash
ros2 run ros_gz_bridge parameter_bridge \
/camera/image@sensor_msgs/msg/Image@gz.msgs.Image \
/FLIP/thermal_camera@sensor_msgs/msg/Image@gz.msgs.Image \
/front/image@sensor_msgs/msg/Image@gz.msgs.Image \
/rear/image@sensor_msgs/msg/Image@gz.msgs.Image
```
*This exposes Gazebo topics to ROS 2.*

---

**TERMINAL 3** — Python Processing Node
```bash
source /workspace/venv/bin/activate
source /opt/ros/jazzy/setup.bash
cd <pythonfile-location>    # In this folder: cd prototypes/thermal-camera
python <pythonfile>         # In this folder: python thc.rviz.py
```
*This runs the python file*

---
 **TERMINAL 4** — RViz Visualization
```bash
source /opt/ros/jazzy/setup.bash
rviz2
```
*This opens Rviz.*

## What to do in Rviz
**Thermal camera output from Python file**

*In RViz UI:*
1. Click **Add**
2. Select **Image**
3. Set topic to:
    `/thermal/heatmap_image/image`


## Errors & Debug
**ERROR: Wrong Numpy version:**
```bash
A module that was compiled using NumPy 1.x cannot be run in NumPy 2.4.6
```
*Solution:*
```bash
pip uninstall numpy
pip install numpy==1.26.4
```
Inside the `.ps1` file, everytime this runs it makes sure the correct version of Numpy is installed and *doesn't* update automatically. Make sure to check out the [`.ps1`](../../../docker/setup/container-start/example-ps1-file.txt) and use it to start and enter the container.

**ERROR: rclpy not found:**
```bash
ModuleNotFoundError: No module named 'rclpy'
```
*Solution:*
```bash
source /opt/ros/jazzy/setup.bash
```
---
**ERROR: Python package not found:**
```bash
ModuleNotFoundError: No module named 'ultralytics'
```
*Solution:*
```bash
source /workspace/venv/bin/activate
pip uninstall ultralytics
pip install ultralytics
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
The thermal camera is very useful for visualising temperatures inside rooms, buildings or other simulated environments. It is easy to adjust minimum and maximum temperature ranges depending on the situation, which makes the sensor flexible for many different robotics scenarios. Using this setup it becomes easy to run FLIP and monitor everything happening in real-time at the same time.

Within this project, fire detection is one of the biggest use cases for the thermal camera. Because thermal sensors focus on heat instead of visible light, they can detect temperature differences much more reliably than normal RGB cameras in situations involving:

- Fire
- Smoke
- Dark environments
- Low visibility conditions

One important thing to keep in mind is that temperatures need to be configured correctly inside the `model.sdf` files. The thermal camera depends **heavily** on these assigned temperatures. As long as:

- The plugin is configured correctly
- The topics match
- The `.sdf` files contain proper temperature values

then the sensor should work reliably without major issues.

**A very important limitation of the Gazebo thermal camera is that it often estimates temperatures when no explicit temperature is assigned to an object.** If a model does not contain a temperature definition, Gazebo falls back to `<emissive>` values. This basically represents how much light or energy is reflected/emitted by an object instead of its **actual** physical temperature.

Because of this:

- Thermal values are not always physically accurate
- Reflections can influence readings
- Objects without configured temperatures may appear incorrect

This is very important to keep in mind when processing the thermal data inside Python scripts. The raw thermal image often still needs **proper scaling** and conversion before temperatures become meaningful or visually correct.


**Future improvements could include:**
- Real-time fire localisation
- Thermal hotspot tracking
- Victim heat-signature detection
- Thermal + RGB sensor fusion

**Overall, the thermal camera is a very powerful sensor for robotics simulations and emergency-response scenarios, especially when combined with AI-based detection systems and environmental awareness pipelines.**


# Sources
- *Gazebo sensors: Thermal camera in gazebo SIM. (z.d.). https://gazebosim.org/api/sensors/6/thermalcameraigngazebo.html*
- *Gazebo Sensors: ThermalCameraSensor Class Reference. (z.d.). https://gazebosim.org/api/sensors/7/classgz_1_1sensors_1_1ThermalCameraSensor.html*
- *Making sure you’re not a bot! (z.d.). https://wiki.ros.org/hector_gazebo_thermal_camera*
- *Using gazebo — (Murilo’s) ROS2 tutorial. (z.d.). https://ros2-tutorial.readthedocs.io/en/latest/gazebo/usage.html*
