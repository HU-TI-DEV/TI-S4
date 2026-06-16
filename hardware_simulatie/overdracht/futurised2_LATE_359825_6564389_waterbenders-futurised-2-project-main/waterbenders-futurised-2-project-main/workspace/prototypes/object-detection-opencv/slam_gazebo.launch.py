from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{
            'config_file': '/workspace/prototypes/lidarSensorOmgeving/rosBridge.yaml'
        }]
    )

    static_laser_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='laser_static_tf',
        arguments=[
            '0.6', '0', '0.3', '0', '0', '0',
            'chassis', 'FLIP/chassis/gpu_lidar'
        ],
        output='screen'
    )

    # Cartographer node
    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{
            'use_sim_time': True,
        }],
        arguments=[
            '-configuration_directory', '/workspace/prototypes/objectHerkenningCV2',
            '-configuration_basename', 'my_robot_2d.lua'
        ]
    )

    # Occupancy grid node (publishes the /map topic)
    occupancy_grid_node = Node(
        package='cartographer_ros',
        executable='cartographer_occupancy_grid_node',
        name='occupancy_grid_node',
        output='screen',
        parameters=[{
            'use_sim_time': True,
        }],
    )

    # slam_launch = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(
    #         os.path.join(
    #             get_package_share_directory('slam_toolbox'),
    #             'launch',
    #             'online_async_launch.py'
    #         )
    #     ),
    #     launch_arguments={
    #         'slam_params_file': '/workspace/prototypes/lidarSensorOmgeving/mapper_params_online_async.yaml',
    #         'use_sim_time': 'true'
    #     }.items()
    # )

    return LaunchDescription([
        bridge,
        static_laser_tf,
        cartographer_node,
        occupancy_grid_node
    ])
