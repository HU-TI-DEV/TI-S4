cmake_minimum_required(VERSION 3.22)

project(recap_cpp_1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Zorgt voor build/compile_commands.json, zodat IntelliSense in VSCode werkt
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Standaard een Debug build: debug-symbolen (-g), geen optimalisatie, asserts actief
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Debug CACHE STRING "Build type" FORCE)
endif()

# 1. Warnings aan. Lees ze! Een groot deel van de bugs in dit project geeft al een warning.
add_compile_options(-Wall -Wextra)

# 2. Sanitizers: het programma controleert zichzelf tijdens het draaien op
#    geheugenfouten (AddressSanitizer) en undefined behaviour (UBSan).
#    Uitzetten (bijvoorbeeld om valgrind te gebruiken):
#        cmake -B build -DENABLE_SANITIZERS=OFF
option(ENABLE_SANITIZERS "Compileer met AddressSanitizer en UndefinedBehaviorSanitizer" ON)
if(ENABLE_SANITIZERS)
    add_compile_options(-fsanitize=address,undefined -fno-omit-frame-pointer)
    add_link_options(-fsanitize=address,undefined)
    # Stop ook bij undefined behaviour (standaard print UBSan alleen en gaat door)
    add_compile_options(-fno-sanitize-recover=undefined)
endif()

# Elke oefening is een eigen executable. Kies de target in de CMake Tools
# statusbalk onderaan VSCode, of bouw alles met: cmake --build build
foreach(oefening 01_functies 02_pointers 03_bughunt)
    add_executable(${oefening} src/${oefening}.cc)
endforeach()
