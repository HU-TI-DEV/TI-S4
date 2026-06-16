from launch import LaunchDescription, LaunchContext
from launch.actions import IncludeLaunchDescription, TimerAction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, LifecycleTransition, LifecycleNode
from ament_index_python.packages import get_package_share_directory
from launch.actions.execute_process import ExecuteProcess
from launch_ros.descriptions import ParameterFile
from launch.actions import GroupAction
from launch_ros.actions import SetRemap
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
import yaml
import os

ROS_BRIDGE_DIRECTORY = '/workspace/models/ros/'

def generate_launch_description():

    gazebo = ExecuteProcess(
        cmd=[
            'env', '-i',
            'PATH=/usr/bin:/usr/local/bin',
            f'HOME={os.environ["HOME"]}',
            f'DISPLAY={os.environ.get("DISPLAY")}',

            # Below lines break path-finding due to 
            # issues with the 'odom' transform frame:
            # f'GZ_PARTITION={os.environ.get("GZ_PARTITION", "")}',
            # f'GZ_IP={os.environ.get("GZ_IP", "")}',

            f'XAUTHORITY={os.environ.get("XAUTHORITY")}',
            'gz', 'sim', '/workspace/models/gazebo/environment.sdf'
        ],
        output='screen'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{
            'config_file': os.path.join(ROS_BRIDGE_DIRECTORY, 'ros_bridges.yaml')
        }]
    )

    # Static TF for 2D LiDAR
    static_laser_tf_2d = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='laser_static_tf_2d',
        arguments=[
            '0.6', '0', '0.3', '0', '0', '0',
            'chassis', 'FLIP/chassis/gpu_lidar'
        ],
        output='screen'
    )

    slam_launch = GroupAction([
        SetRemap(src='/map', dst='/map_2d'),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('slam_toolbox'),
                    'launch',
                    'online_async_launch.py'
                )
            ),
            launch_arguments={
                'slam_params_file': '/workspace/models/ros/slam_params.yaml',
                'use_sim_time': 'true'
            }.items()
        )
    ])

    costmap_2d = LifecycleNode(
        package='nav2_costmap_2d',
        executable='nav2_costmap_2d',
        name='global_costmap',
        namespace='',
        output='screen',
        parameters=[
            '/workspace/models/ros/nav2_costmap_params.yaml'
        ],
        autostart=True
    )

    path_planning = Node(
        package='path_planning',
        executable='main',
        name='path_planning_node',
        output='screen'
    )
    
    return LaunchDescription([
        gazebo,
        bridge,
        static_laser_tf_2d,
        slam_launch,
        costmap_2d,
        path_planning
    ])
