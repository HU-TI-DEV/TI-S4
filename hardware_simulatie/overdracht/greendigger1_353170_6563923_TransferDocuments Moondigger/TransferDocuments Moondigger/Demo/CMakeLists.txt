cmake_minimum_required(VERSION 3.22)

project(AutonomousVehicle)

find_package(gz-transport REQUIRED)
find_package(gz-msgs REQUIRED)
find_package(OpenCV REQUIRED)

add_executable(AutonomousVehicle
# Add the main.cc and aStar.cc when possible
    main.cc
    aStar.cc
    poseSubscriber.cc
    poseSubscriber.hpp
    driving.cc
    objectRecognition.cc
    objectRecognition.hpp
)

target_include_directories(AutonomousVehicle PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR} # Finds root of folder
    ${CMAKE_CURRENT_SOURCE_DIR}/DistanceCalculations  # Finds calcs and constants
    ${OpenCV_INCLUDE_DIRS} # Finds openCV specific includes
)

target_link_libraries(AutonomousVehicle PRIVATE
    gz-transport::gz-transport
    gz-msgs::gz-msgs
    ${OpenCV_LIBS}
)