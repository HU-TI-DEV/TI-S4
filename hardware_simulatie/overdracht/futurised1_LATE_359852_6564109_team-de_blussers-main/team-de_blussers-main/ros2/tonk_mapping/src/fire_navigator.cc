// fire_navigator.cc
// Detecteert vuur via de thermische camera en stuurt de robot via Dijkstra
// naar een punt 2 meter vóór het vuur.
//
// Methode (3 stappen per cameraframe):
//
//   1. Thermische camera (320x240, L8) → gewogen zwaartepunt van hete pixels
//                                      → hoek naar vuur in cameraframe
//
//        pixel_x=0                   pixel_x=319
//        (links)    [==camera==]     (rechts)
//                         ^
//                  pixel_x=160 = recht vooruit
//
//        bearing_offset = (160 - cx) / 320 * CAM_HFOV
//
//   2. LiDAR punten (robot-relatief) → zoek dichtstbijzijnd punt in de richting
//                                      bearing_offset ± 8.6° tolerantie
//                                    → dit is de afstand tot het brandende object
//
//   3. Vuurpositie in world frame:
//        fire_x = robot_x + dist * cos(robot_yaw + bearing_offset)
//        fire_y = robot_y + dist * sin(robot_yaw + bearing_offset)
//
//      Doel (2m vóór vuur, richting robot→vuur):
//        goal = fire_pos - 2.0 * eenheidsvector(robot → vuur)
//
//      Publiceer op /goal_pose → dijkstra_path_planner rijdt ernaartoe.

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/point_cloud2_iterator.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <visualization_msgs/msg/marker.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Matrix3x3.h>

#include <cmath>
#include <mutex>
#include <limits>

// ── Cameraconfiguratie (uit tonk.sdf thermal sensor) ────────────────────────
static constexpr int    CAM_W         = 320;    // pixels breed
static constexpr int    CAM_H         = 240;    // pixels hoog
static constexpr double CAM_HFOV      = 1.047;  // horizontaal FOV in radians (~60°)

// ── Vuurdrempel (overgenomen uit thermal_camera_test.cc) ─────────────────────
// L8 pixelwaarde > 180 → temperatuur > ~450°C → vuur
static constexpr uint8_t FIRE_THRESHOLD = 180;

// ── Navigatieparameters ──────────────────────────────────────────────────────
static constexpr double STOP_DISTANCE       = 3.0;  // meter vóór het vuur stoppen (blus-afstand)
static constexpr double GOAL_UPDATE_DIST    = 0.5;  // meter: minimale verplaatsing doel voor herplanning
static constexpr double AT_FIRE_MARGIN      = 0.5;  // meter extra: niet opnieuw rijden als al op positie

// ── LiDAR zoekparameters ─────────────────────────────────────────────────────
// STRATEGIE: we zoeken het VERSTE punt in de kegel, niet het dichtstbijzijnde.
// Het vuur staat achteraan in de garage; tussenliggende obstakels (pillaren, auto's)
// geven kortere terugkeer en werden eerder verkeerdelijk als vuurafstand gekozen.
static constexpr double LIDAR_BEARING_TOL   = 0.05; // radians (~2.9°) – smalle kegel, minder ruis
static constexpr double LIDAR_MIN_DIST      = 1.0;  // meter: negeer punten te dicht bij robot
static constexpr double LIDAR_MAX_DIST      = 30.0; // meter: sanity-cap (oost-/noordmuur ~31-34m)
static constexpr double LIDAR_DEFAULT_DIST  = 20.0; // meter: fallback als LiDAR niets ziet

class FireNavigator : public rclcpp::Node
{
public:
    FireNavigator() : Node("fire_navigator")
    {
        // ── Subscribers ──────────────────────────────────────────────────────
        cam_sub_ = create_subscription<sensor_msgs::msg::Image>(
            "/thermal_camera_8bit/image", 10,
            [this](sensor_msgs::msg::Image::SharedPtr m){ cameraCallback(m); });

        lidar_sub_ = create_subscription<sensor_msgs::msg::PointCloud2>(
            "/lidar/pointcloud", 5,
            [this](sensor_msgs::msg::PointCloud2::SharedPtr m){ lidarCallback(m); });

        odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
            "/odom", 10,
            [this](nav_msgs::msg::Odometry::SharedPtr m){ odomCallback(m); });

        // ── Publishers ───────────────────────────────────────────────────────
        goal_pub_   = create_publisher<geometry_msgs::msg::PoseStamped>("/goal_pose", 5);
        marker_pub_ = create_publisher<visualization_msgs::msg::Marker>("/fire_marker", 5);

        RCLCPP_INFO(get_logger(), "Fire navigator gestart");
        RCLCPP_INFO(get_logger(), "  Camera: %dx%d, FOV=%.2f rad", CAM_W, CAM_H, CAM_HFOV);
        RCLCPP_INFO(get_logger(), "  Vuurdrempel: %d/255 (L8)", FIRE_THRESHOLD);
        RCLCPP_INFO(get_logger(), "  Stopafstand: %.1f m voor het vuur", STOP_DISTANCE);
    }

private:
    // ════════════════════════════════════════════════════════════════════════
    //  ODOMETRY – robotpositie bijhouden
    // ════════════════════════════════════════════════════════════════════════
    void odomCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        robot_x_ = msg->pose.pose.position.x;
        robot_y_ = msg->pose.pose.position.y;
        tf2::Quaternion q(
            msg->pose.pose.orientation.x, msg->pose.pose.orientation.y,
            msg->pose.pose.orientation.z, msg->pose.pose.orientation.w);
        double r, p;
        tf2::Matrix3x3(q).getRPY(r, p, robot_yaw_);
        has_odom_ = true;
    }

    // ════════════════════════════════════════════════════════════════════════
    //  LIDAR – nieuwste scan cachen voor afstandsmeting
    // ════════════════════════════════════════════════════════════════════════
    void lidarCallback(const sensor_msgs::msg::PointCloud2::SharedPtr msg)
    {
        std::lock_guard<std::mutex> lock(lidar_mutex_);
        latest_lidar_ = msg;
    }

    // ════════════════════════════════════════════════════════════════════════
    //  CAMERA – vuur detecteren en doel berekenen
    // ════════════════════════════════════════════════════════════════════════
    void cameraCallback(const sensor_msgs::msg::Image::SharedPtr msg)
    {
        if (!has_odom_) return;
        if (msg->data.empty()) return;

        // ── STAP 1: Gewogen zwaartepunt van hete pixels ───────────────────
        // Gewicht = (pixelwaarde - drempel), zodat hetere pixels meer meewegen.
        const uint8_t* data = msg->data.data();
        double sum_x      = 0.0;
        double sum_weight = 0.0;
        int    count      = 0;

        for (int i = 0; i < CAM_W * CAM_H; ++i) {
            uint8_t val = data[i];
            if (val < FIRE_THRESHOLD) continue;

            int px = i % CAM_W;
            double weight = static_cast<double>(val - FIRE_THRESHOLD);
            sum_x      += px * weight;
            sum_weight += weight;
            ++count;
        }

        if (count == 0) {
            if (fire_detected_) {
                RCLCPP_INFO(get_logger(), "Vuur verdwenen uit beeld");
                fire_detected_ = false;
            }
            return;
        }

        double cx = sum_x / sum_weight;  // pixel X van het vuurcentrum (0–319)

        if (!fire_detected_) {
            RCLCPP_INFO(get_logger(),
                "Vuur gedetecteerd! %d pixels boven drempel, centrum X=%.0f", count, cx);
            fire_detected_ = true;
        }

        // ── STAP 2: Hoek naar vuur in robotframe ─────────────────────────
        //   cx = 0   → uiterst links → robot draait links → positieve hoek
        //   cx = 160 → midden       → recht vooruit      → hoek = 0
        //   cx = 319 → uiterst rechts → robot draait rechts → negatieve hoek
        double bearing_offset = (CAM_W / 2.0 - cx) / CAM_W * CAM_HFOV;

        // ── STAP 3: Afstand via LiDAR ─────────────────────────────────────
        double fire_dist = fireDistanceFromLidar(bearing_offset);

        // ── STAP 4: Vuurpositie in world frame ────────────────────────────
        double fire_bearing = robot_yaw_ + bearing_offset;
        double fire_x_raw = robot_x_ + fire_dist * std::cos(fire_bearing);
        double fire_y_raw = robot_y_ + fire_dist * std::sin(fire_bearing);

        // ── STAP 4b: Exponentiële smoothing – dempt ruis en korte LiDAR-misses ──
        if (!smooth_init_) {
            smooth_fire_x_ = fire_x_raw;
            smooth_fire_y_ = fire_y_raw;
            smooth_init_   = true;
        } else {
            smooth_fire_x_ = FIRE_SMOOTH_ALPHA * fire_x_raw + (1.0 - FIRE_SMOOTH_ALPHA) * smooth_fire_x_;
            smooth_fire_y_ = FIRE_SMOOTH_ALPHA * fire_y_raw + (1.0 - FIRE_SMOOTH_ALPHA) * smooth_fire_y_;
        }
        double fire_x = smooth_fire_x_;
        double fire_y = smooth_fire_y_;

        // ── STAP 5: Controleer of we al dicht genoeg zijn ─────────────────
        double dist_to_fire = std::hypot(fire_x - robot_x_, fire_y - robot_y_);
        if (dist_to_fire <= STOP_DISTANCE + AT_FIRE_MARGIN) {
            RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 5000,
                "Al op positie: %.1f m van vuur (doel: %.1f m)", dist_to_fire, STOP_DISTANCE);
            return;
        }

        // ── STAP 6: Doel = 2m vóór het vuur op de lijn robot→vuur ─────────
        //   doel = vuurpositie - STOP_DISTANCE × eenheidsvector(robot→vuur)
        double goal_x = fire_x - STOP_DISTANCE * std::cos(fire_bearing);
        double goal_y = fire_y - STOP_DISTANCE * std::sin(fire_bearing);

        // Geen herplanning als het doel nauwelijks veranderd is
        double delta = std::hypot(goal_x - last_goal_x_, goal_y - last_goal_y_);
        if (delta < GOAL_UPDATE_DIST && fire_goal_sent_) return;

        // ── STAP 7: Publiceer doel naar dijkstra_path_planner ─────────────
        geometry_msgs::msg::PoseStamped goal;
        goal.header.stamp    = now();
        goal.header.frame_id = "odom";
        goal.pose.position.x = goal_x;
        goal.pose.position.y = goal_y;
        goal.pose.position.z = 0.0;

        // Richting van het doel: robot kijkt naar het vuur (fire_bearing)
        tf2::Quaternion q;
        q.setRPY(0.0, 0.0, fire_bearing);
        goal.pose.orientation.x = q.x();
        goal.pose.orientation.y = q.y();
        goal.pose.orientation.z = q.z();
        goal.pose.orientation.w = q.w();

        goal_pub_->publish(goal);
        last_goal_x_   = goal_x;
        last_goal_y_   = goal_y;
        fire_goal_sent_ = true;

        RCLCPP_INFO(get_logger(),
            "Vuur op (%.1f, %.1f) @ %.1f m | doel: (%.1f, %.1f) | hoek: %.1f°",
            fire_x, fire_y, fire_dist, goal_x, goal_y,
            fire_bearing * 180.0 / M_PI);

        publishFireMarker(fire_x, fire_y, msg->header.stamp);
    }

    // ════════════════════════════════════════════════════════════════════════
    //  MARKER – oranje bol + tekst in RViz op de vuurpositie
    // ════════════════════════════════════════════════════════════════════════
    void publishFireMarker(double fire_x, double fire_y, const rclcpp::Time & stamp)
    {
        // Bol op de vuurpositie
        visualization_msgs::msg::Marker sphere;
        sphere.header.stamp    = stamp;
        sphere.header.frame_id = "odom";
        sphere.ns              = "fire";
        sphere.id              = 0;
        sphere.type            = visualization_msgs::msg::Marker::SPHERE;
        sphere.action          = visualization_msgs::msg::Marker::ADD;
        sphere.pose.position.x = fire_x;
        sphere.pose.position.y = fire_y;
        sphere.pose.position.z = 1.5;          // hoogte: midden van de vlammen
        sphere.pose.orientation.w = 1.0;
        sphere.scale.x = 1.2;
        sphere.scale.y = 1.2;
        sphere.scale.z = 1.2;
        sphere.color.r = 1.0f;                 // oranje
        sphere.color.g = 0.4f;
        sphere.color.b = 0.0f;
        sphere.color.a = 0.7f;
        sphere.lifetime = rclcpp::Duration::from_seconds(3.0);  // verdwijnt na 3 s zonder update
        marker_pub_->publish(sphere);

        // Tekst "VUUR" boven de bol
        visualization_msgs::msg::Marker text;
        text.header    = sphere.header;
        text.ns        = "fire";
        text.id        = 1;
        text.type      = visualization_msgs::msg::Marker::TEXT_VIEW_FACING;
        text.action    = visualization_msgs::msg::Marker::ADD;
        text.pose.position.x = fire_x;
        text.pose.position.y = fire_y;
        text.pose.position.z = 3.0;
        text.pose.orientation.w = 1.0;
        text.scale.z   = 0.6;                  // teksthoogte in meter
        text.color.r   = 1.0f;
        text.color.g   = 1.0f;
        text.color.b   = 0.0f;
        text.color.a   = 1.0f;
        text.text      = "VUUR";
        text.lifetime  = rclcpp::Duration::from_seconds(3.0);
        marker_pub_->publish(text);
    }

    // ════════════════════════════════════════════════════════════════════════
    //  HULPFUNCTIE – LiDAR afstand in de richting bearing_offset
    //
    //  Strategie: DICHTSTBIJZIJNDE punt binnen de smalle kegel (±2.9°).
    //  De smalle kegel sluit zijdelingse obstakels (pillaren, geparkeerde auto's)
    //  bijna volledig uit. Muren achter het vuur zijn sowieso geblokkeerd door
    //  de brandende auto zelf en worden nooit als "dichtstbij" gekozen.
    // ════════════════════════════════════════════════════════════════════════
    double fireDistanceFromLidar(double bearing_offset)
    {
        std::lock_guard<std::mutex> lock(lidar_mutex_);
        if (!latest_lidar_) return LIDAR_DEFAULT_DIST;

        double min_dist = LIDAR_DEFAULT_DIST;
        bool   found    = false;

        sensor_msgs::PointCloud2ConstIterator<float> it_x(*latest_lidar_, "x");
        sensor_msgs::PointCloud2ConstIterator<float> it_y(*latest_lidar_, "y");

        for (; it_x != it_x.end(); ++it_x, ++it_y) {
            float lx = *it_x, ly = *it_y;
            if (!std::isfinite(lx) || !std::isfinite(ly)) continue;

            double dist = std::hypot(lx, ly);
            if (dist < LIDAR_MIN_DIST || dist > LIDAR_MAX_DIST) continue;

            double bearing = std::atan2(ly, lx);

            double diff = std::abs(bearing - bearing_offset);
            if (diff > M_PI) diff = 2.0 * M_PI - diff;

            if (diff < LIDAR_BEARING_TOL && dist < min_dist) {
                min_dist = dist;
                found    = true;
            }
        }
        return found ? min_dist : LIDAR_DEFAULT_DIST;
    }

    // ════════════════════════════════════════════════════════════════════════
    //  MEMBERS
    // ════════════════════════════════════════════════════════════════════════

    rclcpp::Subscription<sensor_msgs::msg::Image>::SharedPtr       cam_sub_;
    rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr lidar_sub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr       odom_sub_;
    rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr  goal_pub_;
    rclcpp::Publisher<visualization_msgs::msg::Marker>::SharedPtr  marker_pub_;

    // Robotpositie (uit /odom)
    double robot_x_   = 0.0;
    double robot_y_   = 0.0;
    double robot_yaw_ = 0.0;
    bool   has_odom_  = false;

    // LiDAR scan cache (beschermd met mutex voor thread-safety)
    std::mutex lidar_mutex_;
    sensor_msgs::msg::PointCloud2::SharedPtr latest_lidar_;

    // Vuurstatus
    bool   fire_detected_  = false;
    bool   fire_goal_sent_ = false;
    double last_goal_x_    = 0.0;
    double last_goal_y_    = 0.0;

    // Exponentiële smoothing op vuurpositie (voorkomt plotse sprongen bij korte LiDAR-miss)
    // alpha klein = trage, stabiele positie; alpha groot = snel maar gevoeliger voor ruis
    static constexpr double FIRE_SMOOTH_ALPHA = 0.25;
    double smooth_fire_x_  = 0.0;
    double smooth_fire_y_  = 0.0;
    bool   smooth_init_    = false;
};

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<FireNavigator>());
    rclcpp::shutdown();
    return 0;
}