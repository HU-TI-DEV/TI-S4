# 7. Using thrusters

In this section we will see how to use thrusters. Thrusters are a way to provide to simulate for instance propellers.<br>
```
gz sim thruster.sdf &
```

```
gz topic -t /model/cube_with_thruster/joint/thruster_joint/cmd_thrust -m gz.msgs.Double -p "data: 1.0"
```



gz sim camera.sdf &



gz topic -e -t /camera/image


