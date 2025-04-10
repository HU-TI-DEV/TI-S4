### Connect with C on Mac OS

First check your tooling:

```bash
g++ --version
```

It seems that I have already installed what I need. I have Apple clang version 16.0.0.

Download the files publisher.cc, subscriber.cc and CMakeLists.txt from https://github.com/gazebosim/gz-transport/blob/gz-transport14/tutorials/04_messages.md

In the gz_transport_tutorial I will make a new folder build

```bash
mkdir build
cd build
```

Now let us run cmake and then compile the files:

```bash
cmake ..
```

Error. It seems like I am missing a package gz-transport14

Source: https://gazebosim.org/api/transport/13/installation.html

```bash
brew tap osrf/simulation
brew install gz-transport14
```

Let us try again.

```bash
cmake ..
make publisher subscriber
```

Now we have more success. For running examples we need a valid GZ_PARTITION environment variable in all our terminals.

```bash
# Linux and Mac
export GZ_PARTITION=test
```

Run the publisher:

```bash
./publisher
```

Open another terminal and navigate to this build folder. Set the GZ_PARTITION variable

```bash
export GZ_PARTITION=test
```

Run the subscriber:

```bash
./subscriber
```

I am receiving the HELLO messages.

## Now we will connect with the robot

We will open the terminals for the robot, GUI and a terminal for viewing the topics.

```bash
. ~/workspace/install/setup.zsh
export GZ_PARTITION=test
gz sim -v 4 robot.sdf -s
```

In another terminal. Move your robot and start the GUI.

```bash
. ~/workspace/install/setup.zsh
export GZ_PARTITION=test
gz topic -t "/cmd_vel" -m gz.msgs.Twist -p "linear: {x: 0.5}, angular: {z: 0.05}"
gz sim -v 4 -g
```

View the topics.

```bash
. ~/workspace/install/setup.zsh
export GZ_PARTITION=test
gz topic -e -t /imu
```

Now change the subscriber.cc

Add the following function to your subscriber.cc:

```c++
void OnIMUMessage(const gz::msgs::IMU &msg)
{
    // Output the data to the console
    std::cout << "Angular Velocity: " << msg.angular_velocity().z() << std::endl;
}
```

Change the following lines:

```c++
int main(int argc, char **argv)
{
  gz::transport::Node node;
  std::string topic = "/foo";

  // Subscribe to a topic by registering a callback.
  if (!node.Subscribe(topic, cb))
  {
    std::cerr << "Error subscribing to topic [" << topic << "]" << std::endl;
    return -1;
  }

  // Zzzzzz.
  gz::transport::waitForShutdown();

  return 0;
}
```

to:

```c++
int main(int argc, char **argv)
{
  gz::transport::Node node;
  std::string topic = "/imu";

  // Subscribe to a topic by registering a callback.
  if (!node.Subscribe(topic, OnIMUMessage))
  {
    std::cerr << "Error subscribing to topic [" << topic << "]" << std::endl;
    return -1;
  }

  // Zzzzzz.
  gz::transport::waitForShutdown();

  return 0;
}
```

Navigate with an new terminal to your build folder then recompile.

```bash
. ~/workspace/install/setup.zsh
export GZ_PARTITION=test
cmake ..
make subscriber
```

Run the subscriber:

```bash
./subscriber
```

There is your IMU data.