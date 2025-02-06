cmake_minimum_required(VERSION 3.27)

project(buggy_project)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Maak een executable van het main.cc bestand
add_executable(buggy_project src/main.cc)
