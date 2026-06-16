from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os
import shutil


def find_terminal():
    """Return [terminal, ...args...] prefix to run a command in a new window, or None."""
    candidates = [
        ('kitty',        ['kitty', '--hold', '-e']),
        ('xterm',        ['xterm', '-title', 'WASD Control', '-e']),
        ('gnome-terminal', ['gnome-terminal', '--']),
        ('konsole',      ['konsole', '-e']),
        ('foot',         ['foot']),
        ('alacritty',    ['alacritty', '-e']),
    ]
    for name, prefix in candidates:
        if shutil.which(name):
            return prefix
    print('[WARN] No terminal emulator found — WASD control will not launch.')
    return None


def find_gz_binary():
    # 1) docker: absolute path
    docker_path = '/usr/libexec/gz/sim10/gz-sim-main'
    if os.path.isfile(docker_path):
        return [docker_path]

    # 2) native (Arch/Ubuntu): gz sim on PATH
    if shutil.which('gz'):
        return ['gz', 'sim']

    raise RuntimeError('Cannot find Gazebo binary. Install gz-sim or set PATH correctly.')


def find_repo_root():
    # detect where repo is
    # 1) env var override
    repo_root = os.environ.get('TONK_REPO')
    if repo_root and os.path.isdir(os.path.join(repo_root, 'Gazebo')):
        return repo_root
    
    # 2) devcontainer (windows team)
    if os.path.isdir('/workspace/Gazebo'):
        return '/workspace'
    
    # 3) eden's arch native fallback
    native_path = os.path.expanduser('~/dev/school/S4/team-de_blussers')
    if os.path.isdir(os.path.join(native_path, 'Gazebo')):
        return native_path
    
    # 4) auto-detect: search from start file
    candidate = os.path.dirname(os.path.realpath(__file__))
    for _ in range(8):
        if os.path.isdir(os.path.join(candidate, 'Gazebo')):
            return candidate
        candidate = os.path.dirname(candidate)
    
    # Fallback met waarschuwing
    print('[WARN] Cannot locate repo! Set TONK_REPO env var.')
    return native_path


def generate_launch_description():
    repo_root = find_repo_root()
    
    models_path = os.path.join(repo_root, 'Gazebo', 'models')
    people_path = os.path.join(repo_root, 'Gazebo', 'models')
    world_path = os.path.join(repo_root, 'Gazebo', 'worlds', 'parking_garage.world')
    wasd_binary = os.path.join(repo_root, 'Gazebo', 'models', 'makeTonksGreat', 'build', 'wasd_control')
    
    # Combineer model paths met `:` (Linux) of `;` (Windows native — niet relevant voor Docker/WSL)
    sep = ';' if os.name == 'nt' else ':'
    resource_path = sep.join([models_path, people_path])
    
    print(f'[INFO] Repo root: {repo_root}')
    print(f'[INFO] World: {world_path}')
    print(f'[INFO] Resource path: {resource_path}')

    rviz_config = PathJoinSubstitution([
        FindPackageShare('tonk_mapping'),
        'rviz',
        'mapping.rviz'
    ])

    gz_cmd = find_gz_binary()

    gazebo = ExecuteProcess(
        cmd=gz_cmd + ['-r', world_path],
        additional_env={
            'QT_QPA_PLATFORM': 'xcb',
            'GZ_SIM_RESOURCE_PATH': resource_path,
        },
        output='screen'
    )

    terminal = find_terminal()
    wasd = ExecuteProcess(
        cmd=terminal + [wasd_binary],
        output='screen'
    ) if terminal else None

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/lidar/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked',
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist',
            '/imu@sensor_msgs/msg/Imu[gz.msgs.IMU',
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry',
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock',
            # Thermische camera: L8 (8-bit grayscale) → mono8 in ROS2
            '/thermal_camera_8bit/image@sensor_msgs/msg/Image[gz.msgs.Image',
            # Blusslang turret: ROS2 → Gazebo JointPositionController
            '/hose_pan_cmd@std_msgs/msg/Float64]gz.msgs.Double',
            '/hose_tilt_cmd@std_msgs/msg/Float64]gz.msgs.Double',
        ],
        output='screen'
    )

    lidar_to_pc = Node(
        package='tonk_mapping',
        executable='lidar_to_pointcloud',
        output='screen'
    )

    imu_odometry = Node(
        package='tonk_mapping',
        executable='imu_odometry_node',
        output='screen'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        additional_env={'QT_QPA_PLATFORM': 'xcb'},
        output='screen'
    )

    # Statische transform: map → odom (identiteit bij opstart)
    # Zorgt dat RViz alles in het map-frame kan tonen.
    map_to_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom'],
        output='screen'
    )

    # Autonome pathfinding node (Dijkstra)
    path_planner = Node(
        package='tonk_mapping',
        executable='dijkstra_path_planner',
        output='screen'
    )

    # Vuurdetectie + navigatie: thermal camera → LiDAR bearing → /goal_pose
    fire_nav = Node(
        package='tonk_mapping',
        executable='fire_navigator',
        output='screen'
    )

    # Blusslang turret controller: /fire_marker + /odom → pan/tilt oscillatie
    hose_ctrl = Node(
        package='tonk_mapping',
        executable='hose_controller',
        output='screen'
    )

    actions = [gazebo, bridge, lidar_to_pc, imu_odometry, map_to_odom, path_planner, fire_nav, hose_ctrl, rviz]
    if wasd:
        actions.insert(1, wasd)

    return LaunchDescription(actions)