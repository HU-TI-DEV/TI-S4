cmake_minimum_required(VERSION 3.10)
project(cmd_vel_publisher)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(gz-transport13 REQUIRED CONFIG)
find_package(gz-msgs10 REQUIRED)

add_executable(cmd_vel_publisher publisher.cc)
add_executable(lidar_subscriber lidar_subscriber.cc)
add_executable(wasd_control wasd_control.cc)
add_executable(thermal_camera_test thermal_camera_test.cc)

target_link_libraries(thermal_camera_test
    gz-transport13::gz-transport13
    gz-msgs10::gz-msgs10
)

target_link_libraries(cmd_vel_publisher
    gz-transport13::gz-transport13
    gz-msgs10::gz-msgs10
)

target_link_libraries(lidar_subscriber
    gz-transport13::gz-transport13
    gz-msgs10::gz-msgs10
)

target_link_libraries(wasd_control
    gz-transport13::gz-transport13
    gz-msgs10::gz-msgs10
)