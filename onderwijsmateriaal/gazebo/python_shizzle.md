


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
