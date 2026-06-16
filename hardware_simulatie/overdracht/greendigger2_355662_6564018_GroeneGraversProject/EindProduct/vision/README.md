# README

## description
This folder is made for Vision and its camera. We have a Camera attached to the chassis of the excavator and the .cc file saves the images of that camera. The images are saved as "photoVision.jpg". Then in the Vision.py file we analyse the images to check for trees. We return a boolean in "stopSignal.txt" (in the folder: "controller).


## Vision 
For the tree detection we used OpenCV, but to accurately detect them we decided to add filter first. These are the filters we used:
- Grayscale
- Gaussian blur
- edge detection

The image is first converted to Grayscale and a blur is added. This blur lessens the amount of noise in the pictures. Lastly we use canny agde detection to detect the outlines of object.

With al this we detect the different shapes within the picure and when a circle is on top of a recangle we call it a tree. The following files are important to understand the structure:


## File structure

    ├───controller
    │   └───stopSignal.txt    # Contains a boolean indicating whether a tree was detected
    ├───models
    ├───vision
    │   ├───camera.cc         # Captures and saves images from the camera
    │   ├───camera.hh
    │   ├───vision.py         # Uses OpenCV to detect trees and writes to stopSignal.txt
    │   └───main.py           # calls camera.cc


# Main
The camera class is called in the main function. Next, the program subscribes to Gazebo’s camera topic. The program then remains active and checks every five seconds to see if a new camera image is available. If so, the most recently received grayscale image is saved as `photoVision.jpg`. 

# Camera
The camera class handles communication with the camera in Gazebo by subscribing to a specified topic. As soon as a new image arrives, it is automatically processed. The image is converted to a grayscale image using OpenCV, saved as the most recent frame **latestGray**, and displayed in an OpenCV window. Because both the callback function and the main loop have access to the same image, a mutex is used to handle this in a thread-safe manner.

# Vision
In computer vision, we use OpenCV. This software actually recognizes shapes and then determines whether they resemble a tree. Before this can work, a few steps need to be taken. 

## Grayscale
First, the image must be converted to black and white. This is important for all other filters to work properly and ultimately to achieve the best possible recognition. It’s not a difficult step, but it is crucial to the outcome.

## Blur
This is a blur applied to reduce noise. It improves edge detection by reducing errors, which in turn improves the overall detection.

There are several types of blurs you can apply:

**Average Blur**  
the simplest form of blur. For each pixel, the average of all pixels in that kernel is calculated. The new value is then the sum of those pixels divided by 9 (since the kernel is 3x3). The advantage of this is that it’s easy to implement and works well, but it blurs everything slightly, causing you to lose a lot of detail.  

**Guassian Blur** 
We chose this shape, which is very common in computer vision. Instead of assigning equal weight to all pixels, pixels closer to the center are given greater weight. This works better because it preserves the edges more effectively, thereby ensuring that edge detection can be used to its full potential. This is also why we use this shape.  

**Median Blur**  
This process sorts all pixel values and selects the middle value. All values in the kernel are lined up, and the pixel takes on the middle value. This filters out the “extreme” values. It preserves the edges very well, but it is slower and less effective for general camera noise.  

**Bilateral Blur**  
Finally, we have this method. It is the most advanced because it also takes color differences into account. This means that colors that do not resemble the central pixel have less impact on the result. This is best for edges, as they remain very well preserved this way, but it is much slower and also a bit overkill for this project.  

The conclusion is that we chose Gaussian Blur. This seemed like the best option, since it works quickly and effectively enough for this project. Furthermore, we didn’t have any issues with the blur, so our choice seemed to be a good one.  

## edge detection
After the image has been blurred, edge detection must be performed. The purpose of edge detection is to identify the edges of objects. This allows us to remove a lot of irrelevant information from the image. This is the most important step for recognizing the tree later on. 
We also use shape detection. This detects shapes within the image. If a shape resembles a circle and there is a “rectangle” underneath it, we say that it is a tree.


## Recommendations
Using Vision with OpenCV can be challenging. Creating the system itself is not the main issue; achieving reliable detection is much harder. If accurate tree detection is required, we recommend investigating the use of a neural network. This would allow the system to recognize actual trees instead of simply detecting a collection of shapes that resemble a tree.

The reason for this is that factors such as lighting conditions, camera angles, and object shapes have a significant impact on detection accuracy.

Why? Because our detector only looks at basic geometric shapes. For example, it can detect a circle when the entire shape is visible. However, if the circle is partially cut off, it often fails to recognize it. This becomes a problem when an object is close to the camera, because it may no longer fit completely within the frame.

As a result, our system is capable of detecting abstract tree-like shapes, but only when they are far enough away to be fully visible. Unfortunately, this also means that the trees are often far enough away that they are no longer an immediate obstacle.

We did not have the time or the tools available to fully solve this issue. Initially, we planned to use a depth camera, which would have provided distance information and made detection significantly more reliable. However, this approach was not allowed within the requirements of the project.

Our recommendation for future groups is to explore neural-network-based object detection. By training a model on a large set of tree images, the system can learn to recognize trees based on their visual features rather than relying solely on shape detection. This would make the detector more robust to changes in lighting, viewing angles, partial occlusion, and objects that are only partially visible in the frame.

While OpenCV-based shape detection is useful for learning computer vision concepts and building simple prototypes, a trained neural network would likely provide more reliable results for real-world tree detection.
