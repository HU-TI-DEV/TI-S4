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

WORKSPACE_DIR = '/workspace/models/scripts'
DATABASE_FILES_DIRECTORY = '/workspace/models/'
ROS_BRIDGE_DIRECTORY = '/workspace/models/ros/'
VENV_PATH = '/workspace/venv'

def generate_launch_description():

    database_dir = os.path.join(DATABASE_FILES_DIRECTORY, 'databaseFiles')
    os.makedirs(database_dir, exist_ok=True)

    db_name_arg = DeclareLaunchArgument(
        'db_name',
        default_value='rtabmap.db',
        description='Name of the RTAB-Map database file inside databaseFiles'
    )

    db_path = PathJoinSubstitution([
        database_dir,
        LaunchConfiguration('db_name')
    ])

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
            'gz', 'sim', 'gazebo/environment.sdf'
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

    # Static TF for 3D LiDAR
    static_laser_tf_3d = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='laser_static_tf_3d',
        arguments=[
            '0.6', '0', '0.925',
            '0',   '0', '0',
            'chassis',
            'FLIP/3D_LidarSensor/lidar_sensor_link/gpu_lidar'
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

    rtabmap_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('rtabmap_launch'),
                'launch',
                'rtabmap.launch.py'
            )
        ),
        launch_arguments={
            # ── Odometry ──────────────────────────────────────────────────────
            'visual_odometry': 'false',
            'icp_odometry':    'true',
            'odom_topic':      '/odom',
            'odom_frame_id':   'odom',

            # ── Frames ────────────────────────────────────────────────────────
            'frame_id':       'chassis',
            'map_frame_id':   'map',
            'publish_tf_map': 'true',

            # ── Input: 3D LiDAR point cloud ───────────────────────────────────
            'subscribe_scan':       'false',
            'subscribe_scan_cloud': 'true',
            'scan_cloud_topic':     '/points',
            'depth':                'false',

            # ── Sync / QoS ────────────────────────────────────────────────────
            'qos':         '2',
            'approx_sync': 'true',
            'queue_size':  '30',

            # ── Database ──────────────────────────────────────────────────────
            'database_path': db_path,

            'args': (
                # Remove -d to resume/continue a previous mapping session.
                '-d '

                # ── Registration ──────────────────────────────────────────────
                '--Reg/Strategy 1 '
                '--Reg/Force3DoF false '

                # ── ICP tuning ────────────────────────────────────────────────
                '--Icp/VoxelSize 0.001 '
                '--Icp/PointToPlane true '
                '--Icp/Iterations 60 '
                '--Icp/MaxCorrespondenceDistance 0.15 '
                '--Icp/Epsilon 0.001 '
                '--Icp/MaxTranslation 1.0 '

                '--Mem/IncrementalMemory true '
                '--RGBD/LinearUpdate 0.05 '
                '--RGBD/AngularUpdate 0.025 '
                '--RGBD/NeighborLinkRefining true '

                '--Rtabmap/DetectionRate 5 '

                '--Grid/FromDepth false '
                '--Grid/3D true '
                '--Grid/CellSize 0.02 '
                '--Grid/RangeMax 10.0'
            ),

            'use_sim_time': 'true',
            'rtabmap_viz':  'false',
            'rviz':         'false',
        }.items()
    )

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
    
    object_detection = Node(
        package='object_detection',
        executable='main',
        name='object_detection_node',
        output='screen',
    )
    
    fire_detection = Node(
        package='fire_detection',
        executable='main',
        name='fire_detection_node',
        output='screen',
    )

    explosion_detection = Node(
        package='explosion_detection',
        executable='main',
        name='explosion_detection_node',
        output='screen',
    )
    
    rviz_config = os.path.join(WORKSPACE_DIR, 'rtabmap_mapping.rviz')

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config],
        parameters=[{
            'use_sim_time': True
        }]
    )

    audio_bridge_node = Node(
        package='logical_audio_sensor',
        executable='main',
        name='logical_audio_sensor_node',
        output='screen'
    )

    return LaunchDescription([
        db_name_arg,
        gazebo,
        bridge,
        static_laser_tf_2d,
        static_laser_tf_3d,
        slam_launch,
        rtabmap_launch,
        costmap_2d,
        path_planning,
        audio_bridge_node,
        rviz_node,
        object_detection,
        fire_detection,
        explosion_detection
    ])
