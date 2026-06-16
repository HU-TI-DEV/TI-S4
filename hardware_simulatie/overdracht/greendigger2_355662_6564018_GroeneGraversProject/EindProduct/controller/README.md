# Controller

## description
This folder is made for the intelligence and movement behind the excavator. We have made seperate files for the angle calculations of the joints, and for the PID controller that all the joints use to move smoothly. In the main is where all the joints get defined and connected to their respective PID controllers and activated. Further in de while(!g_terminated) loop is the intelligence behind the digging operation.

## File structure

    ├───controller
    |   ├───build/             # Folder where the executables and generated build files end up
    |   ├───calc_Functions.cc  # Source file where the kinematics and point generator functions are defined
    |   ├───calc_Functions.hh  # Header file for the the inverse kinematics function and point generator
    |   ├───CMakeLists.txt     # File where possible executables are defined, for linking files to an executable
    |   ├───joint_PID.cc      # Source file for the jointPID class, contains PID tuning and gazebo connection logic
    |   ├───joint_PID.hh      # Header file for the jointPID class, contains the class layout and functions
    |   ├───main.cc           # All other code gets implemented here, also digging loop's location
    |   ├───README.md         # This file
    │   └───stopSignal.txt    # Contains a boolean indicating whether a tree was detected
    ├───models
    ├───vision


## Files with more explanation

### calc_Functions.cc

Within this file are the definitions of the setTargetPoint and pointGenerator functions. 

- The setTargetPoint functions uses the the variables:(double x, double y, double z, double L1, double L2, double& q1, double& q2, double& q3). The x,y and z are the coordinates of the desired end-affector position, L1 and L2 are the lengths of the arm-links and q1, q2 and q3 are placeholder variables that end up saving the calculated radians. Explanations of the inverse kinematics and the code are given in the cc file at the top and throughout the function. Most importantly is this link: https://motion.cs.illinois.edu/RoboticSystems/InverseKinematics.html 

- The pointGenerator function gives the possibility to customize the amount of digging motions, or points, the arm needs to complete. The generator uses the variables:(float z_coordinate, float radius, int amount_setpoints). The z-coordinate is the depth at which the arm will dig(a higher z will make it go lower(no idea why but it works, probably some orientation definition in the sdf-file)), radius is the radius is the distance the arm will dig(for MVP 2.5 metres) and amount_setpoints is ofcourse the amount of in between points the arm will dig to. The idea is that the functions creates an amount of points on a half circle so the arm can dig towards every point with in between steps. Further explained in the main section ahead.

### joint_PID.cc

This file contains the jointClass-class, this class has a few functions. 

- jointPID(double setpoint, double Kp, double Ki, double Kd, std::string joint_name, std::string publish_topic, std::string subscribe_topic):
Technically a constructer, it asks a initial setpoint as the desired angle the joint has to reach. Furthermore, the Kp, Ki and Kd variables, these are the PID gains used to compute a command from the error. The error is the difference between the currect joint angle and the desired angle. Tuning these gains is very important as it changes how it moves from angle to angle. Lastly, it asks for the joint_name, publish_topic and subscribe_topic. These variables correspond to the correct names in the .sdf file of the excavator. It uses joint_name for gathering the right joint information, since it gathers all the joints information. publish_topic is the name of the topic where the joint gets commanded with a certain velocity, subscribe_topic is the topic name where it can gather the joints current angle to compare it to the desired angle.

- changeSetpoint(double newSetpoint):
This function simply changes the setpoint of the joint, making it go to a new angle.

- onJointState(const gz::msgs::Model &msg):
This function is the callback function that can keep running in the background after activating. This function keeps gathering the current joint angle, compares it to the setpoint and then determines the correct angle velocity and publishes that to the joint. Here the PID gains are used, in our main implementation we kept the I-gains 0. As this would make the arm rise over time, but many PID systems can operate without the I-gain. 

- activate(gz::transport::Node& node):
This function activates the onJointState callback function and connects it to the gazebo environment through the node.

### main.cc

Within this file are the implementations of the made functions and classes. Also the while loop contains the digging motion loop with the vision part implemented as an interupt. 

- The while loop within int main() contains a loop to go through the list of points generated previously by the generator. For every point, the code runs a loop of a custom amount of steps the arm needs to complete in between the origin of the arm towards the point. More steps means more in between points, so a smoother motion, 10 works fine in our tests. After every point the code checks the stopSignal.txt file with the stopSignal() function, here if the camera detected a tree the code breaks and starts the loop over. If there isn't a detected tree, the arm goes to the path of the next point while lifting first.

### CMakeLists.txt

File to link all the files that get compiled, we used a template from school and added the neccesary details:

    if (EXISTS "${CMAKE_SOURCE_DIR}/main.cc")
        add_executable(main main.cc calc_Functions.cc joint_PID.cc)
        target_link_libraries(main gz-transport::core)
    endif()

This is the executable the final version and run.sh uses. It makes sure all the neccesary files get compiled with the main. The resulting executable ends up in the build-map.


### stopSignal.txt
This text file connects the C++ controller and the Python vision script (vision.py). 
* 0: Everything is safe. The excavator continues digging.
* 1: The camera detected a tree. The controller stops the arm immediately and goes back to its beginning position.