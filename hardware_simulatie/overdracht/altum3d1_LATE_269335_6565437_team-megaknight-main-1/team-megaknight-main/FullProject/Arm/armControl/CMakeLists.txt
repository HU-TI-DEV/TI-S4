add_library(armControl STATIC
    armControl.cpp
)

target_include_directories(armControl PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

target_link_libraries(armControl PUBLIC
    motorJoint
)