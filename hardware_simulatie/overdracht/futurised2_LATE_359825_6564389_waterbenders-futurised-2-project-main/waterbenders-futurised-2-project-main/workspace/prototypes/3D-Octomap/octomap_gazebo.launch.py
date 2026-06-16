from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{
            'config_file': '/workspace/prototypes/3D-Lidar-Mapping/rosBridge.yaml'
        }]
    )

    static_laser_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='laser_static_tf',
        arguments=[
            '0.6', '0', '0.3',
            '0', '0', '0',
            'chassis',
            'FLIP/chassis/gpu_lidar'
        ],
        output='screen'
    )

    octomap = Node(
        package='octomap_server',
        executable='octomap_server_node',
        name='octomap_server',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'frame_id': 'odom',
            'resolution': 0.05
        }],
        remappings=[
            ('cloud_in', '/points')
        ]
    )

    return LaunchDescription([
        bridge,
        static_laser_tf,
        octomap
    ])