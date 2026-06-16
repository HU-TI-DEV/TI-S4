from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.actions import ExecuteProcess
from ament_index_python.packages import get_package_share_directory
import os
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

WORKSPACE_DIR = '/workspace/prototypes/3D-Lidar-Mapping-RTAB'


def generate_launch_description():

    db_name_arg = DeclareLaunchArgument(
        'db_name',
        default_value='rtabmap.db',
        description='Name of the RTAB-Map database file inside databaseFiles'
    )

    db_path = PathJoinSubstitution([
        WORKSPACE_DIR,
        'databaseFiles',
        LaunchConfiguration('db_name')
    ])

    # ── 1. Gazebo ↔ ROS bridge ────────────────────────────────────────────────
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        output='screen',
        parameters=[{
            'config_file': os.path.join(WORKSPACE_DIR, 'rosBridge.yaml')
        }]
    )

    # ── 2. Static TF: chassis → LiDAR sensor frame ───────────────────────────
    # Matches the <pose> inside <sensor> in lidarRoomScan.sdf: 0.6 0 0.3
    static_laser_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='laser_static_tf',
        arguments=[
            '0.6', '0', '0.925',
            '0',   '0', '0',
            'chassis',
            'FLIP/chassis/gpu_lidar'
        ],
        output='screen'
    )

    # ── 3. Height-to-colour node ──────────────────────────────────────────────
    # Your 16-line LiDAR has no RGB or intensity — everything renders as one
    # flat colour in RViz making objects impossible to distinguish.
    # This node reads /points and republishes /points_colored where each
    # point's RGB is mapped from its Z height:
    #   z <= -0.5 m  →  blue   (floor / low objects)
    #   z ~= 1.5 m   →  green  (mid height)
    #   z >= 3.5 m   →  red    (ceiling / tall objects)
    # Adjust z_min / z_max to match your room height.
    height_color_node = ExecuteProcess(
        cmd=[
            'python3',
            os.path.join(WORKSPACE_DIR, 'height_color_node.py'),
            '--ros-args',
            '-p', 'z_min:=-0.5',
            '-p', 'z_max:=3.5',
            '-p', 'use_sim_time:=true',
        ],
        output='screen'
    )

    # ── 4. RTAB-Map (SLAM + 3D mapping) ──────────────────────────────────────
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
            # ICP odometry aligns consecutive point clouds to estimate motion,
            # much more accurate than raw Gazebo wheel odometry which drifts.
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
                # '-d '

                # ── Registration ──────────────────────────────────────────────
                # ICP registration for loop closure (correct for LiDAR-only).
                # Force3DoF false → full 6-DoF pose corrections; setting this
                # true locks roll/pitch and causes vertical drift.
                '--Reg/Strategy 1 '
                '--Reg/Force3DoF false '

                # ── ICP tuning (key fix for misalignment) ─────────────────────
                # VoxelSize 0.1 → downsample to 10 cm voxels BEFORE ICP runs.
                #   Your LiDAR has only 16 vertical scan lines, producing a very
                #   sparse and uneven cloud. Without voxelisation, ICP tries to
                #   match dense horizontal rings against sparse vertical regions
                #   and fails to find correct correspondences → misalignment.
                #   Voxelising first gives a uniform point density so ICP works.
                # PointToPlane true → fit points onto surface normals (walls,
                #   floor). Far more accurate than point-to-point for structured
                #   indoor environments; converges in fewer iterations.
                # Iterations 50 → more convergence steps for sparse clouds.
                # MaxCorrespondenceDistance 0.2 → only pair points within 20 cm;
                #   rejects false matches from the sparse scan pattern.
                # Epsilon 0.001 → stop when pose delta drops below 1 mm.
                # MaxTranslation 1.0 → discard ICP result if pose jumps > 1 m
                #   (false loop-closure guard).
                '--Icp/VoxelSize 0.05 '
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

    return LaunchDescription([
        db_name_arg,
        bridge,
        static_laser_tf,
        rtabmap_launch,
        rviz_node,
    ])