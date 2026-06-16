cmake_minimum_required(VERSION 3.10)
project(cmd_vel_publisher)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(gz-transport13 REQUIRED)
find_package(gz-msgs10 REQUIRED)

add_executable(thermal_camera_test thermal_camera_test.cc)

target_link_libraries(thermal_camera_test
    gz-transport13::gz-transport13
    gz-msgs10::gz-msgs10
)