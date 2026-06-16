<img src="../../images/teamlogo.png" align="right" width="135">

# Contributions
`Code written by: Ruben Kroon, Jelle Warries & Ryan Smit`

The code files found in this folder are responsible for the entire obstacle detection process. This consists of both registering an object in view of the depth camera and performing calculations to determine the absolute position of the object. Since no prior knowledge was taught to about this process this code evolved and was restructured multiple times throughout development. Most changes related to OpenCV functionalities and how these could be used on the image received from the Gazebo environment.

## Choices & Clarification
### Programming language
`Decided by team, Coded by Ruben Kroon`

Spotting and placing every object accurately is of utmost importance. Missing an object could entail a collision and misplacing an object could entail pathfinding right into an obstacle. Having a higher frame rate to analyse and doing the analysation quickly would make sure all obstacles are spotted and placed at the right place. To accelerate this process the code was migrated from Python to C++. Although this transition required approximately a week of development effort, it resulted in a significant, and worthwile, performance increase. As expected the use of the faster language sped up our analysis of the images by a large margin.

### Depth camera
`Decision made by entire team`

To view objects in the environment, the depth camera has been mounted on the simulated Autonomous Mobile Platform. The depth camera was neither the first choice nor the first iteration but was certainly a well-chosen solution. In Gazebo there are 8 different camera sensors to use ([sdf format, n.d.](https://sdformat.org/spec/1.12/sensor/)). Each has its own limitations or was simply not fully compatible with the software supplied. This left the decision up to a normal RGB camera, a logical camera, a bounding box camera or a depth camera. The RGB camera was the first choice and contained our first implementations. The logical camera would entail a process where objects are programmed to be found. This cannot be replicated in real-life and was therefore removed from the considered options. Next up to evaluate is the bounding box camera. This camera performed exactly as needed. Unfortunately the camera found bounding boxes where none were needed and therefore did not become our final choice. Another limitation of the bounding box camera was the lack of distance data we could get from it. The depth camera was the only option left with genuine promise.

The depth camera uses multiple cameras or lasers to produce a greyscale image where any point gets coloured along a greyscale depending on how far they are from the camera. This not only allows for bounding box detection but also for distance calculations. The combination of these two factors became good reason to use this camera.

### [Hardcoded horizon](objectRecognition.hpp#L64)
`Coded by: Ruben Kroon`

When using the depth camera, the horizon will also be seen as a sudden change of distance. This is due to the camera only being able to see a certain distance. This limitation could unfortunately not be fully avoided. Various filters, modifications of the depth image horizon, and other implementation techniques were tested to overcome the limitation. All of these attempts did not resolve the limitation. This caused the choice to disregard a small part of the image along the axis of the horizon. The disregarded area is big enough to not detect the horizon as a strong edge but is not big enough to cover any obstacle which poses danger to the Autonomous Mobile Platform.

### [Area threshold](objectRecognition.hpp#L69)
`Coded by: Ruben Kroon`

Pebbles on the surface of the terrain are obstacles the Autonomous Mobile Platform can definitely disregard. This required the implementation of a threshold for an obstacle which would classify obstacles as path-breaking obstacles or insignificant artifacts. 
Implementing this threshold also prevented several image inaccuracies from being detected and classified as obstacles. The cause of the inaccuracies was not clear but this choice did solve the problem. This approach was both simple and effective which prompted no following fixes to be considered nor tried. 

### [Value threshold](objectRecognition.hpp#L67)
`Coded by: Ruben Kroon & Ryan Smit`

To eliminate calculations for obstacles which are too far away, a value threshold was implemented to skip over certain pixels in the far distance. This decision was made because the edge gradient values of distant obstacles become very difficult to distinguish and therefore do not result in correct obstacle placements. This value gets scaled with the linear scaling algorithm mentioned later in this file.

### [OpenCV image analysis (ImageCallback)](objectRecognition.cc#L86)
`Coded by: Ruben Kroon & Jelle Warries`
To obtain depth information from the environment, the system subscribes to the /camera topic. The depth images received from this topic are processed using OpenCV to detect obstacles and determine their approximate positions relative to the Autonomous Mobile Platform.

Using different kernel filters, the image supplied by the depth camera is altered to detect obstacles. The Canny edge filter is used to draw edges on top of obstacles. This process is done by multiplying all pixel values with the kernel. Edges have strong color differences and will therefore show up bright on the edge detected image. The Canny edge filter has been chosen because it is very efficient and makes very few mistakes (OpenCV, 2024).

After this image is altered to only contain edges, a dilate kernel is passed over the image to thicken any lines (OpenCV, 2024). A byproduct of this process is the coloration of a small line near the ground of an obstacle. This will become the lower edge of the bounding box later on.

### [Bounding box analysis (DecodeBB(amp_x, amp_y, amp_yaw))](objectRecognition.cc#L183)
`Coded by: Ryan Smit`

Analysing the position of the bounding boxes derived from the OpenCV edited image contains several complex calculations. The calculations pass the pixel data through multiple processing stages. The first step is determining the vector to the depth camera on the Autonomous Mobile Platform, since this only needs to be done once per pass of calculations. 

```cpp
auto [depth_cam_x_vec, depth_cam_y_vec] = rotateXYVectorBasedOnYaw(offset_x_depthcamera, offset_y_depthcamera, amp_yaw);
```

The vector to an object is found by adding the yaw to the simple pixel distance data. This way it can be accurately stated in which direction the vector is going. This data is then added to the position of the Autonomous Mobile Platform and the vector to the depth camera, which results in an absolute position of the obstacle.

Next the obstacles get loaded into a cleared vector. This vector can be accessed by any other class or function as it is a global variable. We will discuss these processes into more detail now.

#### [Linear scaling](objectRecognition.cc#L215)
`Coded by: Ryan Smit`

Since the data is still relative to Gazebo measurements, the pixel values need to be scaled. Since a lot of the scale depended on user input data such as the scale of the light values, the choice was made to do this via a linear scaling function. This function consists of finding the scale of the Gazebo values and multiplying this with a real world distance vector.

```cpp
if (xi < 0 || yi < 0 || xi >= vis_copy.cols || yi >= vis_copy.rows){continue;} // Coördinaten moet niet out of bounds zijn
float value = vis_copy.at<uchar>(yi, xi); // Grijswaarde ophalen
float threshold;
if(yi < y_value_horizon){threshold = value_threshold;}
else{threshold = value_threshold - convertPixelValueToDistance(0, value_threshold, y_value_horizon, image_height - 1, yi);}

if (value < threshold){
    ...
```

#### [simplifyCalcs(pixel_x_value, pixel_grayscale_value, amp_yaw)](objectRecognition.cc#L78)
`Coded by: Ryan Smit`

As listed before, this process can become very complicated. Therefore the choice was made to wrap this in a simplifyCalcs() function. This function calls all the corresponding calculations depending on what is supplied. The end result is a 2D vector from the depth camera to the obstacle. Add this vector to the position of the Autonomous Mobile Platform and the position of the obstacle is determined.

#### [Obstacle rounding, padding & simplification](objectRecognition.cc#L219)
`Coded by: Jelle Warries & Ryan Smit`

As a result of the previous functions the assumption can be made that every bounding box contains an obstacle. For each bounding box we simplify obstacles to their most extreme x and y values. This is to prevent having an abundance of data or calculations in this process. This will be explained further under the paragraph about [performance issues](#performance-issues). Finally once these most extreme x and y coordinates have been determined, the entire area that is now defined by said object and added padding is stored in the obstacles member variable through the use of a nested for-loop. Through this obstacles member variable other classes will be able to extract and apply the collected data.

After the location of the object has been found, a padding and the original object are added to the "obstacles" member variable, which is then read and analysed by the ProcessController.

### Helper functions
`Coded by: Ryan Smit`

#### [angledDistanceToComponents(float distance, float angle)](objectRecognition.cc#L57)

This function calculates the XY vector to a point dependent on the angle. This is done by using the SOH CAH TOA rule (MathIsFun, 2025).

#### [rotateXYVectorBasedOnYaw(float x, float y, float yaw)](objectRecognition.cc#L69)
Using a rotation matrix, this function turns a vector according to the yaw of our AMP [(GeeksforGeeks, 2025)](https://www.geeksforgeeks.org/maths/rotation-matrix/).

## Problems
### Camera type
`Solved as a group`

As discussed earlier, a lot of different cameras were at our disposal and one had to be chosen. At first the RGB camera was chosen. The algorithm this camera used was an algorithm to find the difference in color between the background and the object. This worked really well in our testing environment but we quickly foresaw issues when deploying this in a different environment. This also limited our distance detection mechanism. No distance data was given by this camera so this would mean a second camera would have to be mounted. The fix to this problem was the depth camera, because this 

### Undetectable bottom
`Solved by: Jelle Warries & Ruben Kroon`

The lowest line of a bounding box was difficult to detect due to the thin edge the Canny edge filter produced. This meant that no proper four edge connection could be made. By implementing the dilate function a very small line near the bottom was created and the lines thickened. This made sure that the bounding box could be drawn around the obstacle. Multiple other possible solutions were evaluated but did not stick. The dilate filter performed the right alterations and did not prompt any other solution.

### Horizon bounding boxes
`Solved by: Ruben Kroon`

As listed earlier, the choice was made to transition to C++ from Python. This process was all but easy but did give us an enormous performance boost. It did however also change the image we read from the depth camera. The exact reason this happened still sparks debate but the horizon transformed from a straight line into a curve. This meant that the curve was now outside of our horizon threshold and could be detected by the Canny edge filter. This problem was solved by changing the background pixels to a different shade of white. The depth camera now does have a little less vision in the distance but this distance is minimal enough for us to disregard it. 

### Performance issues
`Solved by: Ryan Smit, Ruben Kroon & Jelle Warries`

The performance increase gained by switching from Python to C++ was not fully voluntary. It was prompted when the code began to show performance issues and threw error codes. Migrating meant all code had to be rewritten and therefore a new look at all our functions. This resulted in a more optimised bounding box analysis and a quicker and better performing codebase.

Besides migrating the full class, several other issues were encountered while programming the bounding box analysis. An early iteration of code added padding to the vector created by each pixel, then immediately used a nested for-loop to add this list of coordinates to a local set. It did this for each pixel which passed previous tests and resulted into a relative x,y-vector. As a result, there were two nested for-loops iterating over the pixels (one for x and one for y directions) followed by another two nested for-loops to iterate over the coordinates which needed to be blocked by its resulting vector. This caused a very noticable performance loss once an obstacle was detected and also had its padding added. The upside of previously mentioned approach is an increase in object shape accuracy it the performance loss however, was too great to continue with this analysis method. The problem was solved by simplying obstacles to their most extreme values as seen by our current implementation in [the decodeBB() function](#bounding-box-analysis-decodebbamp_x-amp_y-amp_yaw).

### 'Doorframe or tree' problem
`Solved by: Ruben Kroon`

An issue we encountered and could not resolve, involved drawing two bounding boxes on either side of an object. This situation could come up when the Autonomous Mobile Platform is located right in front of a large tree or when in front of a gap in a wall. In one scenario the best approach is to drive straight ahead and in the other making a path around the obstacle is preferred. This is an analysis we will be passing to the next group.

## Advice
`Written by: Ryan Smit, Ruben Kroon & Jelle Warries`

- Adding LiDAR to the Autonomous Mobile Platform.

Detecting obstacles using LiDAR is considerably more consistent, faster and better for multiple direction detection. Since the other group had chosen to work on the LiDAR sensor it had been removed from our sensor pool. This meant this solution unfortunately could not be developed by us. We highly recommend future developers to use this technology.

- Dynamic horizon variable.

Because our demo does not show the Autonomous Mobile Platform on a slope we were able to complete the project without resolving this issue. When the Autonomous Mobile Platform drives up towards a hill it will detect it as an obstacle since it sticks out above our horizon variable. This was unfortunately outside our research period to resolve.

- Add additional research behind minimal bounding box size.

Currently the minimal bounding box is chosen based on deleting as many added obstacles as possible. The threshold could be accurately determined using additional research we unfortunately did not have time to perform.

- Choosing which pixels to look at in a bounding box.

The code now performs quite well but skips a lot of pixels within a bounding box. This means that we might not detect the front-most pixel. There could be a sweet spot where the performance is mostly unaffected but there are still a lot of pixels being evaluated.

- Doorframe or tree.

We recommend two solutions:
1. Perform a search from farther away and use this information to influence your decision.
2. See if you can check the outside values of the bounding box.

## Sources
Open Robotics. (n.d.). SDF specification 1.12: Sensor. https://sdformat.org/spec/1.12/sensor/
e-con Systems. (n.d.). What are depth sensing cameras & how do they work? https://www.e-consystems.com/blog/camera/technology/what-are-depth-sensing-cameras-how-do-they-work/
OpenCV team. (2024). Canny edge detector. OpenCV documentation. https://docs.opencv.org/4.x/da/d22/tutorial_py_canny.html
OpenCV team. (2024). Morphological transformations (dilate). OpenCV documentation. https://docs.opencv.org/4.x/d9/d61/tutorial_py_morphological_ops.html
MathsIsFun. (2025). SOHCAHTOA. https://www.mathsisfun.com/algebra/sohcahtoa.html
GeeksforGeeks. (2025, July 23). Rotation matrix. https://www.geeksforgeeks.org/maths/rotation-matrix/