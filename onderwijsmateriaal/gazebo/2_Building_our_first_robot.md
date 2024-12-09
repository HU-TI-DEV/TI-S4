# 2. Building our first robot
*source: https://gazebosim.org/docs/latest/building_robot/*

In this step we will build our first robot and move it using commands in the command editor window. 

Below the following environments are used:<br>
<sup>1</sup> The prompt of the power shell environment<br>
<sup>2</sup> The prompt of the docker container<br>
<sup>3</sup> Inside the docker container, inside the vi editor

### Build the sdf (Simulation Description Format) 
Follow the steps in https://gazebosim.org/docs/latest/building_robot/ and save the file as robot.sdf in your pc environment. The end result should look something like this: 
LINK NAAR ROBOT.SDF

We will now try to run the robot.sdf with gz sim. First:
- start dockers for desktop in your windows environment.
- run vcxsrv in your windows environement.
- run the powershell

In the powershell type<sup>1</sup>:
~~~ 
docker run -it -e DISPLAY=host.docker.internal:0 -v /tmp/.X11-unix:/tmp/.X11-unix gazebo
~~~

We will make a directory in which we will save our robot.sdf<sup>2</sup>:
~~~
mkdir ~/gz_transport_tutorial
cd ~/gz_transport_tutorial
~~~

Open vi<sup>2</sup>:
~~~
vi robot.sdf
~~~

Paste the content of the robot.sdf (on your dekstop) inside the vi editor.
To save and exit<sup>3</sup>:
~~~
:w
:q 
~~~

Type<sup>2<sup>:
~~~
gz sim robot.sdf
~~~
Are you proud? I hope so!
Close the gz sim window.

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



