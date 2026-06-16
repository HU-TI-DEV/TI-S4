cmake_minimum_required(VERSION 3.16)
project(joint_mover_executable)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Try commonly installed gz-transport package variants.
find_package(gz-transport14 QUIET)
find_package(gz-transport13 QUIET)
find_package(gz-transport12 QUIET)
find_package(gz-transport QUIET)

if(TARGET gz-transport14::core)
	set(GZ_TRANSPORT_TARGET gz-transport14::core)
elseif(TARGET gz-transport13::core)
	set(GZ_TRANSPORT_TARGET gz-transport13::core)
elseif(TARGET gz-transport12::core)
	set(GZ_TRANSPORT_TARGET gz-transport12::core)
elseif(TARGET gz-transport::core)
	set(GZ_TRANSPORT_TARGET gz-transport::core)
else()
	message(FATAL_ERROR "Could not find a compatible gz-transport package")
endif()

# Try commonly installed gz-msgs package variants.
find_package(gz-msgs11 QUIET)
find_package(gz-msgs10 QUIET)
find_package(gz-msgs9 QUIET)
find_package(gz-msgs QUIET)

if(TARGET gz-msgs11::core)
	set(GZ_MSGS_TARGET gz-msgs11::core)
elseif(TARGET gz-msgs10::core)
	set(GZ_MSGS_TARGET gz-msgs10::core)
elseif(TARGET gz-msgs9::core)
	set(GZ_MSGS_TARGET gz-msgs9::core)
elseif(TARGET gz-msgs::core)
	set(GZ_MSGS_TARGET gz-msgs::core)
else()
	message(FATAL_ERROR "Could not find a compatible gz-msgs package")
endif()

add_executable(movement main.cpp pid_control.cpp inverse_kinematics.cpp)
target_link_libraries(movement PRIVATE ${GZ_TRANSPORT_TARGET} ${GZ_MSGS_TARGET})
