# Info
The reason for creating a teleop file is to be able to steer and move simultaneously since the `TriggeredPublisher` plugin doesn't allow this.

# Instructions
## Generating `teleop` file in build folder
1. Inside this folder: `kamerMetObjecten`, run 
    ```bash
    mkdir build
    cd build
    cmake ..
    make
    ```

2. If that fails you need to install `sdl2` by running
    ```bash
    apt update && apt install -y libsdl2-dev
    ```

3. Navigate back to `cd /workspace/groepsProject/omgeving/kamerMetObjecten` and run 
    ```bash
    rm -rf build
    ```
    to remove the failed build-folder with its content.

4. Rerun the commands from step 1 to create the `teleop` file. This should now be made succesfully.


## Using the `teleop` file for navigation
1. Navigate into the **build folder of** `/workspace/groepsProject/omgeving/kamerMetObjecten` and run 
    ```bash
    ./teleop
    ```

- a small windows will popup which you will need to click on later

2. Open a new terminal in `/workspace/groepsProject/omgeving/kamerMetObjecten` and run the [roomWithObjects.sdf file](./roomWithObjects.sdf)

3. Click on the play button of the gazebo world

4. Now click on the small teleop-window and simply navigate using the arrow keys