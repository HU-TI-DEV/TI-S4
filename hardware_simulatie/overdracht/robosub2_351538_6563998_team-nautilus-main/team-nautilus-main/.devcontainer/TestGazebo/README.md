# Gazebo Test

Use this project to check if all libraries for Gazebo were properly installed. It's a basic C++ program that drives a car in Gazebo using the gz::transport and gz::msgs libraries.

## Testing Gazebo

### Building
To build, use the "Load CMake project" button (right click on CMakeLists.txt first). CMake will automatically build a project for you, and CLion will automatically build a run profile. 

### Running 
First, head into gazebo sim in this directory by using the `gz sim car.sdf` command, Gazebo should show up.

Now, to make it drive, just click on the play button in the top-right corner. Make sure that it's using the build config for the CMake project.