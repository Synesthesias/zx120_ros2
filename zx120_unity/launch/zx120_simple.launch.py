import os
import xacro
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    # パスの定義
    description_pkg = get_package_share_directory('zx120_moveit_config')
    urdf_file = os.path.join(description_pkg, 'config', 'zx120_unity.urdf.xacro')
    initial_positions_file = os.path.join(description_pkg, 'config', 'initial_positions.yaml')
    controllers_yaml = os.path.join(description_pkg, 'config', 'ros2_controllers.yaml')
    unity_pkg = get_package_share_directory('zx120_unity')
    rviz_config = os.path.join(unity_pkg, 'rviz', 'zx120_simple.rviz')

    # xacro展開
    robot_description_config = xacro.process_file(
        urdf_file,
        mappings={
            "initial_positions_file": initial_positions_file
        }
    ).toxml()

    return LaunchDescription([
        # robot_state_publisher
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            parameters=[{'robot_description': robot_description_config}],
            output='screen'
        ),

        # ros2_control_node
        Node(
            package='controller_manager',
            executable='ros2_control_node',
            parameters=[
                {'robot_description': robot_description_config},
                controllers_yaml
            ],
            output='screen'
        ),

        # joint_state_broadcaster spawner
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['joint_state_broadcaster', '--controller-manager-timeout', '50'],
            output='screen'
        ),

        # joint_trajectory_controller spawner
        Node(
            package='controller_manager',
            executable='spawner',
            arguments=['upper_arm_controller', '--controller-manager-timeout', '50'],
            output='screen'
        ),

        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config],
            output='screen'
        )
    ])
