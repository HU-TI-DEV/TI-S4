add_library(rotationControl STATIC
    rotationControl.cpp
)

target_include_directories(rotationControl PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

target_link_libraries(rotationControl PUBLIC
    motorJoint
)