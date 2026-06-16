cmake_minimum_required(VERSION 3.22.1)
project(IKSolver)

# Compile all the source files inside this directory into a static library
add_library(IKSolver STATIC
        ForwardKinematics.cpp
        InverseKinematics.cpp
)

# Expose this folder as an include directory to anyone who links this library
target_include_directories(IKSolver PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# If these files use Gazebo, link them here too
target_link_libraries(IKSolver PRIVATE
        common
        ArmCoordinatenMovement
        gz-transport::core
        gz-msgs::gz-msgs
)