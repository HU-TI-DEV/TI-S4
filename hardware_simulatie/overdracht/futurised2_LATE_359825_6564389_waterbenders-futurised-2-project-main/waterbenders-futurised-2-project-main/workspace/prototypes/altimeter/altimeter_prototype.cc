#include <iostream>
#include <atomic>
#include <csignal>
#include <thread>
#include <gz/msgs.hh>
#include <gz/transport.hh>

// flag used to break the publisher loop and terminate the program
static std::atomic<bool> g_terminate(false);

double height = 0.0;

// altimeter callback
void OnAltimeter(const gz::msgs::Altimeter &msg) {
  height = msg.vertical_position();
}

// signal handeler: when SIGINT or SIGTERM signals are detected, break the infinite loop that publishes messages and exit the program smoothly
void signal_handler(int signal) {
  if (signal == SIGINT || signal == SIGTERM) 
    g_terminate = true;
}

//////////////////////////////////////////////////
int main (int argc, char **argv) {
  // install a signal handler for SIGINT and SIGTERM.
  std::signal(SIGINT,  signal_handler);
  std::signal(SIGTERM, signal_handler);

  // create a transport node and advertise a topic
  gz::transport::Node node;
  std::string topic = "/model/cube_with_thruster/joint/thruster_joint/cmd_thrust";

  auto pub = node.Advertise<gz::msgs::Double>(topic);
  if (!pub) {
    std::cerr << "Error advertising topic [" << topic << "]" << std::endl;
    return -1;
  }

  // subscribe to a topic by registering a callback
  if (!node.Subscribe("/altimeter", OnAltimeter)) {
    std::cerr << "Error subscribing to topic [" << topic << "]" << std::endl;
    return -1;
  }

  // publish messages at 1Hz
  while (!g_terminate) {
    gz::msgs::Double msg;
    msg.set_data(height);
    pub.Publish(msg);

    std::cout << "Height: " << height << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(1000));
  }

  return 0;
}