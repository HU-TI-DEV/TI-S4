# Gazebo installation on Apple M1 
by: [Ingmar van de Sande](https://github.com/ingmarvdsande/gazeboinstallog/blob/main/logbook_Gazebo.md)
modified by: H. Snippe

### Step 1: Installation preparation

Make sure you have xQuartz terminal for MacOS installed, furthermore you'll need Homebrew. You could download a second terminal, as you'll need one arm64 and one x86 terminal and it's nice to have a separate dedicated terminal for this. However, it's not required. You could turn Rosetta on and off on MacOS terminal. Up to you. If you are installing a second terminal iTerm 2 is recommended.

### Step 2: Homebrew and Rosetta

We're going to install Ogre1.9 and Ogre2.3, alongside a few other dependencies. These rendering libraries are required for Gazebo. This is the most annoying part though. Go to your Applications folder in Finder, scroll down to the terminal app you wish to use for x86, right click on it and press "get info". There you'll find a checkbox with the text "Open using Rosetta", check this box. Now open this terminal. 

Now here comes the fun part, because we have to install a different version of Brew for X86_64 installations. We can install this by running the following command: 

```bash
arch -x86_64 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Follow the instructions displayed on screen, so you can add Brew to your path. 

### Step 3: Installation of Ogre

The time has arrived, we are going to install Ogre. 
We're going to run the following 2 commands:

```bash
brew tap osrf/simulation

brew install assimp boost bullet cmake cppzmq dartsim doxygen eigen fcl ffmpeg flann freeimage freetype gdal gflags google-benchmark gts ipopt jsoncpp libccd libyaml libzzip libzip nlopt ode open-scene-graph ossp-uuid ogre1.9 ogre2.3 pkg-config protobuf qt@5 qwt-qt5 rapidjson ruby tbb tinyxml tinyxml2 urdfdom zeromq
```

Here we're installing a bunch of dependencies Gazebo requires. I would strongly suggest following the on screen instructions in regards to adding Qt5 and Ruby to your path. Run all of them.

Okay, now we have installed all required dependencies. 

### Step 4: Installation of Gazebo

Now open a different terminal, one that does not use Rosetta. You can do this by unchecking the box we checked earlier in the Applications menu, or by running a different terminal app. We recommend keeping the iTerm2 with Rosetta enabled, and running the following commands in MacOS terminal. 
**You can run "Arch" in terminal to check if you're running it in Arm64 architecture. If it returns "Arm64", you're good to go**
The following command will ensure we can have enough files open simultaneously, so that we can install Gazebo.

```bash
ulimit -n 1024
```

```bash
brew tap osrf/simulation
brew install gz-ionic
```
With this command, we're actually finally installing Gazebo. 

### Step 5: Launching Gazebo 

If everything went well, we have now installed Gazebo. You can test this by running the following command. Here we run the server.
```bash
gz sim -v 4 shapes.sdf -s
```
Open a second terminal to run the GUI.
```bash
gz sim -v 4 -g
```

If everything went well, you will see a GUI with shapes. Congrats, Gazebo has been installed!

## References

- Logbook for installation of Gazebo on M1 Macbook Pro [https://github.com/ingmarvdsande/gazeboinstallog/blob/main/logbook_Gazebo.md](<https://github.com/ingmarvdsande/gazeboinstallog/blob/main/logbook_Gazebo.md>)