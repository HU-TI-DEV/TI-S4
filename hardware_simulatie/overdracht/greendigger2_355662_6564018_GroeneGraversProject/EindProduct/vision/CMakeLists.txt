cmake_minimum_required(VERSION 3.10)

project(camera)

set(CMAKE_CXX_STANDARD 17)

find_package(OpenCV REQUIRED)

find_package(gz-transport REQUIRED)
find_package(gz-msgs REQUIRED)

add_executable(camera main.cc camera.cc)

target_link_libraries(camera
    ${OpenCV_LIBS}
    gz-transport::core
    gz-msgs::core
)