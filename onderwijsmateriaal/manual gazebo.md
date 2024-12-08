# Installing Gazebo
Gazebo is a modelling/simulation framework with which we can simulate reality. In this guide we will learn how to install it. 

Below the following environments are used:<br>
<sup>1</sup> The prompt of the power shell environment<br>
<sup>2</sup> The prompt of the docker container<br>
<sup>3</sup> Inside the docker container, inside the vi editor


## Installing gazebo in a docker container
Allthough you can install Gazebo on native windows the version is broken, it does not work correctly. We will install it in a docker container. 

### Install Docker Desktop on Windows:
*Source: https://www.docker.com/products/docker-desktop/<br>*
First, you need to install Docker Desktop for Windows. You can download it from Docker's official site.
Follow the installation steps to set it up.
Docker Desktop provides a LinuxKit-based virtual machine (VM) that runs Linux inside Windows. This is necessary because Docker uses Linux containers, and Docker Desktop for Windows leverages WSL2 (Windows Subsystem for Linux) to provide a Linux kernel.

Open the windows powershell prompt and type the following<sup>1</sup>:

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
and save it under a different name. First we need to  find the id<sup>1</sup>:
~~~
docker ps -a
~~~
You need to find the id of the container you just exited (so the last one).<br>
Copy the id & paste it in the below command<sup>1</sup>:
~~~
docker commit <container_id> gazebo
~~~
This may take some time. Patience is virtue.

### Installing WSL & X server
*Source: https://learn.microsoft.com/en-us/windows/wsl/install & https://vcxsrv.com/*

We will also have to install WSL<sup>1</sup>:
~~~
wsl --install
wsl --set-default-version 2
~~~
Configure Docker to use WSL 2:

Open Docker Desktop and go to Settings.
Under the General tab, ensure Use the WSL 2 based engine is checked.
Go to Resources > WSL Integration. Here, you’ll see a list of installed WSL distros.
Enable the WSL 2 integration for your preferred distros (like Ubuntu). This allows Docker to use those distros as Docker hosts.

We also have to install a X server (to enable a graphical user interface in Ubuntu). Go to https://vcxsrv.com/ and install the server on your windows computer. 

Run the X server (via the start menu of windows).

Set the environment display variable<sup>1</sup>:
~~~
$env:DISPLAY="host.docker.internal:0"
~~~

### First time running

Run our previously commited docker container<sup>1</sup>:
~~~
docker run -it -e DISPLAY=host.docker.internal:0 -v /tmp/.X11-unix:/tmp/.X11-unix gazebo
~~~

We can test it by running<sup>2</sup>:
~~~
gz sim
~~~
Select the robot and press run. You should see the robot in a new window (some errors/warnings could be present in the container window).

If you want to take a break with this manual this would be a nice time to do so. You've committed the container so everything is nicely saved! 

### Running after a reboot or exiting the powershell:

- start dockers for desktop in your windows environment.
- run vcxsrv in your windows environement.
- run the powershell

In the powershell type<sup>1</sup>:
~~~ 
docker run -it -e DISPLAY=host.docker.internal:0 -v /tmp/.X11-unix:/tmp/.X11-unix gazebo
~~~

You could now start gz sim or do other stuff. For the next step we do not need to start gz sim!

## Connect with c++
*Source: https://github.com/gazebosim/gz-transport/blob/gz-transport14/tutorials/04_messages.md*

We would like to be able to interact with gazebo via c++. The next steps enable this.

if you did not open your container yet, type in the powershell<sup>1</sup>:
~~~ 
docker run -it -e DISPLAY=host.docker.internal:0 -v /tmp/.X11-unix:/tmp/.X11-unix gazebo
~~~

We will first install the tooling we need<sup>2</sup>:
~~~
sudo apt install cmake g++ -y
apt-get install vim
~~~
Next step: we are going to make a directory<sup>2<sup>:
~~~
mkdir ~/gz_transport_tutorial
cd ~/gz_transport_tutorial
~~~

Download 
- publisher.cc 
- subscriber.cc 
- CMakeLists.txt

from https://github.com/gazebosim/gz-transport/blob/gz-transport14/tutorials/04_messages.md

Study the manual of the VI editor: 
https://www.redhat.com/en/blog/introduction-vi-editor

Make a new file with the vi editor with<sup>2</sup>:
~~~
vi publisher.cc
~~~
Copy the text from publisher.cc (the one you have downloaded earlier) and paste it in the vi editor. 
Type the following commands in the vi editor<sup>3</sup>:
~~~
:w
:q
~~~
This will save the file and exit the vi editor. 

Do the same for the **subscriber.cc** and **CMakeLists.txt**

Next we will make a new dir<sup>2</sup>:
~~~
mkdir build
cd build
~~~



Type the following commands<sup>2</sup>:
~~~
cmake ..
make publisher subscriber
~~~
We have now compiled the subscriber.cc and publisher.cc file!

Read the description in *https://github.com/gazebosim/gz-transport/blob/gz-transport14/tutorials/04_messages.md* to understand what happens in the subscriber and publisher code. 

We will now exit the container<sup>2</sup>:
~~~
exit
~~~
and save it. First we need to  find the id<sup>1</sup>:
~~~
docker ps -a
~~~
You need to find the id of the container you just exited (so the last one).<br>
Copy the id & paste it in the below command<sup>1</sup>:
~~~
docker commit <container_id> gazebo
~~~
This may take some time. Patience is virtue.

### Running our first test with the transport layer!

First we will start a container again<sup>1</sup>:
~~~
docker run -it -e DISPLAY=host.docker.internal:0 -v /tmp/.X11-unix:/tmp/.X11-unix gazebo
~~~
In this container we will first go to the correct directory<sup>2</sup>:
~~~
cd ~/gz_transport_tutorial/build
~~~
Then we start the publisher<sup>2</sup>:
~~~
./publisher
~~~

We should see something like this:

![
](image.png)

We start a new powershell and type in the new window<sup>1</sup>:
~~~
docker ps -a
~~~
Copy the name of the last docker running and past it in the following<sup>1</sup>:
~~~
docker exec -it <name_container> /bin/bash
~~~ 
Because we used exec instead of run we will now enter the same container as we opened before. 

Again we will first go to the correct directory<sup>2</sup>:
~~~
cd ~/gz_transport_tutorial/build
~~~
Then we start the subscriber<sup>2</sup>:
~~~
./subscriber
~~~
You should now receive the hello message!











# TODO






- a lot
- really
- a
- lot


## Connect with python
we will first try python.

apt-get install vim
apt-get update
apt-get install vim
~~~
https://gazebosim.org/api/transport/13/python.html
~~~

~~~
vi publisher.py
~~~
press
~~~
:i 
~~~
inside the editor 
paste the publisher.py code from https://gazebosim.org/api/transport/13/python.html


https://gazebosim.org/api/sim/8/install.html

apt-get update && apt-get install -y wget

libgz-sim<#>-dev



================================================================================

apt-get update && apt-get install -y wget
sudo apt-get install curl
curl -sSL http://packages.osrfoundation.org/gazebo.key | sudo tee /etc/apt/trusted.gpg.d/osrf-archive.key
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 67170598AF249743
sudo sh -c 'echo "deb http://packages.osrfoundation.org/gazebo/ubuntu noble main" > /etc/apt/sources.list.d/gazebo-stable.list'


Please note: I have the version noble (check with: lsb_release -a)





# WSL2 

open a powershell and type:
~~~
wsl --install
~~~
This will start an Ubuntu distribution. Choose a login and password. 
Logout using:
~~~
exit
~~~
Configure the WSL to always use WSL2 and ubuntu:
~~~
wsl --set-default-version 2
wsl --setdefault Ubuntu
~~~
Start wsl:
~~~
wsl
~~~
Install Gazebo by:

~~~
sudo apt-get update
sudo apt-get install lsb-release gnupg
sudo curl https://packages.osrfoundation.org/gazebo.gpg --output /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
sudo apt-get update
sudo apt-get install gz-ionic
~~~~
Run gazebo by:
~~~
gz sim
~~~

If you get the error:
```
MESA: error: ZINK: failed to choose pdev
glx: failed to create drisw screen
```




Install https://vcxsrv.com/




curl -sSL http://get.gazebosim.org | sh
