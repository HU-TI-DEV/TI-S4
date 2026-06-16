# Hardware rendering with Gazebo & WSL (CUDA)

`Authors: Ocarian` 


## This research topic has been discontinued due to unstable results. Run the Gazebo simulation native on Linux for better results

> Sources used:
- [Reddit thread | Gazebo on WSL2](https://www.reddit.com/r/ROS/comments/1l0wobi/gazebo_on_wsl2/)
- [Robotics Stackexchange](https://robotics.stackexchange.com/questions/111677/gazebo-not-use-nvidia-gpu-when-i-installed-ros2-jazzy-by-using-docker-desktop-on)
- [GitHub Gazebo issues](https://github.com/gazebosim/gz-sim/issues/2595)
- [Reddit thread | WSL acceleration](https://www.reddit.com/r/wsl2/comments/1ohnhqr/trying_to_accelerate_wsl_apps_like_gazebo_using/)
- [Reddit thread | ROS environment variables](https://www.reddit.com/r/ROS/comments/1mxwhse/comment/nap095t/)

### Make sure to install the CUDA tools from NVIDIA before you start!:
- [NVIDIA Download page](https://developer.nvidia.com/cuda-downloads?target_os=Windows&target_arch=x86_64)  

---

`Install distro`

> Install your required Linux distro for WSL with the following command. In this guide we will use Ubuntu-24.04.

```ps
wsl --install -d Ubuntu-24.04
```

> Now enter the installed Linux distro and install the required tools

```ps
sudo apt update
sudo apt install -y curl gnupg lsb-release
```

`Installing Gazebo`

> Download the key and Gazebo repo-lists using the following commands

```ps
sudo curl -fsSL https://packages.osrfoundation.org/gazebo.key \
| sudo gpg --dearmor -o /usr/share/keyrings/gazebo-archive-keyring.gpg
```

```ps
echo "deb [signed-by=/usr/share/keyrings/gazebo-archive-keyring.gpg] \
http://packages.osrfoundation.org/gazebo/ubuntu-stable noble main" \
| sudo tee /etc/apt/sources.list.d/gazebo-stable.list
```

> Now update your lists and check the available Gazebo versions

```ps
sudo apt update
```

```ps
apt search gz-sim
```

> For this guide we are using Gazebo version 10.0.0. Use the following command if available

```ps
sudo apt install gz-sim10-cli libgz-sim10-plugins
```

> The correct Gazebo version should now be installed

![alt text](hardware-rendering/media/image.png)
