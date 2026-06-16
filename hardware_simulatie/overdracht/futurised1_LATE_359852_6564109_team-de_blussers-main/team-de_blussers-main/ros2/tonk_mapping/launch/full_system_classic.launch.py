from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os
import shutil


def find_terminal():
    candidates = [
        ('kitty',          ['kitty', '--hold', '-e']),
        ('xterm',          ['xterm', '-title', 'WASD Control', '-e']),
        ('gnome-terminal', ['gnome-terminal', '--']),
        ('konsole',        ['konsole', '-e']),
        ('foot',           ['foot']),
        ('alacritty',      ['alacritty', '-e']),
    ]
    for name, prefix in candidates:
        if shutil.which(name):
            return prefix
    print('[WARN] Geen terminal gevonden — WASD control start niet.')
    return None


def find_gz_binary():
    docker_path = '/usr/libexec/gz/sim10/gz-sim-main'
    if os.path.isfile(docker_path):
        return [docker_path]
    if shutil.which('gz'):
        return ['gz', 'sim']
    raise RuntimeError('Gazebo binary niet gevonden. Installeer gz-sim of stel PATH in.')


def find_repo_root():
    repo_root = os.environ.get('TONK_REPO')
    if repo_root and os.path.isdir(os.path.join(repo_root, 'Gazebo')):
        return repo_root
    if os.path.isdir('/workspace/Gazebo'):
        return '/workspace'
    native_path = os.path.expanduser('~/dev/school/S4/team-de_blussers')
    if os.path.isdir(os.path.join(native_path, 'Gazebo')):
        return native_path
    candidate = os.path.dirname(os.path.realpath(__file__))
    for _ in range(8):
        if os.path.isdir(os.path.join(candidate, 'Gazebo')):
            return candidate
        candidate = os.path.dirname(candidate)
    print('[WARN] Repo niet gevonden! Stel TONK_REPO in.')
    return native_path


def generate_launch_description():
    repo_root = find_repo_root()

    models_path = os.path.join(repo_root, 'Gazebo', 'models')
    world_path  = os.path.join(repo_root, 'Gazebo', 'worlds', 'parking_garage.world')
    wasd_binary = os.path.join(repo_root, 'Gazebo', 'models', 'makeTonksGreat', 'build', 'wasd_control')

    sep = ';' if os.name == 'nt' else ':'
    resource_path = sep.join([models_path])

    print(f'[INFO] Repo root:     {repo_root}')
    print(f'[INFO] World:         {world_path}')
    print(f'[INFO] Resource path: {resource_path}')

    rviz_config = PathJoinSubstitution([
        FindPackageShare('tonk_mapping'),
        'rviz',
        'mapping.rviz'
    ])

    gz_cmd = find_gz_binary()

    # ── Gazebo ──────────────────────────────────────────────────────────────
    gazebo = ExecuteProcess(
        cmd=gz_cmd + ['-r', world_path],
        additional_env={
            'QT_QPA_PLATFORM':     'xcb',
            'GZ_SIM_RESOURCE_PATH': resource_path,
        },
        output='screen'
    )

    # ── Gazebo ↔ ROS2 bridge ────────────────────────────────────────────────
    # Bevat: LiDAR, camera (RGB), thermische camera, cmd_vel, IMU, odom, clock
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/lidar/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            '/thermal_camera_8bit/image@sensor_msgs/msg/Image[gz.msgs.Image',
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image',
        ],
        output='screen'
    )

    # ── LiDAR verwerking ────────────────────────────────────────────────────
    lidar_to_pc = Node(
        package='tonk_mapping',
        executable='lidar_to_pointcloud',
        output='screen'
    )

    # ── IMU odometry ────────────────────────────────────────────────────────
    imu_odometry = Node(
        package='tonk_mapping',
        executable='imu_odometry_node',
        output='screen'
    )

    # ── Statische transform map → odom ──────────────────────────────────────
    map_to_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom'],
        output='screen'
    )

    # ── Pathfinding (Dijkstra) ───────────────────────────────────────────────
    path_planner = Node(
        package='tonk_mapping',
        executable='dijkstra_path_planner',
        output='screen'
    )

    # ── Vuur-detectie + navigatie (thermische camera → doel) ────────────────
    fire_nav = Node(
        package='tonk_mapping',
        executable='fire_navigator',
        output='screen'
    )

    # ── Kaart bouwen (occupancy grid van LiDAR) ─────────────────────────────
    # map_builder = Node(
    #     package='tonk_mapping',
    #     executable='map_builder',
    #     output='screen'
    # )

    # ── Persoons-detectie (YOLO + temperatuur-overlay) ──────────────────────
    # Gebruikt /camera/image_raw (RGB bridge) — best.pt is getraind op RGB beelden.
    person_detector = Node(
        package='person_detection',
        executable='person_detector',
        output='screen'
    )

    # ── RViz (mapping config) ───────────────────────────────────────────────
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        additional_env={'QT_QPA_PLATFORM': 'xcb'},
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        bridge,
        lidar_to_pc,
        imu_odometry,
        map_to_odom,
        path_planner,
        fire_nav,
        # map_builder,
        person_detector,
        rviz,
    ])
