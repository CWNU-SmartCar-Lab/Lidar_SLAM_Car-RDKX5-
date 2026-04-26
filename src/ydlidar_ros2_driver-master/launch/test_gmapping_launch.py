import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration, EqualsSubstitution


def generate_launch_description():
    # 1. 声明参数，并直接给一个默认值 'x3'，解决环境变量为空导致的报错
    lidar_type_arg = DeclareLaunchArgument(
        name='lidar_type',
        default_value='x3',
        description='The type of lidar'
    )

    lidar_type = LaunchConfiguration('lidar_type')

    # 2. 启动雷达节点 (修正了原本代码中的 ydliar 拼写错误，直接调用 x3_ydlidar_launch.py)
    lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ydlidar_ros2_driver'), 'launch', 'x3_ydlidar_launch.py')
        )
    )

    # 3. 启动 4ros 版本的建图 (升级为 Jazzy 最新语法，消灭黄色警告)
    slam_4ros_gmapping_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_gmapping'), 'launch', 'slam_4ros_gmapping.launch.py')
        ),
        condition=IfCondition(EqualsSubstitution(lidar_type, '4ros'))
    )

    # 4. 启动 x3 版本的建图 (升级为 Jazzy 最新语法，消灭黄色警告)
    # 注意：这里调用的是我们之前修复好的 gmapping_x3_launch.py
    slam_x3_gmapping_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('slam_gmapping'), 'launch', 'gmapping_x3_launch.py')
        ),
        condition=UnlessCondition(EqualsSubstitution(lidar_type, '4ros'))
    )

    return LaunchDescription([
        lidar_type_arg,
        lidar_launch,
        slam_4ros_gmapping_launch,
        slam_x3_gmapping_launch
    ])