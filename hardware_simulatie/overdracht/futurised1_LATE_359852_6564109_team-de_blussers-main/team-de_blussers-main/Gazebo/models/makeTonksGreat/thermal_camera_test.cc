#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>
#include <gz/msgs/image.pb.h>

#include <chrono>
#include <thread>
#include <iostream>
#include <mutex>

// Global state
std::mutex g_mutex;

float g_temp = 0.0f;
int g_x = -1;
int g_y = -1;
bool g_is_fire = false;

// Thermal sensor callback
void thermalCallback(const gz::msgs::Image &msg)
{
    // Thermal sensor range
    const float temp_min = 253.15f; // K
    const float temp_max = 673.15f; // K

    const uint8_t fire_threshold = 180;

    int width = msg.width();
    const std::string &raw = msg.data();
    const unsigned char* data =
        reinterpret_cast<const unsigned char*>(raw.data());

    float sum_x = 0;
    float sum_y = 0;
    float sum_temp = 0;
    int count = 0;

    for (size_t i = 0; i < raw.size(); ++i)
    {
        uint8_t val = data[i];

        // Convert L8 -> Kelvin -> Celsius
        float temp_k = temp_min + (val / 255.0f) * (temp_max - temp_min);
        float temp_c = temp_k - 273.15f;

        // Vuur detectie op basis van intensiteit
        if (val > fire_threshold)
        {
            int x = i % width;
            int y = i / width;

            sum_x += x;
            sum_y += y;
            sum_temp += temp_c;
            count++;
        }
    }

    std::lock_guard<std::mutex> lock(g_mutex);

    if (count == 0)
    {
        g_is_fire = false;
        g_x = -1;
        g_y = -1;
        g_temp = 0.0f;
        return;
    }

    g_x = static_cast<int>(sum_x / count);
    g_y = static_cast<int>(sum_y / count);

    // Gemiddelde temperatuur van hete regio
    g_temp = sum_temp / count;

    g_is_fire = true;
}

int main()
{
    gz::transport::Node node;

    node.Subscribe("/thermal_camera_8bit/image", thermalCallback);

    while (true)
    {
        int x;
        int y;
        float temp;
        bool fire;

        {
            std::lock_guard<std::mutex> lock(g_mutex);
            x = g_x;
            y = g_y;
            temp = g_temp;
            fire = g_is_fire;
        }

        if (fire)
        {
            std::cout << "Vuur gedetecteerd\n";
            std::cout << "Temp: " << temp << " °C\n";
            std::cout << "Position: x=" << x << " y=" << y << "\n";
        }
        else
        {
            std::cout << "Geen vuur gedetecteerd\n";
        };

        std::this_thread::sleep_for(std::chrono::milliseconds(2000));
        
    }
    return 0;
}