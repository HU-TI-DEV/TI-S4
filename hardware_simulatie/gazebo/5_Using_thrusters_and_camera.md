# 5. Using thrusters and camera

## Thrusters
*Please note: the youtube link at the end of this chapter shows a demo of the following steps.*   
In this section we will see how to use thrusters. Thrusters are a way to simulate for instance propellers.<br>
The sdf can be found here: [thrusters.sdf](./files/thrusters.sdf)  
Copy it to your container. Run it with:
```
gz sim thruster.sdf &
```
The ```&``` command makes the gz sim run in the background.   
Make sure you start the simulation (triangle in the bottom left corner).
We can now (in the same container) still give commands in the container:

```
gz topic -t /model/cube_with_thruster/joint/thruster_joint/cmd_thrust -m gz.msgs.Double -p "data: 1.0"
```
The cube should behave like a rocket!  
See:   
[![YouTube Video Preview](https://img.youtube.com/vi/DtrU5ze-Ux8/0.jpg)](https://www.youtube.com/watch?v=DtrU5ze-Ux8)


## Camera
*Please note: the youtube link at the end of this chapter shows a demo of the following steps.*   
We will now introduce the camera sensor. The sdf can be found here: [camera.sdf](./files/camera.sdf)

Start the simulation:
```
gz sim camera.sdf &
```
The camera output the images. Let's see how the raw output looks like with:
```
gz topic -e -t /camera/image
```
See:  
[![YouTube Video Preview](https://img.youtube.com/vi/9yOtOGGP5xs/0.jpg)](https://www.youtube.com/watch?v=9yOtOGGP5xs)

## Camera with python visualisation
To make sense of the data stream I have build a small python program to show the output of the camera in a separate window. 
The program:
```python
#!/usr/bin/env python3
import gz.transport as gz
from gz.msgs import image_pb2
import numpy as np
import cv2
import time

TOPIC = "/camera/image"

node = gz.Node()

def image_cb(msg: image_pb2.Image):
    # Use numeric values for pixel format
    if msg.pixel_format_type == 3:   # RGB_INT8
        channels = 3
    elif msg.pixel_format_type == 4: # RGBA_INT8
        channels = 4
    elif msg.pixel_format_type == 1: # L_INT8
        channels = 1
    else:
        print("Unsupported pixel format:", msg.pixel_format_type)
        return

    img = np.frombuffer(msg.data, dtype=np.uint8)
    img = img.reshape((msg.height, msg.width, channels))

    if channels == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif channels == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

    cv2.imshow("Gazebo Camera", img)
    cv2.waitKey(1)

# Subscribe
node.subscribe(image_pb2.Image, TOPIC, image_cb)

print(f"Subscribed to {TOPIC}. Press Ctrl+C to exit.")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")

cv2.destroyAllWindows()
```
Save it as show_camera.py in your container. 

Run it with:
```
python3 show_camera.py
```

See:  
[![YouTube Video Preview](https://img.youtube.com/vi/R3QMzlAZnzo/0.jpg)](https://www.youtube.com/watch?v=R3QMzlAZnzo)

How cool is that!!!

## Camera with object recognigtion in python
We will now add some vision techniques to detect the cube. There is a separate lecture series on vision techniques (this is just a quick peek ahead):

The program:
```python
#!/usr/bin/env python3
import gz.transport as gz
from gz.msgs import image_pb2
import numpy as np
import cv2
import time

TOPIC = "/camera/image"

node = gz.Node()

def image_cb(msg: image_pb2.Image):
    # Determine number of channels
    if msg.pixel_format_type == 3:   # RGB_INT8
        channels = 3
    elif msg.pixel_format_type == 4: # RGBA_INT8
        channels = 4
    elif msg.pixel_format_type == 1: # L_INT8
        channels = 1
    else:
        print("Unsupported pixel format:", msg.pixel_format_type)
        return

    # Convert message to numpy array
    img = np.frombuffer(msg.data, dtype=np.uint8)
    img = img.reshape((msg.height, msg.width, channels))

    # Convert to BGR for OpenCV
    if channels == 3:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    elif channels == 4:
        img = cv2.cvtColor(img, cv2.COLOR_RGBA2BGR)

    # ----- Red rectangle detection -----
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Red color range (two ranges because red wraps around 180 hue)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 | mask2

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Draw green rectangle

    # Show image
    cv2.imshow("Gazebo Camera", img)
    cv2.waitKey(1)

# Subscribe
node.subscribe(image_pb2.Image, TOPIC, image_cb)

print(f"Subscribed to {TOPIC}. Press Ctrl+C to exit.")

try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")

cv2.destroyAllWindows()
```

The demo (execute it yourself, you know the steps by now I hope...):  
[![YouTube Video Preview](https://img.youtube.com/vi/lhfKNJloKxw/0.jpg)](https://www.youtube.com/watch?v=lhfKNJloKxw)

### END OF THIS MD...
For the next step:  
[6_Driving_the_robot](./6_Driving_the_robot.md)


