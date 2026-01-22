# 1. Installing Gazebo

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
docker load -i gazebo_s4.tar
~~~
This will load the docker container as an image. 

### Installing X server
*Source:  [https://vcxsrv.com/](https://mobaxterm.mobatek.net/download-home-edition.html)* <!-- markdown-link-check-disable-line -->

We have to install a X server (to enable a graphical user interface in Ubuntu). Go to (https://mobaxterm.mobatek.net) [https://mobaxterm.mobatek.net/download-home-edition.html] and install the server on your windows computer. <!-- markdown-link-check-disable-line -->

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

