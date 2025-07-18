# 1. Installing Gazebo
Gazebo is a modelling/simulation framework. In this guide we will learn how to install it. 

Below the following environments are used:<br>
<sup>1</sup> The prompt of the power shell environment<br>
<sup>2</sup> The prompt of the Docker container<br>

## Installing gazebo in a Docker container
Although you can install Gazebo on native Windows that specific version is broken, it malfunctions. Therefore we will install Gazebo in a Docker container on Ubuntu. If you use a Mac only a native install seems to be possible. Use the following [logbook-item for installing on Mac OS X](./Mac-OS/1_Installing_gazebo-Mac-OS.md).

### Install Docker Desktop on Windows:
If you have not done this already we first install [Docker Desktop](https://www.docker.com/products/docker-desktop/). Please note, you need approximatly 10Gb of diskspace to install it. You can download it from Docker's official site.

Make sure to choose WSL as the default option. Follow the installation steps to set it up. Please note, it could be that you need to [enable hardware virtualization in your bios to make it run](https://forums.docker.com/t/hardware-assisted-virtualization-and-data-execution-protection-must-be-enabled-in-the-bios/109073).   
Docker Desktop provides a LinuxKit-based virtual machine (VM) that runs Linux inside Windows. 

Make sure Docker Desktop is running. 
Open the Windows Powershell prompt and type the following<sup>1</sup>:

~~~
docker pull ubuntu
docker run -it ubuntu
~~~
We are now inside the container. First we will install all the necessary software tools<sup>2</sup>:
~~~
apt-get update
apt-get install -y curl
apt-get install -y sudo
apt-get install -y wget
~~~
Please note, on my setup I could paste one sentence at a time. I would copy a sentence and with rightclick I could paste it in the docker container.

### Install Gazebo inside the container:
*Source: https://gazebosim.org/docs/latest/install_ubuntu/<br>*
To install type the following<sup>2</sup>:
~~~
sudo apt-get update
sudo apt-get install lsb-release gnupg

sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null

sudo apt-get update
sudo apt-get install gz-ionic
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
docker commit <container_id> gazebo
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
gz sim
~~~

### Creating a new container from our image:
We could also create a new container from our image (the disadvantage is that you will accumulate containers very quickly!)
Run our previously commited image, this will create a new container<sup>1</sup>:
~~~
docker run -it -e DISPLAY=host.docker.internal:0  gazebo
~~~

For the next step:  
2 [Building our first robot](./2_Building_our_first_robot.md)