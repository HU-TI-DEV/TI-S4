cmake_minimum_required(VERSION 3.22.1)
project(ArmCoordinatenMovement)

# Compile all the source files inside this directory into a static library
add_library(ArmCoordinatenMovement STATIC
        Joint.cpp
        JointController.cpp
        # Note: Do NOT include main.cpp here if it's meant to be an independent test
)

# Expose this folder as an include directory to anyone who links this library
target_include_directories(ArmCoordinatenMovement PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# If these files use Gazebo, link them here too
target_link_libraries(ArmCoordinatenMovement PRIVATE
        IKSolver
        common
        gz-transport::core
        gz-msgs::gz-msgs
)