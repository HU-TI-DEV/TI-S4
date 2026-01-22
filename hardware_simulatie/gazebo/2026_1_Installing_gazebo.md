# 0. Installing Gazebo

Gazebo is a modelling/simulation framework. In this guide we will learn how to install it. 

Below the following environments are used:<br>
<sup>1</sup> The prompt of the CMD<br>
<sup>2</sup> The prompt of the Docker container<br>


### Install Docker Desktop on Windows:
If you have not done this already we first install [Docker Desktop](https://www.docker.com/products/docker-desktop/). Please note, you need approximatly 10Gb of diskspace to install it. You can download it from Docker's official site.

Make sure to choose WSL as the default option. Follow the installation steps to set it up. Please note, it could be that you need to [enable hardware virtualization in your bios to make it run](https://forums.docker.com/t/hardware-assisted-virtualization-and-data-execution-protection-must-be-enabled-in-the-bios/109073).   
Docker Desktop provides a LinuxKit-based virtual machine (VM) that runs Linux inside Windows. 

Make sure Docker Desktop is running. 

Download the image.tar file from canvas (canvas -> hoofdpagina -> linkje bij planning). Make sure you save the file at the same place as where your CMD prompt opens. 

Open the CMD prompt and type the following<sup>1</sup>:

~~~
docker load -i image.tar
~~~
~~~
apt-get update
apt-get install -y curl
apt-get install -y sudo
apt-get install -y wget
~~~
Please note, on my setup I could paste one sentence at a time. I would copy a sentence and with rightclick I could paste it in the docker container.

### Install ROS 2 in docker:

We will base the installation on this site: https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html#try-some-examples  
I've copied the relevant commando's below.  
Type the following commands<sup>2</sup>:
~~~
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F\" '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo $VERSION_CODENAME)_all.deb" # If using Ubuntu derivates use $UBUNTU_CODENAME
sudo dpkg -i /tmp/ros2-apt-source.deb
sudo apt update && sudo apt install ros-dev-tools
sudo apt update
sudo apt upgrade
sudo apt install ros-jazzy-desktop
source /opt/ros/jazzy/setup.bash
~~~

We will now exit the container<sup>2</sup>:
~~~
exit
~~~
and save it as an image. First we need to  find the id<sup>1</sup>:
~~~
docker ps -a
~~~
You need to find the id of the container you just exited (so the last one). <br>
Copy the id & paste it in the below command<sup>1</sup>:
~~~
docker commit <container_id> ros2
~~~
This may take some time. Patience is virtue.

### Installing X server
*Source:  https://vcxsrv.com/* <!-- markdown-link-check-disable-line -->

We have to install a X server (to enable a graphical user interface in Ubuntu). Go to https://vcxsrv.com/ and install the server on your windows computer. <!-- markdown-link-check-disable-line -->

Run the X server (via the start menu of windows).

Set the environment display variable<sup>1</sup>:
~~~
$env:DISPLAY="host.docker.internal:0"
~~~

### First time running

We will now start the container again.  
First we need to  find the id<sup>1</sup>:
~~~
docker ps -a
~~~
You need to find the id of the container you just exited (so the last one).<br>
Copy the id & paste it in the lines below<sup>1</sup>:
~~~
docker start <container_id>
docker exec -it -e DISPLAY=host.docker.internal:0 <container_id> bash
~~~

Each time you start a container you have to set the environment variables with <sup>2</sup>:
~~~
source /opt/ros/jazzy/setup.bash
~~~

Run the examples on (excluding rqt_graph) up till and including the turtlesim:  
https://github.com/MOGI-ROS/Week-1-2-Introduction-to-ROS2?tab=readme-ov-file#running-some-examples

### Running after a reboot or exiting the powershell:

- start dockers for desktop in your windows environment.
- run vcxsrv in your windows environment.
- run the powershell

First we need to  find the id<sup>1</sup>:
~~~
docker ps -a
~~~
You need to find the id of the container you just exited (so the last one).<br>
Copy the id & paste it in the lines below<sup>1</sup>:
~~~
docker start <container_id>
docker exec -it -e DISPLAY=host.docker.internal:0 <container_id> bash
~~~

Each time you start a container you have to set the environment variables with <sup>2</sup>:
~~~
source /opt/ros/jazzy/setup.bash
~~~

