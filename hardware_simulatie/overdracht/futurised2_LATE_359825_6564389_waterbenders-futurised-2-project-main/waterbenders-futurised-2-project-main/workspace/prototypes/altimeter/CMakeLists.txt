cmake_minimum_required(VERSION 3.10)

project(altimeter_prototype)

# Find Gazebo transport and msgs
find_package(gz-transport REQUIRED)
find_package(gz-msgs REQUIRED)

# Create executable
add_executable(altimeter_prototype altimeter_prototype.cc)

# Link libraries
target_link_libraries(altimeter_prototype
  gz-transport::gz-transport
  gz-msgs::gz-msgs
)