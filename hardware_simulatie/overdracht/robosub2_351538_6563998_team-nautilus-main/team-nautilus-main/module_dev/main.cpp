#include "RobotArm.hpp"
#include "KinematicsSolver.h"

#include <csignal>
#include <iostream>

static RobotArm* g_arm = nullptr;

static void signalHandler(int sig) {
    if ((sig == SIGINT || sig == SIGTERM) && g_arm)
        g_arm->stop();
}

int main() {
    RobotArm arm;
    g_arm = &arm;

    std::signal(SIGINT,  signalHandler);
    std::signal(SIGTERM, signalHandler);

    arm.start();
    arm.runMenu();

    std::cout << "Shutting down...\n";
    return 0;
}