# Hybrid Detection Pipeline
*10/06/2026*<br>
*Maud Waasdorp*<br>
*Radeiaan Nandoe*

# Table of Contents

- [Hybrid Detection Pipeline](#hybrid-detection-pipeline)
- [Table of Contents](#table-of-contents)
- [What's in this folder](#whats-in-this-folder)
- [Reasoning](#reasoning)
- [Implementation](#implementation)
  - [1. Hybrid Detection Approach](#1-hybrid-detection-approach)
  - [2. Gazebo Image Processing](#2-gazebo-image-processing)
  - [3. Detection Pipeline](#3-detection-pipeline)
  - [4. ROS2 Integration](#4-ros2-integration)
  - [5. Performance Optimisations](#5-performance-optimisations)
    - [Frame Skipping](#frame-skipping)
    - [Image Resizing](#image-resizing)
    - [Result Reuse](#result-reuse)
  - [6. Visualisation](#6-visualisation)
- [Choices](#choices)
- [Choices](#choices-1)
- [Conclusion](#conclusion)
- [Setup](#setup)
  - [3-Terminal setup](#3-terminal-setup)
  - [What to do in Rviz](#what-to-do-in-rviz)
  - [Errors \& Debug](#errors--debug)
- [Advice](#advice)
- [Sources](#sources)

# What's in this folder

In this folder is the complete implementation of a **hybrid detection pipeline** inside Gazebo using **YOLO, OpenCV, ROS2 and Gazebo Transport**. The goal of this implementation is to combine multiple detection techniques into a single perception pipeline which can be used by FLIP.

Instead of relying on only one detection method, this script combines:

* Human detection using YOLO
* Object detection using OpenCV
* Shape classification
* Colour classification
* ROS2 topic publishing
* Gazebo camera processing

This creates a single detection node capable of gathering information about both people and surrounding objects at the same time.

More detailed explanations of the individual detection systems can be found here:

* **YOLO Human Detection** -> [YOLO README](../YOLO-human-detection/ReadME.md)
* **OpenCV Object Detection** -> [Object Detection README](../object-detection-opencv/README.md)

The final result is a perception pipeline capable of:

* Detecting people
* Detecting coloured objects
* Classifying simple object shapes
* Estimating object colours
* Publishing images to ROS2
* Visualising detections live using OpenCV

*Detection results are also printed directly inside the terminal for debugging and future robotics implementation.*

# Reasoning

Within the FLIP project, **environmental awareness is one of the most important requirements.** The robot should not only be able to detect victims, but also understand what objects exist inside its surroundings.

Both detection systems already existed separately:
* YOLO for person detection
* OpenCV for object detection

The next logical step was combining both systems into a single pipeline.

This has a few advantages:
* Only one camera stream needs processing
* Detection results are centralised
* ROS2 integration becomes easier
* Performance can be managed in one location
* Future sensor fusion becomes easier

The result is a more scalable perception architecture where additional detection methods can be added later without completely redesigning the system.

# Implementation
The implementation consists of several stages. Rather than creating separate nodes for every task, this script combines everything into a single processing pipeline.

## 1. Hybrid Detection Approach
The implementation combines two separate detection systems:

**YOLO Human Detection:** YOLO is responsible for detecting victims or people inside the environment.

**OpenCV Object Detection:** OpenCV is responsible for detecting coloured Gazebo objects and classifying their properties.

*The hybrid pipeline combines both outputs into a single image and detection stream.*

## 2. Gazebo Image Processing

Unlike the previous implementations, this script subscribes **directly** to Gazebo Transport topics.

The incoming Gazebo image messages first need to be converted into OpenCV images.

```python
img = np.frombuffer(
    msg.data,
    dtype=np.uint8)
```

After conversion, the image is reshaped according to the image dimensions and pixel format.

```python
img = img.reshape(
    (msg.height,
     msg.width,
     channels))
```

The image is then converted into OpenCV BGR format.

```python
return cv2.cvtColor(
    img,
    cv2.COLOR_RGB2BGR)
```

This creates an image which can be processed by both YOLO and OpenCV.

## 3. Detection Pipeline

The image first enters the YOLO detection stage.

```python
people = self.person_detector.detect_people(
    img_bgr)
```

If people are detected, their bounding boxes can optionally be masked before object detection starts.

```python
ignore_boxes = [
    p["bbox_xyxy"]
    for p in people
]
```

*This prevents clothing colours or victim textures from being detected as generic objects.*

The image is then processed by the object detector.

```python
objects = self.object_detector.detect_objects(
    img_bgr,
    ignore_boxes_xyxy=ignore_boxes
)
```

The result is two separate detection lists:

* **People**
* **Objects**

These are then merged into a single visualisation output.

## 4. ROS2 Integration

Although the image originates from Gazebo Transport, the final output is published using ROS2.

The node publishes:

```python
/camera/image_raw
```

and

```python
/camera/image_annotated
```

The ROS2 publishers are created during initialisation.

```python
self.pub_raw = self.ros_node.create_publisher(
    Image,
    "/camera/image_raw",
    10
)

self.pub_annotated = self.ros_node.create_publisher(
    Image,
    "/camera/image_annotated",
    10
)
```

This makes the detection results available for Rviz and future robotics components.

## 5. Performance Optimisations

One challenge of combining multiple detection methods is **performance**.

Running YOLO and OpenCV every frame can quickly reduce frame rate. Because of this, several optimisations were implemented.

### Frame Skipping
Heavy processing only runs every few frames.
```python
self.process_every_n_frames = 3
```
*This reduces CPU and GPU load significantly.*

### Image Resizing
Incoming images are resized before processing.
```python
self.resize_scale = 0.5
```
*This decreases computation time while maintaining sufficient detection quality.*

### Result Reuse
When a frame is skipped, previous detections are reused.
```python
people = self.last_people
objects = self.last_objects
```
*This creates smoother visualisation while reducing processing requirements.*

## 6. Visualisation

After all detections have been completed, the results are drawn onto the image.

For every detected person:

* Bounding box
* Confidence score
* Centre point

For every detected object:

* Bounding box
* Colour classification
* Shape classification
* Centre point

The image is displayed using OpenCV.

```python
cv2.imshow(
    "Gazebo Hybrid Detection: YOLO People + OpenCV Objects",
    img_bgr)
```

*The same image is also published through ROS2 for visualisation inside Rviz.*

# Choices
To read the specific choices on either of these detectors, please check out their files ([object detection](../object-detection-opencv/README.md) and [human detection](../YOLO-human-detection/README.md).

Important to know is that those files were combined inside this script. It is definite that the script is long, but shortening it in any way possible, it decreased the quality a massive amount. In order to make sure the object and human detection work accordingly, all the line of code in this script is **neccesary and very useful.**

Besides that fact, in order for these scripts to run together, a function was added to make sure the object detection doesn't overwrite the human detection in `mask_out_boxes()`:
```py
def mask_out_boxes(
    self,
    img_bgr: np.ndarray,
    boxes_xyxy: List[List[int]],
    padding: int = 8,
) -> np.ndarray:
    """
    Black out person boxes before colored-object segmentation.

    This prevents colored clothing / textured person models from being
    detected again as generic colored objects.
    """
    masked = img_bgr.copy()
    img_h, img_w = masked.shape[:2]

    for box in boxes_xyxy:
        x1, y1, x2, y2 = clamp_box_xyxy(
            box,
            image_width=img_w,
            image_height=img_h,
            padding=padding,
        )
        masked[y1:y2, x1:x2] = (0, 0, 0)

    return masked
```

Then also in `detect_objects()`:
```py
def detect_objects(
    self,
    img_bgr: np.ndarray,
    ignore_boxes_xyxy: List[List[int]] | None = None,
    ignore_box_padding: int = 8,
) -> List[Dict[str, Any]]:
    """
    Main detection pipeline in single frame.
    Returns a list of detected objects with color, shape, and position data.

    NOTE: If ignore_boxes_xyxy is given, those boxes are blacked out first.
    This is useful for ignoring YOLO-detected people.
    """
    if ignore_boxes_xyxy:
        work_img = self.mask_out_boxes(
            img_bgr,
            ignore_boxes_xyxy,
            padding=ignore_box_padding,
        )
    else:
        work_img = img_bgr
```
Without this function the script will detect objects like 'Brown Box' by scanning a person's arm or body.

# Choices
This human detection script was implemented more at the end of the project, resulting in using an existing YOLO algorithm and intelligence instead of writing one. So in the future it might be worthwhile to write a script with a specific algoritm for this project. 

By using YOLO's existing human detector, it was pretty simple to implement withing our object detection. Classifying COCO YOLO with `class = 0` it's only focused on detecting people. In the future it could also be possible to even detect other objects like a couch, cat or dog. But because of the deadline this wasn't possible for this team.

# Conclusion

This implementation successfully combines multiple perception systems into a single processing pipeline.

Instead of running separate detection applications, the hybrid detector creates a central location for all visual perception tasks. This makes debugging easier, improves maintainability and provides a scalable foundation for future robotics development.

# Setup

In order to be able to run these files, there are a few steps that need to be taken in order for it to work correctly with Gazebo, ROS2 and Rviz.

1. Create a Docker container -> [Docker container setup](../../../docker/setup/container-creation/README.md)
2. Install ROS2 -> [Installing ROS2](../../../setup/ROS2/README.md)
3. Create a venv inside the Docker container and install packages/libraries -> [venv setup](../../../docker/setup/container-venv/README.md)

If this setup is complete and functioning, the next step is to actually run this script. Important is that it is necessary to have **3 powershell terminals** open, because in every terminal something else must be ran.

## 3-Terminal setup

ROS2 + Gazebo + Hybrid Detection Startup

| Terminal | Purpose               |
| -------- | --------------------- |
| 1        | Gazebo simulation     |
| 2        | Hybrid Detection Node |
| 3        | RViz visualisation    |

**TERMINAL 1** — Gazebo Simulator

```bash
cd prototypes/object-human-detection
gz sim room-v2.sdf
```

*This runs the world and camera sensors.*

---

**TERMINAL 2** — Hybrid Detection Pipeline

```bash
source /workspace/venv/bin/activate
cd prototypes/object-human-detection
python detect-objects.py
```

*This starts the hybrid detection node.*

---

**TERMINAL 3** — RViz Visualisation

```bash
source /opt/ros/jazzy/setup.bash
rviz2
```

*This opens Rviz.*

## What to do in Rviz

**Raw image output**

1. Click **Add**
2. Select **Image**
3. Set topic to:<br>
    `/camera/image_raw`

**Annotated image output**

1. Click **Add**
2. Select **Image**
3. Set topic to:<br>
    `/camera/image_annonated`

## Errors & Debug

**ERROR: YOLO model not found**

```bash
FileNotFoundError: yolo11n.pt
```

*Solution:*

Make sure the model exists inside the project directory or provide the correct path.

---

**ERROR: Gazebo topic unavailable**

```bash
Subscribed topic not found
```

*Solution:*

Verify that Gazebo is running and the camera topic exists.

```bash
gz topic -l
```

---

**ERROR: Ultralytics package not found**

```bash
ModuleNotFoundError: No module named 'ultralytics'
```

*Solution:*

```bash
pip install ultralytics
```

---

**ERROR: cv_bridge not found**

```bash
ModuleNotFoundError: No module named 'cv_bridge'
```

*Solution:*

```bash
source /opt/ros/jazzy/setup.bash
```

# Advice

This implementation is intended as a perception framework rather than a standalone detector.

The biggest advantage is that multiple detection methods can operate together while sharing the same camera stream. This makes future expansion significantly easier.

Future improvements could include:
* Victim tracking
* Multi-camera support
* Thermal camera integration (this is used in the [fire detection](../thermal-camera/fire-detection/README.md) file)
* Distance estimation
* Sensor fusion with LIDAR

One important thing to keep in mind is that YOLO and OpenCV both have **strengths and weaknesses**. Combining them creates a much more flexible perception system, but **performance** should always be monitored when additional detection modules are added.

**Overall, this hybrid detection pipeline provides a scalable foundation for environmental awareness, victim detection and future autonomous robotics behaviour within the FLIP project.**

# Sources

* *Ultralytics Documentation. (z.d.). https://docs.ultralytics.com/*
* *OpenCV Documentation. (z.d.). https://docs.opencv.org/*
* *Gazebo Transport Documentation. (z.d.). https://gazebosim.org/api/transport/*
* *ROS 2 Documentation. (z.d.). https://docs.ros.org/*
