<img src = ../../images/teamlogo.png align="right" width="135">

# Contributions
`The following text has been written by Yannick Hogetoorn`
As you might expect the code has been written by all of the group members. To put a percentage split on the contributions would be simply unfair and most likely inaccurate.

# Demo
The demo contains the Autonomous Mobile Platform driving around the designed area. It will drive from keypoint to keypoint. The path it takes is entirely determined by AStar and influenced by the object recognition. The object recognition is demonstrated by the openCV image which will pop up in the MobaXterm window. 

## Instructions
How do we run this code?
### Step 1 - Setup
Make sure all packages are installed and you are within the correct environment. To mimic the development demo best, the demo should be performed inside a docker container. The docker container is based on an image released by the teachers.

If you cannot get your hands on this package it is unfortunately not possible to mimic our test. If any developer would like to perform the demo in a different environment they would need to have access to at least the following software packages/applications.
- Gazebo
- OpenCV
- MobaXTerm

Our docker image is inside of WSL however, this might not be a necessity.

### Step 2 - Prepping our environment
To load all files into the environment it is recommended to use the VSCode IDE in combination with the dev container extension. Before we interact with the extension however, it is important that the user starts their docker container and their MobaXterm. This extension allows us to attach to a running docker container by navigating to the big search bar at the upper middle part of the screen.

Pasting in the command `>Dev Containers: Attach to Running Container` should prompt a second interactable window with all running containers. Select the container you want to work in and which contains the right software listed above.

When this action is performed a new VSCode window will pop up which will load for a little while. Let this load.

When the loading has stopped copy over all files from the demo folder into the new environment. To do this first select the right folder by going to the top left and clicking "file" -> "open folder". Another search bar at the upper middle part of the screen will appear. Locate the folder named "workspace" and click on it. It might need some time to load before you can paste the demo files in the folder. 

### Step 3 - Command line actions
Run the following commands in the terminal or any other command line which is connected to the dev container: 

- `gz sim demoEnvironment &` -> This starts a gazebo window. We do not need to interact with it yet.
- `mkdir build`              -> Creates a directory named 'build'
- `cmake -B build`           -> Running this command will fill the build folder with all necessary files to create a runnable file
- `cmake --build build`      -> Using this command will create a runnable file using the CMakeLists.txt file provided in the demo folder
- `./build/AutonomousVehicle`-> The last command we run will be one to execute the file we just created.

Some of these can be combined to one long command as shown below:

`mkdir build && cmake -B build && cmake --build build && ./build/AutonomousVehicle`

Keep in mind that these steps are for the first time replication of our environment. If you've made a runnable file before, you can use the following commands instead:
`gz sim demoEnvironment &`
`./build/AutonomousVehicle`

### Step 4 - Within Gazebo
Now we open Gazebo back up again and press the play button in the lower left corner. Since the executable file has already been ran, the Autonomous Mobile Platform will start driving immediately and a window will pop up showing the depthcamera image containing all bounding boxes.

## End result
When the code is left running the Autonomous Mobile Platform will drive towards all points it was able to find. During this process it will avoid all obstacles in its path and dynamically calculate a new path around said obstacles.