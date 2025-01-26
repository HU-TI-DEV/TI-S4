### Gazebo install on Mac OS X

Gazebo install on Mac OS X. Tested on Mac M4 with Sequoia 15.1.1. Date: 23-01-2025

Source: [https://gazebosim.org/docs/latest/install_osx_src/](https://gazebosim.org/docs/latest/install_osx_src/)

- Check if you have xQuartz x terminal for Mac OS

- Check if Homebrew package manager is installed

```bash
brew tap osrf/simulation
brew update
```

- Check if Xcode Command Line Tools are installed

- Check if you use Python3

Install vcstool and colcon from PyPI using pip install:

```bash
python3 -m pip install -U colcon-common-extensions vcstool
```

Make a workspace. For now I have chosen to use workspace but you could rename it into something useful e.g. gazebo.

```bash
mkdir -p ~/workspace/src
cd ~/workspace/src
```

```bash
curl -OL https://raw.githubusercontent.com/gazebo-tooling/gazebodistro/master/collection-ionic.yaml
```

Upgrade pip.
```bash
/Library/Developer/CommandLineTools/usr/bin/python3 -m pip install --upgrade pip
```

Make the binaries available and add the bin folder to the PATH.

```bash
sudo nano /etc/paths
```

Add /Users/<your username>/Library/Python/3.9/bin
Save and quit. Restart your terminal and navigate to your src folder.

```bash
sudo pip install vcstool
```

```bash
vcs import < collection-ionic.yaml
```

Your folder should now contain all the sources!

Install general dependencies:

```bash
brew install assimp boost bullet cmake cppzmq dartsim doxygen eigen fcl ffmpeg flann freeimage freetype gdal gflags google-benchmark gts ipopt jsoncpp libccd libyaml libzzip libzip nlopt ode open-scene-graph ossp-uuid ogre1.9 ogre2.3 pkg-config protobuf qt@5 qwt-qt5 rapidjson ruby tbb tinyxml tinyxml2 urdfdom zeromq
```

Take a Coke.

```bash
export CMAKE_PREFIX_PATH=${CMAKE_PREFIX_PATH:+$CMAKE_PREFIX_PATH:}`brew --prefix qt@5`
```

```bash
brew unlink qt
```
This last step might not be needed?

Navigate to your workspace folder.

```bash
colcon graph
```

```bash
colcon build --merge-install
```

Take another Coke.

```bash
colcon build --cmake-args -DCMAKE_MACOSX_RPATH=FALSE -DCMAKE_INSTALL_NAME_DIR=$(pwd)/install/lib --merge-install
```

```bash
colcon build --cmake-args -DBUILD_TESTING=OFF --merge-install
```

```bash
colcon build --cmake-args ' -DBUILD_TESTING=OFF' ' -DCMAKE_BUILD_TYPE=Debug' --merge-install
```

Launch Gazebo server in one terminal.
Source the workspace in zsh.

```bash
. ~/workspace/install/setup.zsh
gz sim -v 4 shapes.sdf -s
```

Launche the GUI in another terminal.
Source the workspace in zsh.

```bash
. ~/workspace/install/setup.zsh
gz sim -v 4 -g
```

Have fun.