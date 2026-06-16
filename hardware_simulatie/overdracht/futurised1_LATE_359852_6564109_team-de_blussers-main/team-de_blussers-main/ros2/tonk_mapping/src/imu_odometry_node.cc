#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/imu.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <tf2_ros/transform_broadcaster.h>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Matrix3x3.h>
#include <cmath>

class IMUOdometryNode : public rclcpp::Node
{
public:
    IMUOdometryNode() : Node("imu_odometry_node")
    {
        // Subscribe to IMU data from Gazebo
        imu_sub_ = create_subscription<sensor_msgs::msg::Imu>(
            "/imu", 10,
            std::bind(&IMUOdometryNode::imuCallback, this, std::placeholders::_1));

        // Subscribe to Odometry data from Gazebo DiffDrive plugin
        odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
            "/odom", 10,
            std::bind(&IMUOdometryNode::odometryCallback, this, std::placeholders::_1));

        // Publisher for filtered/fused odometry
        odom_pub_ = create_publisher<nav_msgs::msg::Odometry>("/odom/filtered", 10);

        // Publisher for IMU data with additional processing
        imu_pub_ = create_publisher<sensor_msgs::msg::Imu>("/imu/processed", 10);

        // Transform broadcaster for odometry
        tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(this);

        // Timer for periodic updates
        timer_ = create_wall_timer(
            std::chrono::milliseconds(50),
            std::bind(&IMUOdometryNode::timerCallback, this));

        RCLCPP_INFO(get_logger(), "IMU & Odometry node started");
        RCLCPP_INFO(get_logger(), "  - Subscribing to: /imu, /odom");
        RCLCPP_INFO(get_logger(), "  - Publishing: /odom/filtered, /imu/processed");
    }

private:
    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg)
    {
        last_imu_ = msg;

        // Log IMU data
        RCLCPP_DEBUG(get_logger(), 
            "IMU - Accel: [%.3f, %.3f, %.3f] m/s², Angular Vel: [%.3f, %.3f, %.3f] rad/s",
            msg->linear_acceleration.x, msg->linear_acceleration.y, msg->linear_acceleration.z,
            msg->angular_velocity.x, msg->angular_velocity.y, msg->angular_velocity.z);

        // Calculate roll, pitch, yaw from orientation
        tf2::Quaternion q(
            msg->orientation.x,
            msg->orientation.y,
            msg->orientation.z,
            msg->orientation.w);
        
        tf2::Matrix3x3 m(q);
        double roll, pitch, yaw;
        m.getRPY(roll, pitch, yaw);

        RCLCPP_DEBUG(get_logger(), 
            "IMU Orientation - Roll: %.3f°, Pitch: %.3f°, Yaw: %.3f°",
            roll * 180.0 / M_PI, pitch * 180.0 / M_PI, yaw * 180.0 / M_PI);

        // Publish processed IMU data
        auto processed_imu = std::make_shared<sensor_msgs::msg::Imu>(*msg);
        imu_pub_->publish(*processed_imu);
    }

    void odometryCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        last_odom_ = msg;

        // Log Odometry data
        RCLCPP_DEBUG(get_logger(), 
            "Odometry - Pose: [%.3f, %.3f] m, Vel: [%.3f, %.3f, %.3f] m/s",
            msg->pose.pose.position.x,
            msg->pose.pose.position.y,
            msg->twist.twist.linear.x,
            msg->twist.twist.linear.y,
            msg->twist.twist.linear.z);

        // Create filtered odometry message
        auto filtered_odom = std::make_shared<nav_msgs::msg::Odometry>();
        filtered_odom->header = msg->header;
        filtered_odom->header.frame_id = "odom";
        filtered_odom->child_frame_id = "base_link";
        
        // Copy pose and twist (in real implementation, could apply Kalman filter here)
        filtered_odom->pose = msg->pose;
        filtered_odom->twist = msg->twist;

        // Add covariance (6x6 matrix for pose, 6x6 for twist)
        // Diagonal values represent uncertainty
        for (int i = 0; i < 36; ++i) {
            if (i % 7 == 0) {  // Diagonal
                filtered_odom->pose.covariance[i] = 0.01;  // Position uncertainty
                filtered_odom->twist.covariance[i] = 0.05; // Velocity uncertainty
            } else {
                filtered_odom->pose.covariance[i] = 0.0;
                filtered_odom->twist.covariance[i] = 0.0;
            }
        }

        odom_pub_->publish(*filtered_odom);

        // Publish TF transform from odom to base_link
        publishOdometryTF(filtered_odom);
    }

    void publishOdometryTF(const nav_msgs::msg::Odometry::SharedPtr odom)
    {
        geometry_msgs::msg::TransformStamped tf;
        tf.header = odom->header;
        tf.header.frame_id = "odom";
        tf.child_frame_id = "base_link";
        
        tf.transform.translation.x = odom->pose.pose.position.x;
        tf.transform.translation.y = odom->pose.pose.position.y;
        tf.transform.translation.z = odom->pose.pose.position.z;
        
        tf.transform.rotation = odom->pose.pose.orientation;

        tf_broadcaster_->sendTransform(tf);
    }

    void timerCallback()
    {
        // Periodic status update (reduce spam with counter)
        if (++timer_count_ % 20 == 0) {
            RCLCPP_DEBUG(get_logger(), "IMU & Odometry node is running...");
        }
    }

    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
    rclcpp::Publisher<sensor_msgs::msg::Imu>::SharedPtr imu_pub_;
    rclcpp::TimerBase::SharedPtr timer_;
    std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;

    sensor_msgs::msg::Imu::SharedPtr last_imu_;
    nav_msgs::msg::Odometry::SharedPtr last_odom_;
    int timer_count_ = 0;
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<IMUOdometryNode>());
    rclcpp::shutdown();
    return 0;
}
