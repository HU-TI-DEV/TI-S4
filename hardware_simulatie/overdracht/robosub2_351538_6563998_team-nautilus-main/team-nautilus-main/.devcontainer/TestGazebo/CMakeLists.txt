cmake_minimum_required(VERSION 3.22.1)
project(CarTestWorld)

# Find the Gazebo msgs library
find_package(gz-msgs REQUIRED)
find_package(gz-transport REQUIRED)
add_executable(main.cpp
        "main.cpp"
)

target_link_libraries(main.cpp
        gz-transport::gz-transport
        gz-msgs::gz-msgs
)