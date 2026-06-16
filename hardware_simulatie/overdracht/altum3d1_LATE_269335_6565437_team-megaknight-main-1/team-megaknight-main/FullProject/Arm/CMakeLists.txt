cmake_minimum_required(VERSION 3.14)
project(arm_controller CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ── Gazebo Transport ──────────────────────────────────────────────────────────
find_package(gz-transport REQUIRED)
find_package(gz-msgs      REQUIRED)

# ── Subdirectories (each builds a static library) ─────────────────────────────
add_subdirectory(motorJoint)
add_subdirectory(armControl)
add_subdirectory(rotationControl)

# ── Main executable ───────────────────────────────────────────────────────────
add_executable(arm_controller main.cpp)

target_link_libraries(arm_controller PRIVATE
    armControl
    rotationControl
    pthread
)