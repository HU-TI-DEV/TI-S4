# Camera
*13/06/2026*<br>
*Django Manders*

# Table of Contents
- [Camera](#camera)
- [Table of Contents](#table-of-contents)
- [What's in this folder](#whats-in-this-folder)
- [Reasoning](#reasoning)
- [Implementation](#implementation)
  - [1. Camera sensor (SDF)](#1-camera-sensor-sdf)
  - [2. FLIP integration](#2-flip-integration)
  - [3. World setup](#3-world-setup)
  - [4. Python viewer](#4-python-viewer)
- [Setup](#setup)
  - [2-Terminal setup](#2-terminal-setup)
  - [Errors \& Debug](#errors--debug)
- [Advice](#advice)

# What's in this folder

This folder contains a prototype for adding an **RGB camera sensor** to the FLIP robot inside a Gazebo simulation. The camera is mounted on the chassis and streams live images that are received and displayed using a Python script with **OpenCV**.

| File / Folder | Description |
|---|---|
| `camera.sdf` | Standalone camera sensor model (640×480 RGB, 30 fps) |
| `FLIP.sdf` | Full FLIP robot model with the camera, LiDAR and IMU included |
| `roomWithObjectsTemplate.sdf` | Gazebo world with FLIP and coloured obstacle objects |
| `camera.py` | Python script that subscribes to the camera topic and shows the live feed |
| `obstakels/` | SDF models for obstacle shapes and walls used in the world |
| `camera+thermalcamera-RVIZ.mp4` | Recording of the camera and thermal camera combined in RViz |
| `rear+front-camera-openCV.mp4` | Recording of front and rear cameras displayed via OpenCV |

# Reasoning

In an emergency-response scenario, FLIP needs visual awareness of its surroundings to navigate, identify victims, and avoid obstacles. An RGB camera provides a live image feed that:
- Can be processed in real-time for object or human detection
- Can be combined with other sensors (LiDAR, thermal camera) for a richer environmental picture
- Serves as the foundation for computer-vision pipelines (OpenCV, YOLO, etc.)

This prototype focuses on getting the camera working inside Gazebo and displaying the output, as a basis for more advanced detection features.

# Implementation

## 1. Camera sensor (SDF)

The camera is defined in `camera.sdf` as a **static model** containing a `camera_link` with a sensor of type `camera`. Key parameters:

| Parameter | Value |
|---|---|
| Resolution | 640 × 480 px |
| Format | R8G8B8 (24-bit RGB) |
| Update rate | 30 Hz |
| Horizontal FOV | ~60° (1.047 rad) |
| Clip range | 0.1 m – 100 m |
| Topic | `/camera/image` |

## 2. FLIP integration

`FLIP.sdf` includes the camera model via an `<include>` tag and mounts it relative to the chassis:

```xml
<include>
  <uri>file:///workspace/prototypes/camera/camera.sdf</uri>
  <name>camera</name>
  <pose relative_to="chassis">0 0 2.05 0 0.3 0</pose>
</include>
```

The pose places the camera 2.05 m above the chassis centre and tilts it 0.3 rad downward so it sees the area in front of the robot. FLIP also carries:
- A **2D LiDAR** (640 samples, ±80°, 10 Hz) on the front of the chassis
- An **IMU sensor** (20 Hz) on the chassis body
- **Ackermann steering** plugin for driving via `/model/FLIP/cmd_vel`

## 3. World setup

`roomWithObjectsTemplate.sdf` defines a walled room (~8.4 × 7.8 m) containing FLIP and six coloured obstacle objects to give the camera something to see:

| Object | Colour | Approximate position |
|---|---|---|
| Cube 1×1×1 m | Red | (3, 2) |
| Cylinder ø0.5 × 1 m | Green | (−2, −3) |
| Box 1×2×1 m | Blue | (3, −2) |
| Box 1.5×1×1.5 m | Yellow | (−3, 2) |
| Ball ø0.6 m | Pink | (1, 3) |
| Box 0.8×0.8×0.8 m | Orange | (−2, 0) |

## 4. Python viewer

`camera.py` subscribes to `/camera/image` using **gz.transport** and renders each frame with **OpenCV**:

```python
TOPIC = "/camera/image"
node = gz.Node()

def image_cb(msg: image_pb2.Image):
    img = np.frombuffer(msg.data, dtype=np.uint8)
    img = img.reshape((msg.height, msg.width, channels))
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imshow("Gazebo Camera", img)
    cv2.waitKey(1)

node.subscribe(image_pb2.Image, TOPIC, image_cb)
```

Pixel format is detected automatically — RGB (format 3), RGBA (format 4), and grayscale L (format 1) are all supported.

# Setup

Make sure the base environment is in order before running:
1. Create a Docker container → [Docker container setup]()
2. Install ROS2 → [Installing ROS2](../../models/README.md)
3. Create a venv inside the Docker container and install packages → [venv setup](../../models/README.md)

## 2-Terminal setup

| Terminal | Purpose |
|---|---|
| 1 | Gazebo simulation (`gz sim`) |
| 2 | Python camera viewer |

**TERMINAL 1** — Gazebo Simulator
```bash
cd /workspace/prototypes/camera
gz sim roomWithObjectsTemplate.sdf
```
*Loads the room world with FLIP and all obstacle objects.*

---

**TERMINAL 2** — Python Camera Viewer
```bash
source /workspace/venv/bin/activate
cd /workspace/prototypes/camera
python camera.py
```
*Opens an OpenCV window with the live camera feed from Gazebo.*

Press **Ctrl+C** in terminal 2 to stop the script. The OpenCV window closes automatically.

## Errors & Debug

**ERROR: gz.transport not found**
```
ModuleNotFoundError: No module named 'gz.transport'
```
*Solution:* Make sure the gz-transport Python bindings are installed in the venv:
```bash
source /workspace/venv/bin/activate
pip install gz-transport
```

**ERROR: Unsupported pixel format**
```
Unsupported pixel format: <number>
```
*Solution:* The camera SDF uses `R8G8B8` (pixel format type 3). If you change the format in `camera.sdf`, update the format check in `camera.py` accordingly.

**ERROR: No image displayed / blank window**

Check that the Gazebo sensors plugin is loaded in the world SDF:
```xml
<plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
  <render_engine>ogre2</render_engine>
</plugin>
```
Without this plugin, camera sensors will not produce any output.

# Advice

This prototype is a clean starting point for adding vision to FLIP. A few things to keep in mind when building on top of it:

- **Camera placement matters.** The current 0.3 rad downward tilt means the camera looks slightly toward the ground. Adjust the `<pose>` in `FLIP.sdf` to match the desired field of view for your use case.
- **Combining with other sensors.** The videos in this folder show the camera working alongside the thermal camera in RViz. For a full perception stack, bridge all sensor topics to ROS2 and visualise them together in RViz.
- **Computer-vision pipelines.** `camera.py` is intentionally minimal — it only displays the image. Feed the `img` array directly into OpenCV processing functions or a YOLO model for detection. See the [objectHerkenningCV2](../objectHerkenningCV2) and [YOLO-HumanDetection](../YOLO-HumanDetection) prototypes for examples.
- **Performance.** At 30 fps and 640×480, the image stream is relatively lightweight. If the simulation slows down, lower `<update_rate>` in `camera.sdf` or reduce the resolution.
