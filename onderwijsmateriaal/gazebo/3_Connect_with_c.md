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
](images\image.png)

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
You should now receive the hello message:

![alt text](images\image-1.png)






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
