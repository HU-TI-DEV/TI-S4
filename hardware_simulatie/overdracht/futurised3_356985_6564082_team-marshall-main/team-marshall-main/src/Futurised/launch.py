from launch import LaunchDescription
from launch.actions import TimerAction, ExecuteProcess
from launch_ros.actions import Node


def generate_launch_description():

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': '/workspace/src/Futurised/bridge.yaml',
            'lazy': False,
        }],
        output='screen'
    )

    # Pass use_sim_time so the node's clock uses /clock from Gazebo
    tf_node = ExecuteProcess(
        cmd=['python3', '/workspace/src/Futurised/tf_broadcaster.py',
             '--ros-args', '-p', 'use_sim_time:=true'],
        output='screen'
    )

    camera_node = ExecuteProcess(
        cmd=['python3', '/workspace/src/Futurised/camera.py',
             '--ros-args', '-p', 'use_sim_time:=true'],
        output='screen'
    )

    slam = TimerAction(
        period=5.0,
        actions=[Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            output='screen',
            parameters=[{
                'use_sim_time': True,
                'scan_topic': '/scan',
                'base_frame': 'base_link',
                'odom_frame': 'odom',
                'map_frame': 'map',
                'queue_size': 100,
                'transform_timeout': 2.0,
                'tf_buffer_duration': 30.0,
                'resolution': 0.05,
                'max_laser_range': 10.0,
                'minimum_time_interval': 0.0,
                'map_update_interval': 0.1,
                'update_factor': 0.9,
                'occupied_space_cost_factor': 1.0,
            }]
        )]
    )

    configure_slam = TimerAction(
        period=12.0,
        actions=[ExecuteProcess(
            cmd=['ros2', 'lifecycle', 'set', '/slam_toolbox', 'configure'],
            output='screen'
        )]
    )

    activate_slam = TimerAction(
        period=15.0,
        actions=[ExecuteProcess(
            cmd=['ros2', 'lifecycle', 'set', '/slam_toolbox', 'activate'],
            output='screen'
        )]
    )

    explorer = TimerAction(
        period=20.0,
        actions=[ExecuteProcess(
            cmd=['python3', '/workspace/src/Futurised/explorer.py',
                 '--ros-args', '-p', 'use_sim_time:=true'],
            output='screen'
        )]
    )


    room_detector = TimerAction(
        period=20.0,
        actions=[ExecuteProcess(
            cmd=['python3', '/workspace/src/Futurised/room_detector.py',
                 '--ros-args', '-p', 'use_sim_time:=true'],
            output='screen'
        )]
    )

    rviz = TimerAction(
        period=10.0,
        actions=[Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', '/workspace/src/Futurised/slam_rviz.rviz'],
            parameters=[{'use_sim_time': True}],
            output='screen'
        )]
    )

    # C++ veiligheidsfilter (gz-transport): leest /cmd_vel_nav (pathfinding),
    # remt bij obstakels via de lidar, en stuurt het veilige commando naar
    # /cmd_vel (de robot). Zonder terminal start het binary automatisch in
    # filter-modus. Moet vooraf gebouwd zijn (cmake --build build).
    botsing_detectie = TimerAction(
        period=8.0,
        actions=[ExecuteProcess(
            cmd=['/workspace/src/RobotFlip_cc/build/botsing_detectie'],
            output='screen'
        )]
    )

    return LaunchDescription([
        bridge,
        tf_node,
        camera_node,
        slam,
        configure_slam,
        activate_slam,
        explorer,
        room_detector,
        rviz,
        botsing_detectie,
    ])