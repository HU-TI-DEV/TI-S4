# Object Detection

*09/06/2026*<br>
*Maud Waasdorp*<br>
*Radeiaan Nandoe*

# Table of Contents

- [Object Detection](#object-detection)
- [Table of Contents](#table-of-contents)
- [What's in this folder](#whats-in-this-folder)
- [Reasoning](#reasoning)
- [Implementation](#implementation)
  - [1. Image Processing](#1-image-processing)
  - [2. Object Segmentation](#2-object-segmentation)
  - [3. Dominant Color Detection](#3-dominant-color-detection)
  - [4. Shape Classification](#4-shape-classification)
  - [5. Drawing \& Visualisation](#5-drawing--visualisation)
  - [6. Gazebo Integration](#6-gazebo-integration)
- [Choices](#choices)
- [Conclusion](#conclusion)
- [Setup](#setup)
  - [3-Terminal setup](#3-terminal-setup)
- [Errors \& Debug](#errors--debug)
- [Advice](#advice)
- [Sources](#sources)

# What's in this folder

In this folder is **the whole process of detecting and classifying colored objects inside Gazebo using OpenCV**. The Python script subscribes to a Gazebo camera topic, processes incoming images in real-time and detects objects based on color and shape. The final result is an object detection pipeline that can determine:

* Object color
* Object shape
* Bounding box location
* Object center point

The detected objects are visualised directly onto the camera feed using OpenCV.

# Reasoning

The purpose of this object detection system is to allow FLIP to recognise simple objects inside a simulated Gazebo environment. Instead of using heavy AI or neural-network based detection models, this implementation uses traditional computer vision techniques. This makes the system:

* Fast
* Lightweight
* Easy to debug
* Easy to expand

The object detection works completely from image processing. It does **not** rely on hardcoded object mappings like:

```python
green = cylinder
blue = cube
```

Instead, the pipeline analyses the actual image itself using:

* HSV color segmentation
* Contour extraction
* Hue histogram analysis
* Geometric contour calculations

This means object labels are generated dynamically based on what the camera sees.

# Implementation

The object detection pipeline is divided into several processing stages. Every incoming camera frame goes through these steps before objects are detected and visualised.

## 1. Image Processing

The first step is converting the incoming Gazebo image into a format OpenCV can process correctly. Gazebo images arrive as raw byte data and can contain different pixel formats such as:

* RGB
* RGBA
* Grayscale

Inside `gz_image_to_bgr()` the raw data gets reshaped into a proper image array and converted into OpenCV BGR format.

```python
img = np.frombuffer(msg.data, dtype=np.uint8)
img = img.reshape((msg.height, msg.width, channels))
return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
```

This ensures all following OpenCV functions work correctly.

---

## 2. Object Segmentation

After converting the image, the next step is isolating colored objects from the background. This happens in HSV color space instead of RGB, because HSV is much more stable for color-based detection.

The image is converted using:

```python
hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
```

After conversion, a mask is created that filters out:

* Low saturation pixels
* Dark pixels
* Background noise

```python
lower = np.array([0, self.min_saturation, self.min_value])
upper = np.array([179, 255, 255])
mask = cv2.inRange(hsv, lower, upper)
```

To clean up the mask, morphological operations are used:

```python
mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
```

*This removes small noisy pixels and closes gaps inside detected objects.*

After segmentation, contours are extracted from the cleaned mask:

```python
contours, _ = cv2.findContours(
    mask,
    cv2.RETR_EXTERNAL,
    cv2.CHAIN_APPROX_SIMPLE
)
```

These contours become the base for all following object calculations.

---

## 3. Dominant Color Detection

Once contours are detected, the dominant color inside every contour is calculated.

First, a contour mask is created:

```python
cv2.drawContours(
    contour_mask,
    [contour],
    -1,
    255,
    -1
)
```

Only pixels **inside** the object are used:

```python
pixels = hsv[contour_mask == 255]
```

To remove unstable colors and noise, low saturation and low brightness pixels are filtered out:

```python
pixels = pixels[
    (pixels[:, 1] >= self.min_saturation) &
    (pixels[:, 2] >= self.min_value)
]
```

The system then builds a hue histogram to determine the most dominant hue value:

```python
hue_hist = np.bincount(hues, minlength=180)
dominant_hue = int(np.argmax(hue_hist))
```

This hue gets mapped to a readable color name:

```python
color_name = self.closest_color_name(dominant_hue)
```

Examples:

* red
* green
* blue
* yellow
* purple

This makes the object labels understandable for humans instead of only numerical HSV values.

---

## 4. Shape Classification

After detecting object color, the contour geometry is analysed to estimate object shape.

Several geometric calculations are used:

* Contour vertices
* Aspect ratio
* Circularity
* Extent
* Solidity

```python
approx = cv2.approxPolyDP(
    contour,
    0.035 * perimeter,
    True
)
```

The amount of vertices helps identify **basic shapes**:

```python
if vertices == 3:
    return "triangle"

if vertices == 4:
    return "cube"
```

Circularity is used for **sphere-like objects**:

```python
circularity = (
    4.0 * np.pi * area /
    (perimeter * perimeter)
)
```

Additional calculations such as extent and solidity help classify **more difficult shapes** like cylinders.

The current implementation can classify:

* Triangle
* Cube
* Box
* Sphere
* Cylinder

*Because this is 2D vision only, **some** depth ambiguity can still happen depending on camera angle.*

---

## 5. Drawing & Visualisation

After all object information is calculated, the detections are drawn onto the image.

For every object the system draws:

* Bounding box
* Center point
* Object label

```python
cv2.rectangle(
    img_bgr,
    (x, y),
    (x + w, y + h),
    draw_color,
    2
)
```

The object label combines color and shape:

```python
label = f"{color_name} {object_type}"
```

Example labels:

* red cube
* blue sphere
* green cylinder

The final processed frame is visualised using OpenCV:

```python
cv2.imshow(
    "Gazebo Object Recognition",
    img
)
```

This creates a real-time object detection window.

---

## 6. Gazebo Integration

The complete detection system works directly with Gazebo Transport topics. The script subscribes to:

```python
/front/image
```

This happens inside:

```python
self.node.subscribe(
    image_pb2.Image,
    self.topic,
    self.image_cb
)
```

Every incoming frame automatically triggers the detection pipeline through the callback function.

The application continuously runs until interrupted:

```python
while True:
    time.sleep(0.1)
```

This allows real-time object recognition directly inside the Gazebo simulation.

# Choices
During this process there were two big ways to be able to detect objects: using **contours** and using **houghlines**. 

The first test file was used with the contours method, finding the contours of objects with `cv2.findContours()`, yet a big problem while running this file with Gazebo, was the lighting. Because of the lighting and walls, the script would detect the walls as triangles. Or even not see a cube, but detect a triangle from its shadow. 

These things had to be fixed so the next thing to test was using `cv2.HoughLines()`, but this method seemed to be even worse. It would not detect the shadows as much, but the `vertices` (corners) and outer edge lines of objects were barely visible. There were alot of gaps within the shapes, so the script could not use these lines as specificly to be able to detect shapes with it. So it was back to `cv2.findContours()`.

In order to make sure the object detection wouldn't detect the walls, there was a way to distinguish te objects from eachother, using the RGB camera and colors. With this the `vertices` were more clear by reading each pixel color of an object and create a `mask`. This way it filters out low-saturation and low-brightness pixels (background noise). This also helped with not detecting shadows of objects. 

Besides using `vertices`, `aspect_ratio` and `circularity`, with adding `solidity` and `extent` the objects could be filtered more. This helped with checking the robustness and the *actual* shape of an object like a cilinder. By making calculations with these variables it improved the quality of the object detection.

# Conclusion

Using OpenCV and contour-based image processing, the object detection pipeline is able to detect and classify colored objects inside Gazebo in real-time. The final result is lightweight, stable and easy to expand with future improvements.

Compared to AI-based object detection systems, this implementation is significantly simpler and faster while still giving reliable detection results for controlled simulation environments.

The pipeline can already:

* Detect colored objects
* Estimate dominant color
* Estimate object shape
* Draw real-time overlays
* Process live Gazebo camera feeds

This creates a strong base for future robotics tasks where FLIP needs environmental awareness.

# Setup

In order to run this object detection pipeline correctly, there are a few setup steps required for Gazebo, Python and OpenCV support.

1. Create Docker container
2. Install Gazebo
3. Create Python venv
4. Install required packages

**Required Python packages:**

```bash
pip install opencv-python numpy
```

Gazebo Transport Python bindings must also be installed correctly.

## 3-Terminal setup

Gazebo + Object Detection Startup

| Terminal | Purpose                  |
| -------- | ------------------------ |
| 1        | Gazebo simulation        |
| 2        | Python object detection  |
| 3        | Optional debugging/tools |

---

**TERMINAL 1** — Gazebo Simulator

```bash
gz sim <world-file>.sdf
```

*This starts the Gazebo world and camera sensor.*

---

**TERMINAL 2** — Python Object Detection

```bash
source /workspace/venv/bin/activate

cd <python-file-location>

python objectdetectioncamerav2.py
```

*This starts the OpenCV object detection pipeline.*

---

**TERMINAL 3** — Optional Topic Debugging

```bash
gz topic -l
```

*This shows all active Gazebo topics.*

# Errors & Debug

**ERROR: Unsupported pixel format**

```bash
Unsupported pixel format
```

*Solution:*
Make sure the Gazebo camera publishes:

* RGB_INT8
* RGBA_INT8
* L_INT8

Other formats are currently unsupported.

---

**ERROR: OpenCV window not showing**

```bash
cv2.imshow not opening
```

*Solution:*

```bash
export DISPLAY=:0
```

Or make sure GUI forwarding is enabled inside Docker.

---

**ERROR: No module named cv2**

```bash
ModuleNotFoundError: No module named 'cv2'
```

*Solution:*

```bash
pip install opencv-python
```

---

**ERROR: No module named gz**

```bash
ModuleNotFoundError: No module named 'gz'
```

*Solution:*
Make sure Gazebo Transport Python bindings are installed correctly inside the container/environment.

# Advice

This object detection system is very useful for lightweight robotics simulations where speed and simplicity are more important than AI-level object understanding. Because the implementation uses classical computer vision instead of machine learning, it is:

* Easier to debug
* Easier to tune
* Easier to understand
* Less computationally expensive

The HSV segmentation is especially important for stable detection. Small changes in:

* Saturation thresholds
* Brightness thresholds
* Minimum contour area

can greatly improve or reduce detection quality depending on the environment and lighting.

*One important limitation is that this system only uses 2D image processing. Because of this, certain objects can still look similar depending on perspective or camera angle.*

Future improvements could include:

* Depth camera integration
* Multi-camera support
* Object tracking
* AI/YOLO integration (this is implemented in this project too)
* ROS2 + RViz visualisation (this is implemented in the combined object + human detection script)
* 3D object estimation

**Still, for simulation environments and structured worlds, this pipeline performs very reliably and gives clear visual feedback in real-time.**

# Sources

* *OpenCV Documentation. (z.d.). https://docs.opencv.org/*
* *Gazebo Transport Documentation. (z.d.). https://gazebosim.org/api/transport/*
* *OpenCV Contours Tutorial. (z.d.). https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html*
* *OpenCV Morphological Operations. (z.d.). https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html*
