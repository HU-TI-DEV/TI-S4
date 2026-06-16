//==============================================================================
// main.cpp
//==============================================================================

#include "armControl.hpp"
#include "rotationControl.hpp"

#include <gz/msgs/boolean.pb.h>
#include <gz/transport/Node.hh>

#include <atomic>
#include <chrono>
#include <cmath>
#include <csignal>
#include <future>
#include <iostream>
#include <thread>
#include <vector>

// ─── Positions ────────────────────────────────────────────────────────────────

struct Position
{
    float  x;
    float  y;
    double height;
    int    pause_ms;
};

const std::vector<Position> POSITIONS = {
    { 1.5f,   1.0f,  1.0,  2000 },
    { 1.01f, -1.48f, 1.64, 2000 },
    { 0.01f,  0.6f,  0.5,  2000 },
    { -0.99f,-1.37f, 2.11, 2000 },
};

constexpr double PIVOT_ARM1_HEIGHT = 0.738;

// ─── Signal / pause handling ──────────────────────────────────────────────────

static std::atomic<bool> g_running{true};
static std::atomic<bool> g_paused{false};

void onSignal(int) { g_running.store(false); }

// Callback voor /arm/pause (gz.msgs.Boolean)
// true  → arm pauzeert en houdt huidige positie vast
// false → arm hervat de cyclus
void pauseCallback(const gz::msgs::Boolean& msg)
{
    const bool pause = msg.data();
    g_paused.store(pause);
    std::cout << "[pause] " << (pause ? "PAUSED" : "RESUMED") << "\n";
}

// Hulpfunctie: blokkeer zolang g_paused actief is (of g_running wegvalt)
static void waitWhilePaused()
{
    while (g_paused.load() && g_running.load())
        std::this_thread::sleep_for(std::chrono::milliseconds(50));
}

// ─── Joint configs ────────────────────────────────────────────────────────────

static MotorJointConfig basePivotConfig()
{
    MotorJointConfig c;
    c.kp             = 18000.0;
    c.ki             =   500.0;
    c.kd             =  3000.0;
    c.integral_limit = 10000.0;
    c.max_force      =  8000.0;
    c.settled_thresh =     0.01;
    c.settled_time   =     0.2;
    c.loop_hz        =  2000.0;
    return c;
}

static MotorJointConfig pivotArm1Config()
{
    MotorJointConfig c;
    c.kp             =  3000.0;
    c.ki             =  1000.0;
    c.kd             =  1500.0;
    c.integral_limit =  5000.0;
    c.max_force      =  3000.0;
    c.settled_thresh =     0.01;
    c.settled_time   =     0.2;
    c.loop_hz        =  2000.0;
    return c;
}

static MotorJointConfig arm1Arm2Config()
{
    MotorJointConfig c;
    c.kp             =  1000.0;
    c.ki             =   500.0;
    c.kd             =   500.0;
    c.integral_limit =  5000.0;
    c.max_force      =  3000.0;
    c.settled_thresh =     0.01;
    c.settled_time   =     0.2;
    c.loop_hz        =  2000.0;
    return c;
}

// ─── Move to position ─────────────────────────────────────────────────────────

static bool moveTo(ArmControl& arm, RotationControl& rotation, const Position& pos)
{
    // Wacht als de arm gepauzeerd is vóór de beweging begint
    waitWhilePaused();
    if (!g_running.load()) return false;

    const double reach           = std::sqrt(pos.x * pos.x + pos.y * pos.y);
    const double adjusted_height = pos.height - PIVOT_ARM1_HEIGHT;

    auto f_base = rotation.move_to(pos.x, pos.y);

    std::array<std::future<void>, 2> f_ik;
    try
    {
        f_ik = arm.inverseKinematics(reach, adjusted_height);
    }
    catch (const std::exception& e)
    {
        std::cerr << "[main] IK error: " << e.what() << "\n";
        return false;
    }

    f_base.wait();
    if (f_ik[0].wait_for(std::chrono::seconds(5)) == std::future_status::timeout)
        std::cout << "  [warn] pivot_arm1 timed out\n";
    if (f_ik[1].wait_for(std::chrono::seconds(5)) == std::future_status::timeout)
        std::cout << "  [warn] arm1_arm2 timed out\n";

    return true;
}

// ─── Main ─────────────────────────────────────────────────────────────────────

int main()
{
    std::signal(SIGINT,  onSignal);
    std::signal(SIGTERM, onSignal);

    gz::transport::Node node;

    // Subscriben op het pause-topic
    if (!node.Subscribe("/arm/pause", pauseCallback))
    {
        std::cerr << "[main] Failed to subscribe to /arm/pause\n";
        return 1;
    }
    std::cout << "[main] Subscribed to /arm/pause (Boolean: true=pause, false=resume)\n";

    ArmControl      arm(node, pivotArm1Config(), arm1Arm2Config());
    RotationControl rotation(node, basePivotConfig());

    std::cout << "[main] Waiting for joint states...\n";
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
    if (!g_running.load()) return 0;

    std::cout << "[main] Starting cycle. Press Ctrl-C to stop.\n";

    int cycle = 0;
    while (g_running.load())
    {
        std::cout << "[main] Cycle " << ++cycle << "\n";

        for (std::size_t i = 0; i < POSITIONS.size() && g_running.load(); ++i)
        {
            const Position& pos = POSITIONS[i];
            std::cout << "  -> position " << i
                      << " (" << pos.x << ", " << pos.y
                      << ", h=" << pos.height << ")"
                      << " hold=" << pos.pause_ms << "ms\n";

            if (!moveTo(arm, rotation, pos))
                continue;

            // Hold position — verleng automatisch zolang gepauzeerd
            const auto pause_end = std::chrono::steady_clock::now()
                                 + std::chrono::milliseconds(pos.pause_ms);
            while (g_running.load() && std::chrono::steady_clock::now() < pause_end)
                std::this_thread::sleep_for(std::chrono::milliseconds(50));

            // Extra wacht als pauze nog actief is na de hold-tijd
            waitWhilePaused();
        }
    }

    std::cout << "[main] Shutting down.\n";
    return 0;
}



// # Pauzeren
// gz topic -t /arm/pause -m gz.msgs.Boolean -p "data: true"

// # Hervatten
// gz topic -t /arm/pause -m gz.msgs.Boolean -p "data: false"