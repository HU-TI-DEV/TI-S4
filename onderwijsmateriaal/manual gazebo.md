# Installing Gazebo
Gazebo is a modelling/simulation framework with which we can simulate reality. In this guide we will learn how to install it. 

Below the following environments are used:<br>
<sup>1</sup> The prompt of the power shell environment<br>
<sup>2</sup> The prompt of the docker container


## Installing gazebo in a docker container
Allthough you can install Gazebo on native windows the version is broken, it does not work correctly. We will install it in a docker container. 

#### Install Docker Desktop on Windows:
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

#### Install Gazebo inside the container:
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

#### Installing WSL & X server
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

#### First time running

Run our previously commited docker container<sup>1</sup>:
~~~
docker run -it -e DISPLAY=host.docker.internal:0 -v /tmp/.X11-unix:/tmp/.X11-unix gazebo
~~~

We can test it by running<sup>2</sup>:
~~~
gz sim
~~~
Select the robot and press run. You should see the robot in a new window (some errors/warnings could be present in the container window).

#### Running after a reboot or exiting the powershell:

- start dockers for desktop in your windows environment.
- run vcxsrv in your windows environement.
- run the powershell

In the powershell type<sup>1</sup>:
~~~ 
docker run -it -e DISPLAY=host.docker.internal:0 -v /tmp/.X11-unix:/tmp/.X11-unix gazebo
~~~

## Connect with c++
we will first try c++.
https://github.com/gazebosim/gz-transport/blob/gz-transport13/tutorials/02_installation.md

sudo apt-get install libgz-transport13-dev

Check if the library is correct:
apt-cache search libgz

sudo apt update
sudo apt install cmake g++ -y

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
