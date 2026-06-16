from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    rviz_config = os.path.join(
        get_package_share_directory('person_detection'),
        'rviz',
        'person_detection.rviz'
    )

    detector = Node(
        package='person_detection',
        executable='person_detector',
        output='screen'
    )

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        output='screen',
        additional_env={'QT_QPA_PLATFORM': 'xcb'}
    )

    return LaunchDescription([detector, rviz])
