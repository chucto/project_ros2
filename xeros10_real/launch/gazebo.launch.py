import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    # 1. Khai báo các đường dẫn của package xeros10_real
    package_name = 'xeros10_real'
    pkg_share = get_package_share_directory(package_name)
    urdf_file = os.path.join(pkg_share, 'urdf', 'xeros10.urdf')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'config.rviz')
    
    # (Tùy chọn) Đường dẫn tới file cấu hình RViz nếu bạn đã có file .rviz 
    # rviz_config_file = os.path.join(pkg_share, 'rviz', 'config.rviz')

    # 2. Đọc nội dung file URDF vào một biến chuỗi
    with open(urdf_file, 'r') as infp:
        robot_desc = infp.read()

    # --- ĐÂY LÀ PHẦN QUAN TRỌNG NHẤT ---
    # Python sẽ tìm chữ "$(find xeros10_real)" trong file URDF 
    # và thay nó bằng đường dẫn thật (pkg_share) trước khi gửi cho Gazebo.
    robot_desc = robot_desc.replace('$(find xeros10_real)', pkg_share)
    # ----------------------------------

    # 3. Fix GAZEBO_MODEL_PATH để Gazebo tìm thấy meshes
    pkg_parent = os.path.abspath(os.path.join(pkg_share, ".."))
    set_gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=pkg_parent
    )

    # 4. Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    # 5. Khởi chạy Gazebo
    gazebo_launch_file = os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(gazebo_launch_file),
    )

    # 6. Spawn Robot vào Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-entity', 'xeros10', '-topic', 'robot_description'],
        output='screen'
    )

    # 7. Nạp các Controller
    load_joint_state_broadcaster = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
        output="screen",
    )

    load_arm_controller = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller"],
        output="screen",
    )

    # 8. Tự động mở cửa sổ Terminal riêng cho node điều khiển bàn phím (Nếu bạn muốn)
    arm_teleop_node = Node(
        package='xeros10_real',
        executable='keyboard_arm.py', # Tên file script bạn đã lưu
        name='arm_teleop',
        output='screen',
        prefix=['gnome-terminal -- '] # Lệnh này sẽ bật một cửa sổ đen riêng biệt để bạn nhấn phím
    )
    
    load_joint_state_publisher = Node(
    package='joint_state_publisher',
    executable='joint_state_publisher',
    name='joint_state_publisher',
    parameters=[{
        'use_sim_time': True,
        # Liệt kê các khớp mà Gazebo ĐÃ ĐIỀU KHIỂN để node này bỏ qua
        'source_list': ['joint_states'], # Nó sẽ gộp dữ liệu từ topic này
        'ignore_joints': ['arm1_joint', 'arm2_point'] 
    }]
)

    # 9. Khởi chạy RViz2
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_config_path]
    )
    
    base_teleop_node = Node(
        package='teleop_twist_keyboard',
        executable='teleop_twist_keyboard',
        name='base_teleop',
        prefix=['gnome-terminal -- '], # Mở cửa sổ terminal riêng để nhập phím
        output='screen'
    )

    return LaunchDescription([
        set_gazebo_model_path,
        robot_state_publisher,
        gazebo,
        spawn_robot,
        load_joint_state_broadcaster, 
        load_arm_controller,          
        arm_teleop_node,
        base_teleop_node,
        load_joint_state_publisher,
        rviz_node  # <--- Đã thêm RViz vào danh sách khởi chạy
    ])
