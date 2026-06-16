### start commands

colcon build --packages-select tonk_mapping --symlink-install
source /opt/ros/jazzy/setup.bash
source install/setup.bash || true
ros2 launch tonk_mapping mapping.launch.py 

### command 
Voor Eden
    gazebo = ExecuteProcess(
        cmd=['gz', 'sim', '-r', world_path],

Voor Thor
gazebo = ExecuteProcess(
        cmd=['/usr/libexec/gz/sim10/gz-sim-main', '-r', world_path],