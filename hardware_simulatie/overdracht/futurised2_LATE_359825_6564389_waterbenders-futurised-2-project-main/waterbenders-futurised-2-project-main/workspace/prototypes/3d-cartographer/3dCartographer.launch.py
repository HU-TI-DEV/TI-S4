from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{
            'config_file': '/workspace/prototypes/3d-cartographer/rosBridge.yaml'
        }]
    )

    # Lidar TF — same as before
    static_laser_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='laser_static_tf',
        arguments=[
            '--x', '0.6', '--y', '0', '--z', '0.3',
            '--roll', '0', '--pitch', '0', '--yaw', '0',
            '--frame-id', 'chassis',
            '--child-frame-id', 'FLIP/chassis/gpu_lidar'
        ],
        parameters=[{'use_sim_time': True}],  # ← add this
        output='screen'
    )

    static_imu_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='imu_static_tf',
        arguments=[
            '--x', '0', '--y', '0', '--z', '0',
            '--roll', '0', '--pitch', '0', '--yaw', '0',
            '--frame-id', 'chassis',
            '--child-frame-id', 'FLIP/chassis/imu_sensor'
        ],
        parameters=[{'use_sim_time': True}],  # ← add this
        output='screen'
    )

    # CHANGED: using my_robot_3d.lua
    cartographer_node = Node(
        package='cartographer_ros',
        executable='cartographer_node',
        name='cartographer_node',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=[
            '-configuration_directory', '/workspace/prototypes/3d-cartographer',
            '-configuration_basename', 'my_robot_3d.lua'
        ]
    )

    # REMOVED: cartographer_occupancy_grid_node — it only works with 2D submaps
    # For 3D visualization use RViz2 with the PointCloud2 / /submap_list topics

    return LaunchDescription([
        bridge,
        static_laser_tf,
        static_imu_tf,   # new
        cartographer_node,
    ])