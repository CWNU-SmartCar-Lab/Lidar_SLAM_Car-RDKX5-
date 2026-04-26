import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('slam_gmapping')
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'view_gmapping.rviz')
    param_file = os.path.join(pkg_share, 'params', 'slam_gmapping.yaml')

    return LaunchDescription([
        # 1. 核心 SLAM 建图节点 (您之前漏掉了这个最关键的！)
        Node(
            package='slam_gmapping',
            executable='slam_gmapping',
            name='slam_gmapping',        # 使用 name 而不是 namespace
            output='screen',
            parameters=[param_file]
        ),
        # 2. 坐标系转换节点
        Node(
            package='slam_gmapping',
            executable='transform',
            name='transform',            # 使用 name 而不是 namespace
            output='screen',
            parameters=[{'parents_frame': "odom",
                         'child_frame': "laser",
                         'x': 0.1,
                         'y': 0.2,
                         'z': 0.5,
                         'roll': 0.0,
                         'pitch': 0.0,
                         'yaw': 0.0}],
        ),
        # 3. 静态 TF 发布
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='laser_to_base_link',   # 使用 name 而不是 namespace
            output='screen',
            arguments=['0', '0', '1', '0', '0', '0', 'laser', 'base_link']
        ),
        # 4. RViz2 可视化
        Node(
            package='rviz2',
            executable='rviz2',
            name='map_rviz',             # 使用 name 而不是 namespace
            output='screen',
            arguments=['-d', rviz_config_file],
        )
    ])