// map_accumulator.cc
// Bouwt een PERSISTENTE 2D occupancy-grid op uit de LiDAR.
//
// In tegenstelling tot de oude aanpak (planner bouwde elke scan een nieuwe grid
// en wiste hem meteen weer) accumuleert dit node de kaart over de tijd:
//   - elke binnenkomende puntenwolk wordt via TF naar het globale frame gezet
//     (dat frame komt van de SLAM-odometrie, bv. KISS-ICP: odom -> base_link -> lidar)
//   - de punten worden geprojecteerd op een 2D-grid en als obstakel (100) gemarkeerd
//   - de kaart blijft staan, ook als de robot verder rijdt
//
// De grid wordt RUW gepubliceerd (0 = vrij, 100 = obstakel). De inflatie van
// obstakels gebeurt in de planner, zodat mapping en planning gescheiden blijven.
//
// Topics:
//   in : /lidar/pointcloud (sensor_msgs/PointCloud2, frame "lidar")
//   out: /map              (nav_msgs/OccupancyGrid, frame = global_frame)

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/point_cloud2_iterator.hpp>
#include <nav_msgs/msg/occupancy_grid.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <tf2_ros/buffer.h>
#include <tf2_ros/transform_listener.h>
#include <tf2/LinearMath/Transform.h>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Vector3.h>

#include <chrono>
#include <cmath>
#include <memory>
#include <vector>

class MapAccumulator : public rclcpp::Node
{
public:
    MapAccumulator() : Node("map_accumulator")
    {
        // Frame waarin de kaart wordt opgebouwd (de globale SLAM-frame).
        global_frame_ = declare_parameter<std::string>("global_frame", "odom");
        // Grid-afmetingen — standaard gelijk aan die van de planner (90x60m @ 0.2m).
        resolution_   = declare_parameter<double>("resolution", 0.2);
        width_        = declare_parameter<int>("width", 450);
        height_       = declare_parameter<int>("height", 300);
        origin_x_     = declare_parameter<double>("origin_x", -45.0);
        origin_y_     = declare_parameter<double>("origin_y", -30.0);
        // Hoogte-filter in het globale frame: vloer en plafond weggooien.
        z_min_        = declare_parameter<double>("z_min", 0.1);
        z_max_        = declare_parameter<double>("z_max", 2.5);

        grid_.assign(static_cast<size_t>(width_) * height_, 0);  // 0 = vrij/onbekend

        tf_buffer_   = std::make_unique<tf2_ros::Buffer>(get_clock());
        tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

        cloud_sub_ = create_subscription<sensor_msgs::msg::PointCloud2>(
            "/lidar/pointcloud", 5,
            [this](sensor_msgs::msg::PointCloud2::SharedPtr m){ cloudCallback(m); });

        map_pub_ = create_publisher<nav_msgs::msg::OccupancyGrid>("/map", 1);

        pub_timer_ = create_wall_timer(
            std::chrono::milliseconds(500),
            [this](){ publishMap(); });

        RCLCPP_INFO(get_logger(),
            "MapAccumulator gestart — frame '%s', %dx%d cellen @ %.2f m",
            global_frame_.c_str(), width_, height_, resolution_);
    }

private:
    void cloudCallback(const sensor_msgs::msg::PointCloud2::SharedPtr msg)
    {
        // Transform global_frame <- cloud-frame ophalen (via odom->base_link->lidar).
        geometry_msgs::msg::TransformStamped tf;
        try {
            tf = tf_buffer_->lookupTransform(
                global_frame_, msg->header.frame_id, msg->header.stamp,
                rclcpp::Duration::from_seconds(0.1));
        } catch (const std::exception &) {
            // Val terug op de laatst bekende transform (bv. als de SLAM-TF iets achterloopt).
            try {
                tf = tf_buffer_->lookupTransform(
                    global_frame_, msg->header.frame_id, tf2::TimePointZero);
            } catch (const std::exception & e2) {
                RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 2000,
                    "Geen TF %s <- %s: %s",
                    global_frame_.c_str(), msg->header.frame_id.c_str(), e2.what());
                return;
            }
        }

        const tf2::Transform T(
            tf2::Quaternion(tf.transform.rotation.x, tf.transform.rotation.y,
                            tf.transform.rotation.z, tf.transform.rotation.w),
            tf2::Vector3(tf.transform.translation.x, tf.transform.translation.y,
                         tf.transform.translation.z));

        sensor_msgs::PointCloud2ConstIterator<float> it_x(*msg, "x");
        sensor_msgs::PointCloud2ConstIterator<float> it_y(*msg, "y");
        sensor_msgs::PointCloud2ConstIterator<float> it_z(*msg, "z");

        for (; it_x != it_x.end(); ++it_x, ++it_y, ++it_z) {
            if (!std::isfinite(*it_x) || !std::isfinite(*it_y) || !std::isfinite(*it_z))
                continue;

            const tf2::Vector3 p = T * tf2::Vector3(*it_x, *it_y, *it_z);
            if (p.z() < z_min_ || p.z() > z_max_) continue;

            const int col = static_cast<int>((p.x() - origin_x_) / resolution_);
            const int row = static_cast<int>((p.y() - origin_y_) / resolution_);
            if (col >= 0 && col < width_ && row >= 0 && row < height_)
                grid_[static_cast<size_t>(row) * width_ + col] = 100;
        }
    }

    void publishMap()
    {
        nav_msgs::msg::OccupancyGrid m;
        m.header.stamp            = now();
        m.header.frame_id         = global_frame_;
        m.info.resolution         = resolution_;
        m.info.width              = width_;
        m.info.height             = height_;
        m.info.origin.position.x  = origin_x_;
        m.info.origin.position.y  = origin_y_;
        m.info.origin.orientation.w = 1.0;
        m.data.assign(grid_.begin(), grid_.end());
        map_pub_->publish(m);
    }

    rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr cloud_sub_;
    rclcpp::Publisher<nav_msgs::msg::OccupancyGrid>::SharedPtr     map_pub_;
    rclcpp::TimerBase::SharedPtr                                   pub_timer_;
    std::unique_ptr<tf2_ros::Buffer>                              tf_buffer_;
    std::shared_ptr<tf2_ros::TransformListener>                   tf_listener_;

    std::string global_frame_;
    double resolution_, origin_x_, origin_y_, z_min_, z_max_;
    int    width_, height_;
    std::vector<int8_t> grid_;
};

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<MapAccumulator>());
    rclcpp::shutdown();
    return 0;
}
