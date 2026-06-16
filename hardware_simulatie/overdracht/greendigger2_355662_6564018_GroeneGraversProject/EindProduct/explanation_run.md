<img src="../../images/teamlogo.png" align="right" width="135">

# Contributions
`The following text has been written by Willem Barneveld`
As you might expect the code has been written by all of the group members. To put a percentage split on the contributions would be simply unfair and most likely inaccurate.

# Demo
The demo showcases the robot excavator operating within the designed Gazebo simulation environment. The vision component detects the targets, after which the controller uses Inverse Kinematics to calculate the required joint positions. The excavator arm will then dynamically move towards the target to perform its operation. The object detection pipeline can be monitored via the vision window popping up in MobaXterm.

---

# Instructions: Setup & Running the Code

## Part 1 - First-Time Setup (For the first time)

Follow these steps if you are replicating the environment for the very first time.

### Step 1 - Setup & Prerequisites
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

### Step 3 - First-Time Manual Build Breakdown
To manually build and run the project step-by-step for the first time (matching the exact behavior of our automated script), run the following commands in a terminal connected to the dev container:

```bash
# 1. Build the controller components
mkdir -p controller/build && cd controller/build
cmake .. && make -j4
cd ../..

# 2. Build the vision components
mkdir -p vision/build && cd vision/build
cmake .. && make -j4
cd ../..

# 3. Export the correct Gazebo model paths
export GZ_SIM_RESOURCE_PATH=$(pwd)/models

# 4. Start the Gazebo simulation in the background
gz sim desert.sdf &

# 5. Start the vision components in the background
cd vision/build
./camera &
cd ..
python3 vision.py &
cd ..

# 6. Wait a few seconds for the simulation to fully load, then run the main controller
sleep 5
./controller/build/main
```
*(Note: If you want to kill all background processes started by these terminal commands later, you can run `kill 0` or exit the terminal session).*

---

## Part 2 - Subsequent Runs (Whenever you want to rerun)

Once the environment is prepped and the initial build folders are created, you can use our ready-to-use script to launch everything automatically.

### Using the Automated Script:
1. Open a terminal inside your connected dev container environment.
2. Change directory to the `EindProduct` folder:
   ```bash
   cd EindProduct
   ```
3. Make the script executable (only needed once):
   ```bash
   chmod +x run.sh
   ```
4. Run the script:
   ```bash
   ./run.sh
   ```
5. **Repeat this step** whenever you want to rerun the simulation.

*Note: The script automatically handles rebuilding and launching both the controller and the vision components (`main` and `vision.py`) in the background after starting Gazebo.*

---

## Part 3 - Execution & Expected Results

### Within Gazebo
Now we open Gazebo back up again and press the play button in the lower left corner. Since the controller and vision scripts are already running in the background, the excavator arm will start moving autonomously towards the detected targets in the desert environment using Inverse Kinematics. A window will pop up showing the camera feed containing the bounding boxes for the target detection.

### End Result
When the code is left running, the robot excavator will continuously scan the environment using the vision script. Once a target is found, the system dynamically calculates the joint angles through Inverse Kinematics, allowing the arm to move precisely towards the target and execute the digging cycle.