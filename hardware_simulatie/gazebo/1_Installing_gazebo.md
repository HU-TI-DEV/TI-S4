# 1. Installing Gazebo
Gazebo is a modelling/simulation framework. In this guide we will learn how to install it. 

Below the following environments are used:<br>
<sup>1</sup> The prompt of the power shell environment<br>
<sup>2</sup> The prompt of the Docker container<br>

## Installing gazebo in a Docker container
Although you can install Gazebo on native Windows that specific version is broken, it malfunctions. Therefore we will install Gazebo in a Docker container on Ubuntu.

### Install Gazebo inside the container:
Start the container from the [previous chapter](0_Installing_ROS.md).  
*Source: https://gazebosim.org/docs/harmonic/install_ubuntu/<br>*
To install type the following<sup>2</sup>:
~~~
sudo apt-get update
sudo apt-get install lsb-release gnupg

sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt-get update
sudo apt-get install gz-harmonic
~~~~
We will now exit the container<sup>2</sup>:
~~~
exit
~~~
and save it as an image. First we need to  find the id<sup>1</sup>:
~~~
docker ps -a
~~~
You need to find the id of the container you just exited (so the last one).<br>
Copy the id & paste it in the below command<sup>1</sup>:
~~~
docker commit <container_id> gazebo_ros
~~~
This may take some time. Patience is virtue.

### First time running Gazebo

We will now start the container again (make sure you also have the vcxsrv running).  
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

We can test it by running<sup>2</sup>:
~~~
gz sim
~~~
We should see:

![alt text](images/image-4.png)

Select the robot and press run. You should see the robot in a new window (some errors/warnings could be present in the container window):

![alt text](images/image-5.png)

If you want to take a break with this manual this would be a nice time to do so. You've committed the container so everything is nicely saved! 

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

Type<sup>2<sup>:
~~~
source /opt/ros/jazzy/setup.bash
gz sim
~~~

### Creating a new container from our image:
We could also create a new container from our image (the disadvantage is that you will accumulate containers very quickly!)
Run our previously commited image, this will create a new container<sup>1</sup>:
~~~
docker run -it -e DISPLAY=host.docker.internal:0  gazebo_ros
~~~

For the next step:  
2 [Building our first robot](./2_Building_our_first_robot.md)