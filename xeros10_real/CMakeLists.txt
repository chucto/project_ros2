cmake_minimum_required(VERSION 3.5)
project(xeros10_real)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(robot_state_publisher REQUIRED)
find_package(gazebo_ros REQUIRED)

install(
  DIRECTORY urdf launch meshes config scripts rviz
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/keyboard_arm.py
  DESTINATION lib/${PROJECT_NAME}
)
ament_package()
