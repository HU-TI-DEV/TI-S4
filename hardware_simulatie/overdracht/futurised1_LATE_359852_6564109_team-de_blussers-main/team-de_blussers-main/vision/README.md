# Vision - Person Detection with YOLO
This module enables real-time human detection within Gazebo simulation. By processing camera streams through a YOLO-model, the system identifies people in the Gazebo environment, publishes their locations and displays bounding boxes and markers directly in Rviz.

---

## How does it work?
The system follows the data flow below to transform raw visual input into classified human detections:

1. **Simulation:** Gazebo simulates the environment with a camera mounted on the robot providing a camera feed.
2. **Bridge:** ros_gz_bridge converts gz.msgs.Image message into ROS2 sensor_msgs/msg/Image on the camera topic.
3. **Processing:** A dedicated ROS2 node uses cv_bridge to convert incomming image messages into an OpenCV format for real-time inference.
4. **Detection:** The finetuned YOLO model processes the frame, identifies humans and generates bounding box coordinates.
5. **Visualization:** The detection results (bounding box, classification) are published as ROS2 topics and visualized in Rviz for real-time monitoring.

### Gebruikte technologieën
- **Gazebo** - simulation of the environment and the camera.
- **ROS2 (Jazzy)** - data transport between components.
- **PyTorch** - training of the model
- **Ultralytics YOLOv8** - the objectdetection model used to finetune
- **OpenCV** - image processing
- **RViz** -live visualisation of the detected person

---

## Computer vision methods
To get the best objectdetection method that fits in the scope of this project and is compatible with Gazebo, research was conducted into various computer vision methods.

### Faster R-CNN
Faster R-CNN is a *two-stage detector*. In the first step, candidate regions where an object might be located are proposed and in the second step, those regions are classified and the bounding boxes are drawn (DigitalOcean, 2025). 

**Pros:**
- **High accuracy:** because of the two seperate steps, the model poduces very precise bounding boxes and works good for small and overlapping objects (Arya, 2024).
- **Complex scenes:** performs well when many objects are located close together.

**Cons:**
- **Slow:** the two-stage approach makes it too slow for real-time detection on a camera.
- **Resource-intensive:** requires a lot of computional power and memory, which can be challenging in a Gazebo simulation that isn't the fastest simulation software. 
- **Complex to train and finetune:** because it involves multiple stages and a more complicated pipeline.

### YOLO
YOLO (You Only Look Once) is a *one-stage detector* that processes the entire image in a single pass and directly predicts the classes and bounding boxes. The image is divided into a grid, where then each cell is responsible for detecting objects within the region (Arya, 2024).

**Pros**
- **Realtime speed:** designed for fast detections. It is ideal for live realtime detections.
- **Pretrained model available:** YOLOv8 model is pretrained on the COCO dataset. Finetuning with minimal data will still give good results.
- **Easy to use:** Ultralytics makes training, finetuning and inference accessible.
- **Good balance:** tGood balance between speed and accuracy of the detections.

**Cons**
- **Less accurate:** it is less accurate than a two-stage detector for small or overlapping objects. 
- **Struggles with small objects:** Difficulty with detecting small objects especially at long distances due to the grid based approach.

### CNN
A convolutional neural network is the fundamental building block behind most modern vision models. A bare CNN can be built and trained from scratch for classification or detection without relying on an existing detection architecture.

**Pros**
- **Full control:**the architecture can be precisely tailored to the problem.
- **Educational:** provides a good understanding of how neural networks work.
- **Lightweight:** suitable for simple classification tasks.

**Cons**
- **Requires a lot of data:** training from scratch needs a large, manually labeled dataset.
- **time consuming:** both designing the architecture and training the model take a lot of time.
- **No built-in object detection:** a basic CNN only performs classification. The bounding boxes must be implemented sperately.

## Why YOLO?
For detecting people, YOLOv8 (ultralytics) was chosen, combined with fine-tuning, instead of training a model completely from scratch. This choice was made because:

- **Pretrained on large dataset:** Yolov8 is already trained on the COCO dataset, which contains hundreds of thousands of images with labeled objects, including the `person` class.
- **Less custom data required:** training a model from scratch requires a very large and diverse dataset. With fine-tuning, less custom training data is needed. This is much more efficient and feasible within the scope of this project. In addition, the `person` class is already well represented in the COCO dataset.
- **Time and feasibility:** no ned to design a custom CNN architecture or collect extensive dataset. This allows the focus to remain on the actual problem.
- **Realtime performance:** YOLO is a one-stage detector and is designed for fast and realtime detection on camera.

### Extra custom dataset on top of YOLO
After testing the YOLO model, it became clear that de confidence scores were reletively low. Further analysis showed that the gazebo models appear too blocky and unrealistic, which affects detection performance. To address this, I collected additional data by taking screenshots and also used an existing dataset from Roboflow. To make the data suitable for training, I manually annotated each image with labels.

The creation of the custom dataset consisted of the following steps:
1. **Data collection:** Using screenshots from the Gazebo simulation, I collected images of people in the parking garage environment. This ensures that the training data matches the image the model will encounter during real use. In addition, I included an existing dataset from Roboflow to increase the variety and the number of images. It was advised by Bart Bozon, HU to use at least 10000+ images.
2. **Labeling:** Each image was labeled by drawing a bounding box around each person and assigning the correct `person` class. For this, I used Roboflow, which saves labels in YOLO format as .txt files.
3. **Dataset structure:** The dataset was split into a training and validation set. The configuration is defined in data.yaml, which specifies the path to the images and class names.
4. **training (finetunen):** Using this combined dataset, the pretrained Yolo model was finetuned. Because the dataset now specifically includes the blocky Gazebo models, trained model recognizes them much better and the confidence scores have increased.

---

## Folder structure

| Path | Description |
| --- | --- |
| train.py | Script for training the model|
| data.yaml | YOLO dataset configuration (paths + classes) |
| dataset/ | Training and validationset images/ + labels/ |
| models/ | trained models .pt |
| img/ | Screenshots and results |

The dataset structure follows the standard YOLO format:

```
dataset/
  images/
    train/
    val/
  labels/
    train/
    val/
```

---

## Technical steps

### Install requirements

**PyTorch met CUDA** (for GPU. omit de CUDA-version for CPU):

```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**Other Python packages**   
ultralytics provides YOLO and includes openCV functionality. matplotlib en pandas are used visualizing the training graphs in train.py:

```bash
pip3 install ultralytics matplotlib pandas
```

**Check installations:**

```bash
# PyTorch + OpenCV available?
python3 -c "import torch; import cv2; print('PyTorch en OpenCV zijn klaar voor gebruik')"

# Does it run on GPU or CPU?
python3 -c "import torch; print('CUDA beschikbaar:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

### Model training / finetuning
Finetuning is performed using the train.py script. The dataset and classes are loaded from the data.yaml file. The paths are automatically resolved relative to train.py, which allows the script to be started from any working directory.

```bash
python3 train.py
```

What the script does:

1. **Device selection:** select_device() automatically detects hether a CUDA GPU is available and otherwise falls back to CPU training. This function was added because GPU training is not always possible, depending on the availability of a graphics card.
2. **Model loading:** the pretrained yolov8.pt model is loaded using Ultralytics YOLO.
3. **Training (finetuning):** model.train() starts the training process using the default parameters defined at the bottom of train.py

   | Parameter | Default | Description |
   | --- | --- | --- |
   | model_name | yolov8n.pt | Pretrained model that is finetuned |
   | epochs | 100 | number of training epochs |
   | imgsz | 640 | input image resolution |
   | batch | 16 | number of images per batch |

  THese values can be adjusted in the train(...) function at the bottom of train.py.

The results are stored in runs/detect/train/ the best weights are saved in runs/detect/train/weights/best.pt.

---

## Recommendation
This section is intended for the follow up team that will continue developing the vision component. The current system detects people in the Gazebo simulation using a finetuned YOLO model. Below are suggestions for further improvement and expansion.

### Improving the model and dataset
- *More diverse training data:** collect more images under different lighting conditions, camera angles, distances and levels of crowding (multiple people at once). This will make the model more robust.
- **Adjusting confidence threshold:** the current recall is high but precision is average (it sometimes produces false positives), Tuning the threshold value can further improve confidence and reduce incorrect detections.

### New features for future development
- **Tracking:** Add object tracking so that a person keeps the same ID across when the person is moving/walking.
- **Multiple classes:** extend the detection to other objects such as vehicles or obstacles by adding extra classes to the dataset and the data.yaml file.
- **Navigation integration:** connect the detections to autonomous navigation so that the robot chooses a completely different path for extra safety of the person.

---

# Sources

Ultralytics. (2026). Explore Ultralytics YOLOv8. [https://docs.ultralytics.com/models/yolov8#overview](https://docs.ultralytics.com/models/yolov8#overview)

Ultralytics. (2026). How to Fine-Tune YOLO on a Custom Dataset. [https://docs.ultralytics.com/guides/finetuning-guide#fine-tuning-vs-training-from-scratch](https://docs.ultralytics.com/guides/finetuning-guide#fine-tuning-vs-training-from-scratch)

Geeks for Geeks. (2025). Evolution of Faster R-CNN Models. [https://www.geeksforgeeks.org/machine-learning/faster-r-cnn-ml/](https://www.geeksforgeeks.org/machine-learning/faster-r-cnn-ml/)

Geeks for Geeks. (2025). Introduction to Convolutional Neural Network. [https://www.geeksforgeeks.org/machine-learning/introduction-convolution-neural-network/](https://www.geeksforgeeks.org/machine-learning/introduction-convolution-neural-network/)

Deeplizard (2017). Convolutional Neural Networks (CNNs) Explained.  Youtube.  [https://www.youtube.com/watch?v=YRhxdVk_sIs](https://www.youtube.com/watch?v=YRhxdVk_sIs)

Gad F. A. Mukherjee S., Skelton J. (2025). Faster R-CNN Explained for Object Detection Tasks. DigitalOcean. [https://www.digitalocean.com/community/tutorials/faster-r-cnn-explained-object-detection](https://www.digitalocean.com/community/tutorials/faster-r-cnn-explained-object-detection)

Ayse A. M., Kiran S. M. (2025). A comprehensive Review on YOLO versions for object detection. ScienceDirect. [https://www.sciencedirect.com/science/article/pii/S2215098625002162](https://www.sciencedirect.com/science/article/pii/S2215098625002162)

Arya S. (2024, July 10). Object Detection Algorithms: R-CNN, Fast R-CNN, Faster R-CNN and YOLO. AnalyticsVidhya. [https://www.analyticsvidhya.com/blog/2024/07/object-detection-algorithms/](https://www.analyticsvidhya.com/blog/2024/07/object-detection-algorithms/) 