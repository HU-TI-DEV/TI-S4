from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch.substitutions import PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os
import shutil


# ─────────────────────────────────────────────────────────────────────────────
#  Full system launch — 3D SLAM (KISS-ICP) + navigatie + vuur + slang + persoon
#
#  Dit is de complete alles-in-één launch. Verschil met full_system_classic.launch.py:
#    - KISS-ICP doet de localisatie en publiceert de TF  odom -> base_link
#      (scan-matching op de 3D LiDAR), i.p.v. de wiel-odometrie van imu_odometry.
#    - map_accumulator bouwt een PERSISTENTE 2D /map op (i.p.v. per-frame in de planner).
#    - de dijkstra-planner draait in 'use_external_map'-modus: hij leest /map en
#      haalt zijn positie uit TF.
#    - GEEN imu_odometry_node (KISS-ICP bezit odom->base_link); map->odom is identity.
#
#  Nodes: gazebo, bridge, lidar_to_pointcloud, kiss_icp, map_accumulator,
#         dijkstra_path_planner, fire_navigator, hose_controller,
#         person_detector, rviz.
# ─────────────────────────────────────────────────────────────────────────────


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

    sep = ';' if os.name == 'nt' else ':'
    resource_path = sep.join([models_path])

    print(f'[INFO] Repo root:     {repo_root}')
    print(f'[INFO] World:         {world_path}')
    print(f'[INFO] Resource path: {resource_path}')

    rviz_config = PathJoinSubstitution([
        FindPackageShare('tonk_mapping'), 'rviz', 'mapping.rviz'
    ])

    gz_cmd = find_gz_binary()

    # ── Gazebo ──────────────────────────────────────────────────────────────
    gazebo = ExecuteProcess(
        cmd=gz_cmd + ['-r', world_path],
        additional_env={
            'QT_QPA_PLATFORM':      'xcb',
            'GZ_SIM_RESOURCE_PATH': resource_path,
        },
        output='screen'
    )

    # use_sim_time op ALLE nodes: Gazebo publiceert sim-tijd (/clock) en stempelt
    # alle data (pointclouds, TF) daarmee. Zonder dit draaien de nodes op wandklok
    # en gooit de tf2-buffer de sim-gestempelde odom->base_link (van KISS-ICP) weg
    # als "te oud" -> "two unconnected trees" -> planner krijgt geen pose -> robot
    # rijdt niet. Met sim-tijd kloppen klok en timestamps overal.
    sim_time = {'use_sim_time': True}

    # ── Gazebo ↔ ROS2 bridge ────────────────────────────────────────────────
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
        parameters=[sim_time],
        output='screen'
    )

    # ── Statische map → odom (identity) ───────────────────────────────────────
    # KISS-ICP levert odom → base_link. Deze identity-transform geeft een nette
    # 'map'-frame bovenaan de tree (conventie: map → odom → base_link → lidar).
    # Bij een SLAM met loop-closure zou dit de globale correctie zijn; KISS-ICP
    # heeft die niet, dus identity.
    map_to_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'odom'],
        parameters=[sim_time],
        output='screen'
    )

    # ── LiDAR verwerking (publiceert /lidar/pointcloud + base_link→lidar TF) ──
    lidar_to_pc = Node(
        package='tonk_mapping',
        executable='lidar_to_pointcloud',
        parameters=[sim_time],
        output='screen'
    )

    # ── KISS-ICP 3D SLAM ──────────────────────────────────────────────────────
    # Subscribet op /lidar/pointcloud, publiceert TF  odom → base_link.
    kiss_icp = Node(
        package='kiss_icp',
        executable='kiss_icp_node',
        name='kiss_icp_node',
        remappings=[('pointcloud_topic', '/lidar/pointcloud')],
        parameters=[{
            **sim_time,
            'base_frame':       'base_link',
            'lidar_odom_frame': 'odom',
            'publish_odom_tf':  True,
            'invert_odom_tf':   False,
            'data.deskew':      False,    # sim-cloud heeft geen per-punt timestamps
            'data.max_range':   40.0,     # = LiDAR <range><max>
            'data.min_range':   0.5,
        }],
        output='screen'
    )

    # ── Persistente 2D-kaart uit de SLAM-gecorrigeerde LiDAR ──────────────────
    map_accumulator = Node(
        package='tonk_mapping',
        executable='map_accumulator',
        parameters=[{**sim_time, 'global_frame': 'odom'}],
        output='screen'
    )

    # ── Pathfinding (Dijkstra) op de externe SLAM-kaart ───────────────────────
    path_planner = Node(
        package='tonk_mapping',
        executable='dijkstra_path_planner',
        parameters=[{
            **sim_time,
            'use_external_map': True,
            'global_frame':     'odom',
            'base_frame':       'base_link',
        }],
        output='screen'
    )

    # ── Vuur-detectie + navigatie (thermische camera → doel) ─────────────────
    fire_nav = Node(
        package='tonk_mapping',
        executable='fire_navigator',
        parameters=[sim_time],
        output='screen'
    )

    # ── Blusslang turret controller (/fire_marker + /odom → pan/tilt) ─────────
    hose_ctrl = Node(
        package='tonk_mapping',
        executable='hose_controller',
        parameters=[sim_time],
        output='screen'
    )

    # ── Persoons-detectie (YOLO) ──────────────────────────────────────────────
    person_detector = Node(
        package='person_detection',
        executable='person_detector',
        parameters=[sim_time],
        output='screen'
    )

    # ── RViz ──────────────────────────────────────────────────────────────────
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[sim_time],
        additional_env={'QT_QPA_PLATFORM': 'xcb'},
        output='screen'
    )

    return LaunchDescription([
        gazebo,
        bridge,
        map_to_odom,
        lidar_to_pc,
        kiss_icp,
        map_accumulator,
        path_planner,
        fire_nav,
        hose_ctrl,
        person_detector,
        rviz,
    ])
