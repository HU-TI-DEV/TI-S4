cmake_minimum_required(VERSION 3.8)
project(tonk_mapping)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2 REQUIRED)
find_package(visualization_msgs REQUIRED)

add_executable(lidar_to_pointcloud src/lidar_to_pointcloud.cc)
ament_target_dependencies(lidar_to_pointcloud
  rclcpp
  sensor_msgs
  geometry_msgs
  tf2_ros
  tf2
)

add_executable(imu_odometry_node src/imu_odometry_node.cc)
ament_target_dependencies(imu_odometry_node
  rclcpp
  sensor_msgs
  nav_msgs
  geometry_msgs
  tf2_ros
  tf2
)

add_executable(dijkstra_path_planner src/dijkstra_path_planner.cc)
ament_target_dependencies(dijkstra_path_planner
  rclcpp
  sensor_msgs
  nav_msgs
  geometry_msgs
  visualization_msgs
  tf2
  tf2_ros
)

add_executable(fire_navigator src/fire_navigator.cc)
ament_target_dependencies(fire_navigator
  rclcpp
  sensor_msgs
  nav_msgs
  geometry_msgs
  visualization_msgs
  tf2
  tf2_ros
)

add_executable(map_accumulator src/map_accumulator.cc)
ament_target_dependencies(map_accumulator
  rclcpp
  sensor_msgs
  nav_msgs
  geometry_msgs
  tf2
  tf2_ros
)

add_executable(hose_controller src/hose_controller.cc)
ament_target_dependencies(hose_controller
  rclcpp
  std_msgs
  visualization_msgs
  nav_msgs
  geometry_msgs
  tf2
  tf2_ros
)

install(TARGETS lidar_to_pointcloud imu_odometry_node dijkstra_path_planner fire_navigator map_accumulator hose_controller
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY launch rviz
  DESTINATION share/${PROJECT_NAME}/)

ament_package()