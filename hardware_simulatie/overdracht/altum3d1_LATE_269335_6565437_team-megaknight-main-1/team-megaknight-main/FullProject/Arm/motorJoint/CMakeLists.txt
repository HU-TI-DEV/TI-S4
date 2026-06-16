add_library(motorJoint STATIC
    motorJoint.cpp
)

target_include_directories(motorJoint PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

target_link_libraries(motorJoint PUBLIC
    gz-transport::gz-transport
    gz-msgs::gz-msgs
)