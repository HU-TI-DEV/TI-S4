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

    slam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('slam_toolbox'),
                'launch',
                'online_async_launch.py'
            )
        ),
        launch_arguments={
            'slam_params_file': '/workspace/prototypes/lidarSensorOmgeving/mapper_params_online_async.yaml',
            'use_sim_time': 'true'
        }.items()
    )

    return LaunchDescription([
        bridge,
        static_laser_tf,
        slam_launch
    ])