#include <gz/transport/Node.hh>
#include <gz/msgs/twist.pb.h>
#include <gz/msgs/pose_v.pb.h>

#include <cmath>
#include <iostream>
#include <thread>
#include <vector>

class GoToPointController{
public:
    GoToPointController(int gx, int gy) : goal_x(gx), goal_y(gy){
        node.Subscribe("/model/vehicle/pose", &GoToPointController::PoseCallback, this);
        pub = node.Advertise<gz::msgs::Twist>("/cmd_vel");
    }

    void loadPath(const std::vector<std::pair<int, int>>& new_path){
        waypoints = new_path;
        current_waypoint = 0;
        reached = false;
        integral = 0.0;
        prev_error = 0.0;
        current_speed = 0.0;
        if (!waypoints.empty()){
            goal_x = waypoints[0].first;
            goal_y = waypoints[0].second;
        }
    }

    bool reached = false; // Placeholder for detection if goal is reached
private:
    gz::transport::Node node;
    gz::transport::Node::Publisher pub;
    std::vector<std::pair<int, int>> waypoints;

    int goal_x, goal_y;
    int current_waypoint = 0;

    double prev_error = 0.0; 
    double integral = 0.0;
    double current_speed = 0.0;

    void advanceWaypoint(){
        current_waypoint++;
        if (current_waypoint >= (int)waypoints.size()){
            reached = true;
            std::cout << "[DRIVER] Reached final goal!" << std::endl;
            return;
        }
        goal_x = waypoints[current_waypoint].first;
        goal_y = waypoints[current_waypoint].second;
        integral  = 0.0;
        prev_error = 0.0;
    }

    float toleranceForWaypoint(int index){
        const float straight_tolerance = 0.4;
        const float corner_tolerance   = 0.15;

        bool is_last = (index >= (int)waypoints.size() - 1);
        if (is_last) return corner_tolerance; // Use corner tolerance since we want to be close to goal
        if (index == 0) return straight_tolerance;

        // Direction of last point. This will be -1 when straight line
        float in_dx = (float)waypoints[index].first  - (float)waypoints[index-1].first;
        float in_dy = (float)waypoints[index].second - (float)waypoints[index-1].second;
        // Direction of next point. This will be -1 when straight line
        float out_dx = (float)waypoints[index+1].first  - (float)waypoints[index].first;
        float out_dy = (float)waypoints[index+1].second - (float)waypoints[index].second;

        // Use pythagoras to determine the length of the next driving line
        float in_len  = std::sqrt(in_dx*in_dx   + in_dy*in_dy);
        float out_len = std::sqrt(out_dx*out_dx + out_dy*out_dy);
        // Check if either is 0
        if (in_len < 1e-6 || out_len < 1e-6) {return corner_tolerance;}
        // Use prior calculated length to normalise the vector and calculate the dot product
        float dot = (in_dx/in_len) * (out_dx/out_len) + (in_dy/in_len) * (out_dy/out_len);
        // We use 8 directional movement so anythin under 1 is a corner
        return (dot >= 0.99) ? straight_tolerance : corner_tolerance;
    }

    // Limits the speed change to 0.5 m/s² when accelerating,
    // and 1.5 m/s² when decelerating.
    double SpeedLimiter(double target_speed, double dt)
    {
        const double max_acceleration = 0.5; // m/s²
        const double max_deceleration = 1.5; // m/s²

        double delta = target_speed - current_speed;

        if (delta > 0.0)
            delta = std::min(delta, max_acceleration * dt);
        else
            delta = std::max(delta, -max_deceleration * dt);

        return current_speed + delta;
    }

    void PoseCallback(const gz::msgs::Pose &msg){
        // Using the pose function in the sdf to find the x and y coordinate of the AMP
        double x = msg.position().x();
        double y = msg.position().y();
        // double z = msg.position().z(); // Unused for now, but left in here to keep it available for use.
        // The orientation of the AMP is of importance to now how the AMP needs to change direction
        auto q = msg.orientation();

        // quaternion → yaw
        double siny_cosp = 2 * (q.w()*q.z() + q.x()*q.y());
        double cosy_cosp = 1 - 2 * (q.y()*q.y() + q.z()*q.z());
        double yaw = std::atan2(siny_cosp, cosy_cosp);

        Update(x, y, yaw);
        return;
    }  

    void Update(double x, double y, double yaw)
    {
        if(reached){return;} // No update when already reached goal
        double max_speed = 2.0;
        
        double dx = goal_x - x;
        double dy = goal_y - y;
        double dt = 0.1; // Placeholder for time step, ideally should be calculated based on actual time between updates

        // --- PID state (must be class members ideally!) ---
        double target_yaw = std::atan2(dy, dx);
        double yaw_error = target_yaw - yaw;

        // normalize angle
        while (yaw_error > M_PI) yaw_error -= 2*M_PI;
        while (yaw_error < -M_PI) yaw_error += 2*M_PI;

        double distance = std::sqrt(dx*dx + dy*dy);

        gz::msgs::Twist cmd;

        // --- Angular control (keep as P for now) ---
        double K_ang = 2.0;

        // --- Linear PID gains ---
        double Kp = 1;
        double Ki = 0.1;
        double Kd = 0.4;

        float tolerance = toleranceForWaypoint(current_waypoint);

        if (distance > tolerance){
            cmd.mutable_angular()->set_z(K_ang * yaw_error);

            if (std::abs(yaw_error) < 0.05){
                // Linear PID calculations only when facing roughly the right direction
                double derivative = (distance - prev_error) / dt;
                prev_error = distance;
                integral += distance * dt;
                double linear_output = Kp * distance + Ki * integral + Kd * derivative;

                if (linear_output > max_speed) linear_output = max_speed;

                current_speed = SpeedLimiter(linear_output, dt);
                cmd.mutable_linear()->set_x(current_speed);
            }
            else{
                current_speed = SpeedLimiter(0.0, dt);
                cmd.mutable_linear()->set_x(current_speed);
            }
            pub.Publish(cmd);
        }
        else{
            std::cout << "[DRIVER] Passed waypoint " << current_waypoint + 1 << " / " << waypoints.size() << std::endl;
            advanceWaypoint();
            // If final waypoint, send a stop command.
            if (reached){
                current_speed = 0.0;
                cmd.mutable_linear()->set_x(0.0);
                cmd.mutable_angular()->set_z(0.0);
                pub.Publish(cmd);
            }
            // No publish when no last command to keep momentum
        }
    }
};