# 5. Using thrusters and camera

## Thrusters

In this section we will see how to use thrusters. Thrusters are a way to simulate for instance propellers.<br>
The sdf can be found here: [thrusters.sdf](./files/thrusters.sdf)  
Copy it to your container. Run it with:
```
gz sim thruster.sdf &
```
The ```&``` command makes the gz sim run in the background.   
Make sure you start the simulation (triangle in the bottom left corner).
We can now (in the same container) still give commands in the container:

```
gz topic -t /model/cube_with_thruster/joint/thruster_joint/cmd_thrust -m gz.msgs.Double -p "data: 1.0"
```
The cube should behave like a rocket!

## Camera

We will now introduce the camera sensor. The sdf can be found here: [camera.sdf](./files/camera.sdf)

Start the simulation:
```
gz sim camera.sdf &
```
The camera output the images... bla bla bla 

gz topic -e -t /camera/image


