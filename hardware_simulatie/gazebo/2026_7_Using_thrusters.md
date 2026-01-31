# 7. Using thrusters

In this section we will see how to use thrusters. Thrusters are a way to provide to simulate for instance propellers.<br>
if you did not open your container yet<sup>1</sup>:
~~~
docker ps -a
~~~
You need to find the id of the container you just exited (probably the first one on the list).<br>
Copy the id & paste it in the lines below<sup>1</sup>:
~~~
docker start <container_id>
docker exec -it -e DISPLAY=host.docker.internal:0 <container_id> bash
~~~

