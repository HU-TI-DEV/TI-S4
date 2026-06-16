# YOLO Person Detection

*09/06/2026*<br>
*Maud Waasdorp*<br>
*Radeiaan Nandoe*

# Table of Contents

- [YOLO Person Detection](#yolo-person-detection)
- [Table of Contents](#table-of-contents)
- [What's in this folder](#whats-in-this-folder)
- [Reasoning](#reasoning)
- [Implementation](#implementation)
  - [1. Image Conversion](#1-image-conversion)
  - [2. YOLO Model Loading](#2-yolo-model-loading)
  - [3. Running Inference](#3-running-inference)
  - [4. Person Detection](#4-person-detection)
  - [5. Drawing \& Visualisation](#5-drawing--visualisation)
  - [6. Gazebo Integration](#6-gazebo-integration)
- [Conclusion](#conclusion)
- [Setup](#setup)
  - [3-Terminal setup](#3-terminal-setup)
- [Errors \& Debug](#errors--debug)
- [Advice](#advice)
- [Sources](#sources)

# What's in this folder

In this folder is **the whole process of detecting people/victims inside Gazebo using YOLO object detection**. The Python script subscribes directly to a Gazebo camera topic, processes incoming images and uses a *pretrained* YOLO model to detect people in real-time.

The final result is a lightweight victim/person detection system capable of:

* Detecting people
* Drawing bounding boxes
* Estimating object confidence
* Calculating object center points
* Visualising detections live using OpenCV

The detection results are also printed **directly** into terminal output for debugging and future robotics integration.

# Reasoning

The purpose of this implementation is to allow FLIP to recognise people or victims inside simulated environments. In robotics and rescue scenarios, detecting humans is one of the most important tasks because it allows the robot to:

* Locate victims
* Identify human presence
* Navigate toward targets
* Gather environmental awareness

Unlike the previous contour-based object detection pipeline, this implementation uses **YOLO (You Only Look Once)**. YOLO is a deep-learning based object detection model trained on large datasets such as COCO.

The advantage of YOLO compared to traditional computer vision:

* Better real-world detection
* Handles complex scenes
* More reliable person recognition
* Works under more difficult lighting conditions
* Detects multiple objects simultaneously

The disadvantage is that it is:

* More computationally expensive
* More difficult to debug internally
* Dependent on pretrained AI models

Still, for victim/person recognition this approach is significantly more accurate than contour or color-based detection.

# Implementation

The YOLO detection pipeline consists of several stages. Every incoming camera frame is processed through these steps before the final detections are visualised.

## 1. Image Conversion

The first step is converting the Gazebo image message into an OpenCV image. Gazebo publishes raw image byte data, which OpenCV cannot process directly.

Inside `gz_image_to_bgr()`:

```python id="w8w1mj"
img = np.frombuffer(
    msg.data,
    dtype=np.uint8)
```

The image data is reshaped into proper height-width dimensions:

```python id="e4z7tt"
img = img.reshape(
    (msg.height, msg.width, channels))
```

Depending on the incoming image type:

* RGB
* RGBA
* Grayscale

the image gets converted into OpenCV BGR format:

```python id="0j7dzm"
return cv2.cvtColor(
    img,
    cv2.COLOR_RGB2BGR)
```

*This conversion step is required because OpenCV internally uses BGR instead of RGB.*

---

## 2. YOLO Model Loading

After setting up the Gazebo connection, the YOLO model is loaded during initialisation of the application.

```python id="h7e2rb"
self.model = YOLO(model_path)
```

The model path can be configured using command-line arguments:

```python id="p9wlqg"
--model yolo11n.pt
```

This makes it possible to:

* Use pretrained YOLO models
* Use custom trained models
* Switch between lightweight and larger networks

**Example:**

```bash id="gm7m8o"
python yolo_people.py --model yolo11n.pt
```

When the application starts, the loaded model is printed:

```python id="ghg95i"
print(f"Loaded YOLO model: {model_path}")
```

This helps verify that the correct weights are loaded successfully.

---

## 3. Running Inference

Every incoming camera frame is passed through the YOLO model for inference.

Before inference, the image gets converted from BGR back into RGB:

```python id="x4m7da"
img_rgb = cv2.cvtColor(
    img_bgr,
    cv2.COLOR_BGR2RGB
)
```

This is important because YOLO models are trained on RGB images.

The prediction step:

```python id="pd0f4k"
results = self.model.predict(
    source=img_rgb,
    imgsz=640,
    conf=self.conf,
    classes=classes,
    verbose=False,
)
```

Important parameters:

* `imgsz=640` → image resolution used for inference
* `conf=self.conf` → minimum confidence threshold
* `classes=classes` → filters object classes

This allows the system to balance:

* Detection accuracy
* Performance
* False positives

---

## 4. Person Detection

For pretrained COCO YOLO models:

```python id="fyob4q"
class 0 = person
```

By default, the script only detects people:

```python id="g7ukx7"
classes = [0]
```

This keeps the detection focused on victim/person recognition.

The model outputs:

* Bounding box coördinates
* Confidence score
* Class ID

**Example:**

```python id="rk4u8w"
confidence = float(box.conf[0])
class_id = int(box.cls[0])
class_name = self.model.names[class_id]
```

A readable label is then created:

```python id="wlyx5s"
label = f"{class_name} {confidence:.2f}"
```

Example output:

```python id="91n5z5"
person 0.87
```

The script also calculates object center points:

```python id="fwmn0y"
center_x = (x1 + x2) // 2
center_y = (y1 + y2) // 2
```

Detection information gets printed directly into terminal:

```python id="b5zj5m"
print({
    "class": class_name,
    "confidence": round(confidence, 3),
    "bbox": [x1, y1, x2, y2],
    "center_px": [center_x, center_y],
})
```

This can later be used for:

* Navigation
* Tracking
* Robot decision making
* Victim localisation

---

## 5. Drawing & Visualisation

After detections are calculated, they are drawn directly onto the image.

Bounding boxes:

```python id="3bvw9v"
cv2.rectangle(
    img_bgr,
    (x1, y1),
    (x2, y2),
    (0, 255, 0),
    2
)
```

Detection labels:

```python id="nkh97h"
cv2.putText(
    img_bgr,
    label,
    (x1, max(20, y1 - 8)),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.6,
    (0, 255, 0),
    2,
)
```

The final image is displayed using OpenCV:

```python id="5t6lxp"
cv2.imshow(
    "Gazebo YOLO People Detection",
    img_bgr
)
```

This creates a live detection window showing:

* People
* Confidence values
* Bounding boxes

in real-time.

---

## 6. Gazebo Integration

This implementation subscribes directly to Gazebo Transport topics and does not use ROS2, this is implemted later on with the [Object Detection](../object-human-detection) script.

The application subscribes to:

```python id="hh9q3m"
/front/image
```

using:

```python id="7lvx8o"
self.node.subscribe(
    image_pb2.Image,
    self.topic,
    self.image_cb
)
```

Every incoming frame automatically triggers the YOLO detection pipeline through the callback function.

The application continuously runs until interrupted:

```python id="rtu4nd"
while True:
    time.sleep(0.1)
```

This allows real-time AI-based victim/person detection directly inside Gazebo simulation environments.

# Conclusion

Using YOLO together with Gazebo and OpenCV creates a powerful real-time person detection system. Compared to traditional contour-based object detection, YOLO performs significantly better for:

* Human detection
* Complex scenes
* Realistic environments
* Multi-object detection

The final implementation can:

* Detect people in real-time
* Estimate confidence values
* Draw live overlays
* Calculate object positions
* Process Gazebo camera feeds directly

This creates a strong base for future robotics tasks where FLIP needs victim awareness and human detection capabilities.

# Setup

In order to run this YOLO detection system correctly, there are several setup requirements for Gazebo, Python and Ultralytics YOLO support.

1. Create Docker container
2. Install Gazebo
3. Create Python venv
4. Install required packages

Required Python packages:

```bash id="5ev2a4"
pip install ultralytics opencv-python numpy
```

*Depending on the system, PyTorch may also need [GPU/CUDA](../../../docker/setup/using-cuda/ReadME.md) support for better performance.*

## 3-Terminal setup

Gazebo + YOLO Detection Startup

| Terminal | Purpose                  |
| -------- | ------------------------ |
| 1        | Gazebo simulation        |
| 2        | Python YOLO detection    |
| 3        | Optional debugging/tools |

---

**TERMINAL 1** — Gazebo Simulator

```bash id="93ulv4"
gz sim <world-file>.sdf
```

*This starts the Gazebo world and camera sensor.*

---

**TERMINAL 2** — Python YOLO Detection

```bash id="6qu57h"
source /workspace/venv/bin/activate

cd <python-file-location>

python yolo_people.py
```

*This starts the YOLO victim/person detection pipeline.*

---

**TERMINAL 3** — Optional Topic Debugging

```bash id="y42bzi"
gz topic -l
```

*This shows all active Gazebo topics.*

# Errors & Debug

**ERROR: No module named ultralytics**

```bash id="m49klr"
ModuleNotFoundError: No module named 'ultralytics'
```

*Solution:*

```bash id="s7drkx"
pip install ultralytics
```

---

**ERROR: Model file not found**

```bash id="q9v8mh"
FileNotFoundError
```

*Solution:*
Make sure the YOLO model file exists:

```bash id="pwh2m4"
yolo11n.pt
```

or provide the correct path:

```bash id="ewww3n"
python yolo_people.py --model <model-path>
```

---

**ERROR: OpenCV window not showing**

```bash id="4lh0dq"
cv2.imshow not opening
```

*Solution:*

```bash id="mp8yz3"
export DISPLAY=:0
```

Or make sure GUI forwarding is enabled inside Docker.

---

**ERROR: CUDA/GPU not detected**

```bash id="lbjlwm"
CUDA unavailable
```

*Solution:*
The script will still work on CPU, but performance may be slower. Make sure CUDA and PyTorch GPU support are installed correctly if GPU acceleration is required.

# Advice

YOLO is significantly more powerful than traditional contour-based object detection when detecting people or victims. It works much better in:

* Complex environments
* Different lighting conditions
* Cluttered scenes
* Realistic simulations

However, because YOLO is AI-based, it is also more **computationally expensive**. On weaker hardware this can reduce FPS and increase inference time.

For robotics projects, confidence thresholds are very important. Lower confidence values can:

* Detect more objects
* Increase false positives

Higher confidence values:

* Reduce false detections
* May miss smaller or distant people

Future improvements could include:

* ROS2 and RViz visualisation (this is implemented in the project)
* Multi-camera detection
* Depth estimation
* Custom victim training datasets
* GPU acceleration

**This implementation already creates a strong base for victim/person detection tasks inside Gazebo simulations and future autonomous robotics systems.**

# Sources

* *Ultralytics YOLO Documentation. (z.d.). https://docs.ultralytics.com/*
* *OpenCV Documentation. (z.d.). https://docs.opencv.org/*
* *Gazebo Transport Documentation. (z.d.). https://gazebosim.org/api/transport/*
* *YOLO Object Detection Paper. (z.d.). https://pjreddie.com/darknet/yolo/*
