# 5. Using thrusters and camera

## Thrusters
*Please note: the youtube link at the end of this chapter shows a demo of the following steps.* 
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
See:   
[![YouTube Video Preview](https://img.youtube.com/vi/DtrU5ze-Ux8/0.jpg)](https://www.youtube.com/watch?v=DtrU5ze-Ux8)


## Camera
*Please note: the youtube link at the end of this chapter shows a demo of the following steps.* 

We will now introduce the camera sensor. The sdf can be found here: [camera.sdf](./files/camera.sdf)

Start the simulation:
```
gz sim camera.sdf &
```
The camera output the images... bla bla bla 

gz topic -e -t /camera/image

See:  
[![YouTube Video Preview](https://img.youtube.com/vi/9yOtOGGP5xs/0.jpg)](https://www.youtube.com/watch?v=9yOtOGGP5xs)



[![YouTube Video Preview](https://img.youtube.com/vi/R3QMzlAZnzo/0.jpg)](https://www.youtube.com/watch?v=R3QMzlAZnzo)


[![YouTube Video Preview](https://img.youtube.com/vi/lhfKNJloKxw/0.jpg)](https://www.youtube.com/watch?v=lhfKNJloKxw)



### END OF THIS MD...
For the next step:  
[6_Driving_the_robot](./6_Driving_the_robot.md)


