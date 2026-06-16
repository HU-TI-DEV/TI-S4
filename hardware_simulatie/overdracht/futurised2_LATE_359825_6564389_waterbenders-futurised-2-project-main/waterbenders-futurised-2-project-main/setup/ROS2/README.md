# ROS, Slam and Packages
Below is a guide for installing ROS2, slam and using the right packages with Colcon. Please follow **all** the instructions below for the installation, when other scripts need to be added to the simulation, follow the steps of building ROS2 packages.

# Table of Contents

- [ROS, Slam and Packages](#ros-slam-and-packages)
- [Table of Contents](#table-of-contents)
- [Installing ROS2 and Slam](#installing-ros2-and-slam)
    - [Update container:](#update-container)
    - [Adding repositories](#adding-repositories)
    - [Installing required software](#installing-required-software)
    - [Install additional optional tools](#install-additional-optional-tools)
- [Build your own ROS2 packages](#build-your-own-ros2-packages)
    - [Install Colcon](#install-colcon)
    - [Source ROS2 before executing the below commands](#source-ros2-before-executing-the-below-commands)
    - [Create a package](#create-a-package)
    - [Build the package](#build-the-package)
    - [Add to Python script](#add-to-python-script)
    - [Sourcing ROS2 again](#sourcing-ros2-again)
  - [Errors and Issues](#errors-and-issues)
    - [Ultralytics not found](#ultralytics-not-found)
    - [my\_package not found](#my_package-not-found)

# Installing ROS2 and Slam
Run the Gazebo Docker container with (or use a [`.ps1`](../../docker/setup/container-start/example-ps1-file.txt) file):
```bash
docker run -it <image> bash
```

### Update container:
```bash
apt update
apt install -y locales curl gnupg2 lsb-release software-properties-common

locale-gen en_US en_US.UTF-8
update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8
export LANG=en_US.UTF-8
```

###  Adding repositories

```bash
add-apt-repository universe -y
apt update

curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
-o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros2/ubuntu noble main" \
> /etc/apt/sources.list.d/ros2.list
```

###  Installing required software

```bash
apt update && apt install -y python3-rosdep ros-jazzy-cartographer ros-jazzy-cartographer-ros ros-jazzy-desktop ros-jazzy-ros-gz ros-jazzy-ros-gz-bridge ros-jazzy-ros-gz-sim ros-jazzy-slam-toolbox ros-jazzy-teleop-twist-keyboard ros-jazzy-rviz2 ros-jazzy-nav2-map-server python3-colcon-common-extensions ros-jazzy-nav2-costmap-2d ros-jazzy-rtabmap ros-jazzy-rtabmap-launch ros-jazzy-cartographer-rviz ros-jazzy-rtabmap-ros ros-jazzy-octomap-server
```

###  Install additional optional tools

```bash
apt update && apt install ros-jazzy-joint-state-publisher ros-jazzy-joint-state-publisher-gui ros-jazzy-xacro 
```


# Build your own ROS2 packages
In order to run and use (new) scripts in the final product, colcon needs to build packages to make sure it can reach and run these from withing the final `simulation.launch.py` file. 

This file makes it really accessible and easy to run all the different scripts in a single terminal only. Without this, the user would have to use a minimum of **4 Powershell Terminals** in order to run one Python script. It's important to let the workspace function with this file for easy use.

### Install Colcon
**Make sure you have Colcon installed:**
```bash
apt install python3-colcon-common-extensions
```

### Source ROS2 before executing the below commands
```bash
source /opt/ros/jazzy/setup.bash
```

### Create a package
Navigate to `/workspace/models/ros/packages/` and use the below command to create a package with a pre-built node, where <package_name> is the name of your package:
```bash
ros2 pkg create --build-type ament_python --node-name main <package_name>
```

This will generate a basic package **template**, which one can use to develop custom Colcon packages for ROS2. You can now edit `my_package/my_package/main.py` to subscribe/publish to a topic and add custom logic. See [path_finding/main.py](../../workspace/prototypes/path-finding-demo/ros/packages/path_planning/path_planning/main.py) for an example of the code structure.

### Build the package
After that build the package using (inside `/workspace/models`):
```bash
colcon build
```

### Add to Python script
And add it to the [`simulation.launch.py`](../../workspace/models/simulation.launch.py) file, like this:
```python
    my_package = Node(
        package='my_package',   # change name of package you have
        executable='main',      # Matches the entry point in setup.py
        name='minimal_publisher', # define a name (example: 'object_detection_node')
        output='screen',        # don't change this
    )

    return LaunchDescription([
        bridge,
        static_laser_tf,
        slam_launch,
        my_package # <-- Added custom package
    ])
```

### Sourcing ROS2 again
Make sure that you source the Colcon workspace before running any packages with:
```bash
source install/setup.bash
```

## Errors and Issues
### Ultralytics not found
Please keep in mind that when using a `venv` for running the scripts **and** installing Python packages/libraries in there, there will be some problems. Using the `simulation.launch.py` causes it to not be able to reach into the `venv` for installations. In this project, the `object-detection.py` file unfortunately has some problems starting.

*Despite the error, the other parts of `simulation.launch.py` will work accordingly.*

This is the error:
```bash
ModuleNotFoundError: No module named 'ultralytics'
```

In order to run this python script, please follow the following commands:
```bash
source /workspace/venv/bin/activate
cd workspace/models/scripts
python detect-objects.py
```

This runs the Python script in an extra terminal, but surpasses the gotton errors. 

### my_package not found
When the package name is changed after creating the package with the [command above](#create-a-package), this can cause some issues inside `setup.py` and `package.xml`. The easiest way to fix these issues is to:
1. Create a copy of the Python code in a different file so it will not be lost
2. Delete the created package that is giving issues
3. Recreate the ROS2 package using [these steps](#create-a-package)
4. Try building again and most likely the error will be solved