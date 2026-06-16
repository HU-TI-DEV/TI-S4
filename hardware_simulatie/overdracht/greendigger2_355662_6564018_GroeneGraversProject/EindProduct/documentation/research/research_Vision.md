# Excavator
--

# Vision 

## OpenCV with a Depth Camera
We will use a depth camera to detect objects that are too close. This allows our excavator to skip a bund, thereby preventing damage to the product and protecting anyone who might jump in front of it. 

**Camera:**  
This camera operates in grayscale. The image it produces has a value between 0 and 255, where 255 represents the lightest color and indicates that an object is closest to the camera. 0 refers to anything so far away that it is no longer relevant to us. We need to determine a threshold for what constitutes “too close.” Next, we need to recognize these pixel colors. Our plan is to first apply a blur, which removes noise from the camera, and then we’ll identify clusters of a single color. In doing so, we’ll measure all objects that are too close and large enough (i.e., not just 5 pixels). 


Our tasks are as follows:
- [ ] Add depth camera -> place camera sensor in SDF 
- [ ] Position camera -> where should it go?
- [ ] Topics -> what topics are available? Such as depth and camera info
- [ ] Image transport -> sending and receiving images
- [ ] Test objects -> place objects in an SDF to see if it works
- [ ] Convert depth? -> convert data into usable information
- [ ] Measure distances -> which value corresponds to which distance?
- [ ] Reduce Noise -> add blurs to combat camera noise
- [ ] Thresholding -> detect minimum value for “too close”
- [ ] Test -> Test for camera latency


We’ve also created a schedule to keep track of when we’ll finish each task. We don’t have a lot of time left, so it’s important to know if we’re on track, and if not, to be able to raise the alarm right away:

| Week | Tasks                              |
| ---- | ---------------------------------- |
| 20   | Add and position camera   |
| 21   | Test image transport and objects |
| 22   | Measure distance and test for blur |
| 23   | Thresholding (cluster) and tests    |

---
## OpenCV met Camera

Slight change of plans: the depth camera hasn't been approved, so we'll now use a regular camera with edge detection. This will allow us to recognize what a tree looks like. This schedule runs from May 12 to June 5 and is as follows: 

| week |   Tasks   |
| ---- | --------- |
| 20   | Add and position the camera. We will add a camera in Gazebo. It will be mounted on the chassis later. For now, this camera must be functional, and it must be possible to subscribe to its topics.             |
| 21   | Image transport and edge detection. An image must now be captured by the camera and used for edge detection. This camera must save images somewhere and update that same image every 5 seconds (to prevent 1,000+ images from piling up). Then, using OpenCV, a blur filter must be applied, followed by edge detection. The blur is to filter out the noise, and the edge detection ensures that everything that is not important to us turns black. So we are left with only the lines that are important for recognizing shapes in the future. |
| 22   | Shape (and tree) recognition. This week we’ll be working on recognizing shapes. This is crucial for being able to recognize trees later on. For the MVP, a tree consists of a rectangle (since a cylinder looks like a rectangle in 2D) and a circle combined, so those shapes are important to recognize. We’ll also start working on recognizing trees when both of those shapes are present in the image.          |
| 23   | Tree recognition and communication. This week, we’ll finish up the final details for tree recognition if needed. The rest of the work will mainly involve bringing everything together. The camera is currently in a separate SDF, but of course it needs to be mounted on the chassis (not a lot of work, but it has to be done). We’ll also do some testing there with a few objects, placing multiple shapes and demonstrating that the shapes are recognized. This will also involve a test report.   |

## Tasks
- [x] Add camera
- [x] Position camera
- [x] Image transport
- [x] Blurs
- [x] Edge detection
- [x] Shape recognition
- [x] Tree recognition *(two objects touching each other are not recognized correctly)*
- [x] while loop
- [x] communication with the excavator arm
- [x] mount the camera on the chassis
- [x] test the camera on the chassis with test objects
- [x] test report 
- [x] README.md 

### Communication
File communication works as follows:
- We have one world containing: Chassis, Arm, Camera, Test Objects
- For obstacle detection, we have a `.py` file. This file uses OpenCV and runs continuously. When a tree is detected, that information is sent to a text file.
- In addition, for the Arm, we have a `.hh` and `.cc` file containing a class for moving the arm (using inverse kinematics). When it wants to dig a trench, it first checks the text file to see if a tree has been detected.
- Finally, we use test objects to verify that everything is working.

## References
https://machinelearningmastery.com/the-beginners-guide-to-computer-vision-with-python/
https://pyimagesearch.com/2016/02/08/opencv-shape-detection/
https://www.geeksforgeeks.org/python/python-opencv-cheat-sheet/
https://www.geeksforgeeks.org/python/real-time-edge-detection-using-opencv-python/
https://docs.opencv.org/3.4/da/d22/tutorial_py_canny.html
https://classic.gazebosim.org/tutorials?tut=ros_depth_camera
https://github.com/osrf/gazebo_tutorials/blob/master/ros_depth_camera/tutorial.md
https://www.youtube.com/watch?v=A3nw2M47K50