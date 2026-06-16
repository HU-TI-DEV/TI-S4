cmake_minimum_required(VERSION 3.22.1 FATAL_ERROR)
project(IKTest)

set(CMAKE_CXX_STANDARD 17)

find_package(gz-transport REQUIRED)
find_package(gz-msgs REQUIRED)

add_library(common INTERFACE)
add_subdirectory(IKSolver)
add_subdirectory(ArmCoordinatenMovement)
add_subdirectory(RobotArm)


target_include_directories(common INTERFACE
        ${CMAKE_CURRENT_SOURCE_DIR}/common
)

add_executable(IKTest main.cpp)

target_link_libraries(IKTest
        ArmCoordinatenMovement
        IKSolver
        RobotArm
        common
        gz-transport::core
        gz-msgs::gz-msgs)