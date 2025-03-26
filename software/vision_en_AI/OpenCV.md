# 1. OpenCV
OpenCV (Open Source Computer Vision Library) is a library of programming functions mainly for real-time computer vision. It focusses on the classical vision methods.

**Machine Learning (AI)**  
 OpenCV does supports machine learning  algorithms, but only the classical ones (Support Vector Machines, K-Nearest Neighbors, Random Forest, etc.). These are useful for tasks like classification, regression, and clustering. 
OpenCV however does **not** include **deep** learning frameworks like TensorFlow or PyTorch.
The present state of the art approach for vision applications (CNN) is better implemented in those modern frameworks.

Below the following environments are used:<br>
<sup>1</sup> The prompt of the power shell environment<br>
<sup>2</sup> The prompt of the Docker container<br>

## Installing OpenCV in a Docker container

Make sure Docker Desktop is running. In addition run vcxsrv in your windows environment. Enter your container. First we will install all the necessary software tools<sup>2</sup>:
```bash
apt-get update && apt-get install -y
apt-get install python3-pip python3-dev -y
apt-get install libopencv-dev python3-opencv -y
rm -rf /var/lib/apt/lists/
```
Please note, on my setup I could paste one sentence at a time. I would copy a sentence and with rightclick I could paste it in the docker container.
Let's check if it is installed<sup>2</sup>:
```
python3 -c "import cv2; print(cv2.__version__)"
```

We will now copy the [example1.png](./files/example1.png) file to our container. You could use the following command for it<sup>1</sup>:
```
docker cp <source> <container_id>:<destination>
```
Please note: you run this command in the prompt of the powershell.   
If you have already mounted a hd in your container (or made a coupling in vs code) you could do this probably much easier!

In my case I have put example1.png in the same folder as my gz_transport example<sup>1</sup>:  
```
docker cp example1.png f1d965431e05:/root/gz_transport_tutorial/
```


Go to the folder<sup>2</sup>
```
cd ~/gz_transport_tutorial
```

Use your favorite editor to make an `example1.py` and paste the following:
```python
import cv2

# Read the image
image = cv2.imread("example1.png")

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

cv2.imshow("Processed Image", gray)
cv2.waitKey(0)  # Wait for a key press
cv2.destroyAllWindows()  # Close the window
```
Run the example & enjoy:
```
python3 example1.py
```

### Sobel filter
The following code implements a sobel filter:

```python
import cv2
import numpy as np

# Read the image
image = cv2.imread("example1.png")

# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
sobel_kernel_x = np.array([[-1, 0, 1],
                            [-2, 0, 2],
                            [-1, 0, 1]])


sobel_x = cv2.filter2D(gray, -1, sobel_kernel_x) 
cv2.imshow("Processed Image", sobel_x)
cv2.waitKey(0)  # Wait for a key press
cv2.destroyAllWindows()  # Close the window
```

Upload a picture of you choice, but make sure it is clear it is from YOU (if you do not want to be in the picture make a picture of a piece of paper with your student #).  

Implement a sobel filter in the y-direction on your picture.  
**Save the resulting image (you need to upload it to canvas)**.

### Sharpening filter
Implement a 3x3 sharpening filter (see https://setosa.io/ev/image-kernels/).  
**Save the resulting image (you need to upload it to canvas)**.


### Gaussian blur

use cv2.getGaussianKernel() to implement a **5 x 5** gaussian blur.   
**Save the resulting image (you need to upload it to canvas)**

substract the previous result from the original image using something like: 
```
result_image=gray-gaussian_blur_image
```

Result should be simular to: 
![Statler en Waldorf](./files/image.png)    

**Save the resulting image (you need to upload it to canvas)**

### Color filtering

Try the following code:
```python
import cv2
import numpy as np

# Read the image
img = cv2.imread("example1.png")
img2=cv2.inRange(img, np.array([0, 0, 100]), np.array([100, 100, 255]))
cv2.imshow("Original Image", img)
cv2.waitKey(0) # Wait for a key press
cv2.imshow("Processed Image", img2)
cv2.waitKey(0)  # Wait for a key press
cv2.destroyAllWindows()  # Close the window
```
The result:
![alt text](./files/image2.png)

Apply a color filter on your image.  
**Save the resulting image (you need to upload it to canvas)**.




pip install torch torchvision