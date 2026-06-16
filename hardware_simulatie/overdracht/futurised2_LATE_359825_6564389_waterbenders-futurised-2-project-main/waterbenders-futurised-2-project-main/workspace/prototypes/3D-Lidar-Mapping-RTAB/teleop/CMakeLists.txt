cmake_minimum_required(VERSION 3.10)
project(gz_teleop_keyboard)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(PkgConfig REQUIRED)
pkg_check_modules(SDL2 REQUIRED sdl2)

find_package(gz-transport REQUIRED)
find_package(gz-msgs REQUIRED)

add_executable(teleop teleop.cc)

target_include_directories(teleop PRIVATE ${SDL2_INCLUDE_DIRS})
target_link_libraries(teleop
  ${SDL2_LIBRARIES}
  gz-transport::gz-transport
  gz-msgs::gz-msgs
)