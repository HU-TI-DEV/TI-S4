#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>

#include <chrono>
#include <thread>
#include <iostream>
#include <termios.h>
#include <atomic>
#include <unistd.h>
#include <mutex>
#include <cmath>
#include <sys/select.h>

std::chrono::steady_clock::time_point last_input_time;
const double timeout = 0.7;

std::mutex time_mutex;

std::atomic<bool> w(false);
std::atomic<bool> a(false);
std::atomic<bool> s(false);
std::atomic<bool> d(false);

void setRawMode(bool enable) {
    static struct termios oldt;

    if (enable) {
        struct termios newt;
        tcgetattr(STDIN_FILENO, &oldt);
        newt = oldt;
        newt.c_lflag &= ~(ICANON | ECHO);
        tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    } else {
        tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    }
}

void inputLoop() {
    setRawMode(true);

    while (true) {
        fd_set fds;
        FD_ZERO(&fds);
        FD_SET(STDIN_FILENO, &fds);
        struct timeval tv = {0, 10000}; // 10ms

        if (select(STDIN_FILENO + 1, &fds, nullptr, nullptr, &tv) > 0) {
            char c;
            if (read(STDIN_FILENO, &c, 1) == 1) {
                std::lock_guard<std::mutex> lock(time_mutex);
                last_input_time = std::chrono::steady_clock::now();
                if (c == 'w') w = true;
                if (c == 'a') a = true;
                if (c == 's') s = true;
                if (c == 'd') d = true;
            }
        }
    }

    setRawMode(false);
}

int main()
{
    gz::transport::Node node;
    auto pub = node.Advertise<gz::msgs::Twist>("/cmd_vel");

    last_input_time = std::chrono::steady_clock::now();

    std::thread(inputLoop).detach();

    std::cout << "WASD control started\n";

    double cur_linear  = 0.0;
    double cur_angular = 0.0;
    const double alpha = 0.2;

    while (true)
    {
        auto now = std::chrono::steady_clock::now();

        std::chrono::steady_clock::time_point last_time_copy;
        {
            std::lock_guard<std::mutex> lock(time_mutex);
            last_time_copy = last_input_time;
        }
        double dt = std::chrono::duration<double>(now - last_time_copy).count();

        if (dt > timeout) {
            w = false;
            a = false;
            s = false;
            d = false;
        }

        gz::msgs::Twist msg;

        double tgt_linear  = w ? 2.0 : (s ? -2.0 : 0.0);
        double tgt_angular = a ? 2.0 : (d ? -2.0 : 0.0);

        cur_linear  += alpha * (tgt_linear  - cur_linear);
        cur_angular += alpha * (tgt_angular - cur_angular);

        if (std::abs(cur_linear)  < 0.05) cur_linear  = 0.0;
        if (std::abs(cur_angular) < 0.05) cur_angular = 0.0;

        msg.mutable_linear()->set_x(cur_linear);
        msg.mutable_angular()->set_z(cur_angular);

        pub.Publish(msg);
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
    }
    return 0;
}
