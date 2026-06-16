// hose_controller.cc
// Beheert de blusslang-turret (pan + tilt) en visualiseert de waterstraal als
// een ballistische boog (blauwe LINE_STRIP in RViz).
//
// Tilt-hoek wordt berekend met de exacte projectielbewegingsvergelijking:
//   target is op (R, dH) t.o.v. de nozzle-tip
//   → kwadratische vergelijking in tan(θ) → lage-hoek oplossing
//
// De Gazebo JointPositionController (in tonk.sdf) bevat een PID die de joint
// fysiek naar de gevraagde hoek drijft.
//
// Waterstraal-visualisatie:
//   ARC_SAMPLES punten langs p(t) = nozzle + v0*t - 0.5*g*t² gepubliceerd als
//   Marker:LINE_STRIP op /water_arc (zichtbaar in RViz).
//
// Topics:
//   Sub : /fire_marker   visualization_msgs/Marker (id=0 = sphere = vuurpositie)
//   Sub : /odom          nav_msgs/Odometry
//   Pub : /hose_pan_cmd  std_msgs/Float64  → Gazebo JointPositionController
//   Pub : /hose_tilt_cmd std_msgs/Float64  → Gazebo JointPositionController
//   Pub : /water_arc     visualization_msgs/Marker (LINE_STRIP, blauw)

#include <rclcpp/rclcpp.hpp>
#include <std_msgs/msg/float64.hpp>
#include <visualization_msgs/msg/marker.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <geometry_msgs/msg/point.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Matrix3x3.h>

#include <cmath>
#include <mutex>
#include <chrono>

// ── Fysische constanten ───────────────────────────────────────────────────────
static constexpr double G          = 9.81;  // [m/s²] zwaartekracht
static constexpr double V0         = 8.0;   // [m/s]  beginsnelheid waterstraal

// ── Nozzle geometrie (benaderd vanuit robot-center) ───────────────────────────
static constexpr double NOZZLE_H   = 0.82;  // [m] hoogte nozzle-tip boven grond (spawn 0.4 + hose_base 0.42)
static constexpr double NOZZLE_OFF = 0.50;  // [m] nozzle-tip offset voor robot-center

// ── Doel hoogte op het vuur ───────────────────────────────────────────────────
static constexpr double FIRE_AIM_H = 0.5;   // [m] richt op de basis van de vlammen

// ── Parkeer- en fallback-tilt ─────────────────────────────────────────────────
static constexpr double TILT_PARK     = 0.10;  // [rad] ~6° – altijd boven horizon
static constexpr double TILT_FALLBACK = 0.35;  // [rad] ~20° – als ballistisch niet lukt

// ── Timeout ───────────────────────────────────────────────────────────────────
static constexpr double FIRE_TIMEOUT_S = 5.0;

// ── Boogvisualisatie ──────────────────────────────────────────────────────────
static constexpr int ARC_SAMPLES = 22;  // punten langs de parabool

class HoseController : public rclcpp::Node
{
public:
    HoseController() : Node("hose_controller")
    {
        fire_sub_ = create_subscription<visualization_msgs::msg::Marker>(
            "/fire_marker", 5,
            [this](visualization_msgs::msg::Marker::SharedPtr m){ fireCallback(m); });

        odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
            "/odom", 10,
            [this](nav_msgs::msg::Odometry::SharedPtr m){ odomCallback(m); });

        pan_pub_  = create_publisher<std_msgs::msg::Float64>("/hose_pan_cmd",  5);
        tilt_pub_ = create_publisher<std_msgs::msg::Float64>("/hose_tilt_cmd", 5);
        arc_pub_  = create_publisher<visualization_msgs::msg::Marker>("/water_arc", 5);

        timer_ = create_wall_timer(
            std::chrono::milliseconds(100),
            [this]{ controlLoop(); });

        RCLCPP_INFO(get_logger(), "Hose controller (ballistisch) gestart");
        RCLCPP_INFO(get_logger(),
            "  V0=%.1f m/s | nozzle_h=%.2f m | doel_h=%.2f m",
            V0, NOZZLE_H, FIRE_AIM_H);
    }

private:
    // ══════════════════════════════════════════════════════════════════════════
    //  ODOMETRY
    // ══════════════════════════════════════════════════════════════════════════
    void odomCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        std::lock_guard<std::mutex> lk(mutex_);
        robot_x_ = msg->pose.pose.position.x;
        robot_y_ = msg->pose.pose.position.y;
        tf2::Quaternion q(
            msg->pose.pose.orientation.x, msg->pose.pose.orientation.y,
            msg->pose.pose.orientation.z, msg->pose.pose.orientation.w);
        double r, p;
        tf2::Matrix3x3(q).getRPY(r, p, robot_yaw_);
        has_odom_ = true;
    }

    // ══════════════════════════════════════════════════════════════════════════
    //  FIRE MARKER
    // ══════════════════════════════════════════════════════════════════════════
    void fireCallback(const visualization_msgs::msg::Marker::SharedPtr msg)
    {
        if (msg->id != 0) return;  // sphere marker (id=0) = vuurcentrum
        std::lock_guard<std::mutex> lk(mutex_);
        fire_x_ = msg->pose.position.x;
        fire_y_ = msg->pose.position.y;
        if (!fire_detected_)
            RCLCPP_INFO(get_logger(),
                "Vuur @ (%.1f, %.1f) – ballistisch richten gestart", fire_x_, fire_y_);
        fire_detected_  = true;
        last_fire_seen_ = std::chrono::steady_clock::now();
    }

    // ══════════════════════════════════════════════════════════════════════════
    //  BALLISTISCHE HOEKBEREKENING
    //
    //  Doelstelling: projectiel gelanceerd op (0, nozzle_z) met snelheid V0
    //  moet landen op (R, FIRE_AIM_H).
    //
    //  Vergelijking (subsitutie u = tan θ):
    //    A·u² - R·u + (A + dH) = 0
    //    A = g·R²/(2·V0²)
    //    dH = FIRE_AIM_H - nozzle_z   (negatief: doel lager dan nozzle)
    //
    //  Twee oplossingen: lage hoek (directe schoot) en hoge hoek (lob).
    //  We kiezen de lage hoek als die boven de horizon ligt (θ > 0.05 rad).
    // ══════════════════════════════════════════════════════════════════════════
    double ballisticTilt(double R, double nozzle_z) const
    {
        if (R < 0.5) return TILT_FALLBACK;

        double dH = FIRE_AIM_H - nozzle_z;          // negatief (doel is lager)
        double A  = G * R * R / (2.0 * V0 * V0);
        double disc = R * R - 4.0 * A * (A + dH);

        if (disc < 0.0) {
            // V0 onvoldoende om doel te bereiken → gebruik fallback
            RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000,
                "Ballistisch: geen oplossing (disc<0) voor R=%.1f m – fallback", R);
            return TILT_FALLBACK;
        }

        double sq = std::sqrt(disc);
        double u_low  = (R - sq) / (2.0 * A);   // lage hoek
        double u_high = (R + sq) / (2.0 * A);   // hoge hoek (lob)

        double theta_low  = std::atan(u_low);
        double theta_high = std::atan(u_high);

        // Lage hoek boven horizon? Dan die gebruiken (meer realistisch voor brandweerslang)
        if (theta_low  >= 0.05) return theta_low;
        if (theta_high >= 0.05) return theta_high;
        return TILT_FALLBACK;
    }

    // ══════════════════════════════════════════════════════════════════════════
    //  WATERSTRAAL BOOG – LINE_STRIP marker in RViz
    //  Punten langs p(t) = nozzle + v·t - ½g·t² tot landing op FIRE_AIM_H
    // ══════════════════════════════════════════════════════════════════════════
    void publishArc(double pan_world, double tilt,
                    double nozzle_wx, double nozzle_wy, double nozzle_wz)
    {
        // Vluchttijd: nozzle_wz + vz·T - ½g·T² = FIRE_AIM_H
        // → ½g·T² - vz·T + (FIRE_AIM_H - nozzle_wz) = 0
        double vz   = V0 * std::sin(tilt);
        double vxy  = V0 * std::cos(tilt);
        double dz   = FIRE_AIM_H - nozzle_wz;
        double disc = vz * vz - 2.0 * G * dz;
        double T = (disc >= 0.0)
                   ? (vz + std::sqrt(disc)) / G   // langste vluchttijd (dalende fase)
                   : vxy > 0.01 ? std::hypot(fire_x_ - nozzle_wx, fire_y_ - nozzle_wy) / vxy : 1.5;

        visualization_msgs::msg::Marker arc;
        arc.header.stamp    = now();
        arc.header.frame_id = "odom";
        arc.ns              = "water_arc";
        arc.id              = 10;
        arc.type            = visualization_msgs::msg::Marker::LINE_STRIP;
        arc.action          = visualization_msgs::msg::Marker::ADD;
        arc.scale.x         = 0.07;         // lijndikte [m]
        arc.color.r         = 0.0f;
        arc.color.g         = 0.55f;
        arc.color.b         = 1.0f;
        arc.color.a         = 0.9f;
        arc.lifetime        = rclcpp::Duration::from_seconds(0.35);
        arc.pose.orientation.w = 1.0;

        double vwx = vxy * std::cos(pan_world);
        double vwy = vxy * std::sin(pan_world);

        for (int i = 0; i <= ARC_SAMPLES; ++i) {
            double t = T * static_cast<double>(i) / ARC_SAMPLES;
            geometry_msgs::msg::Point p;
            p.x = nozzle_wx + vwx * t;
            p.y = nozzle_wy + vwy * t;
            p.z = nozzle_wz + vz * t - 0.5 * G * t * t;
            // Niet onder de grond tekenen
            if (p.z < 0.0) p.z = 0.0;
            arc.points.push_back(p);
        }
        arc_pub_->publish(arc);
    }

    // ══════════════════════════════════════════════════════════════════════════
    //  CONTROL LOOP – 10 Hz
    // ══════════════════════════════════════════════════════════════════════════
    void controlLoop()
    {
        std::lock_guard<std::mutex> lk(mutex_);

        // Timeout: vuur al te lang niet gezien?
        if (fire_detected_) {
            double age = std::chrono::duration<double>(
                std::chrono::steady_clock::now() - last_fire_seen_).count();
            if (age > FIRE_TIMEOUT_S) {
                fire_detected_ = false;
                // Verwijder boog-marker
                visualization_msgs::msg::Marker del;
                del.header.stamp    = now();
                del.header.frame_id = "odom";
                del.ns = "water_arc"; del.id = 10;
                del.action = visualization_msgs::msg::Marker::DELETE;
                arc_pub_->publish(del);
                RCLCPP_INFO(get_logger(), "Vuur verdwenen – hose naar parkeerstand");
            }
        }

        // Geen vuur of geen odom → parkeerstand
        if (!fire_detected_ || !has_odom_) {
            publish(pan_pub_,  0.0);
            publish(tilt_pub_, TILT_PARK);
            return;
        }

        // ── Pan: exact op het vuur richten ───────────────────────────────────
        double dx        = fire_x_ - robot_x_;
        double dy        = fire_y_ - robot_y_;
        double pan_world = std::atan2(dy, dx);           // world-frame richting naar vuur
        double pan_cmd   = pan_world - robot_yaw_;       // relatief t.o.v. robot

        while (pan_cmd >  M_PI) pan_cmd -= 2.0 * M_PI;
        while (pan_cmd < -M_PI) pan_cmd += 2.0 * M_PI;

        // ── Nozzle-tip positie (geschat, θ nog onbekend, gebruik TILT_PARK als seed) ──
        // We benaderen eerst nozzle_wz zonder tilt-correctie, dan corrigeren we.
        double nozzle_wz_approx = NOZZLE_H;   // ≈ 0.82 m

        // ── Horizontale afstand van nozzle-tip tot vuur ───────────────────────
        double R_center = std::hypot(dx, dy);
        double R_nozzle = std::max(0.5, R_center - NOZZLE_OFF);

        // ── Ballistisch hoek ──────────────────────────────────────────────────
        double tilt_cmd = ballisticTilt(R_nozzle, nozzle_wz_approx);

        // ── Verfijn nozzle-positie met bekende tilt ───────────────────────────
        double nozzle_wx = robot_x_ + NOZZLE_OFF * std::cos(tilt_cmd) * std::cos(pan_world);
        double nozzle_wy = robot_y_ + NOZZLE_OFF * std::cos(tilt_cmd) * std::sin(pan_world);
        double nozzle_wz = NOZZLE_H + NOZZLE_OFF * std::sin(tilt_cmd);

        // ── Publiceer joint commando's ────────────────────────────────────────
        publish(pan_pub_,  pan_cmd);
        publish(tilt_pub_, tilt_cmd);

        // ── Publiceer waterstraal-boog ────────────────────────────────────────
        publishArc(pan_world, tilt_cmd, nozzle_wx, nozzle_wy, nozzle_wz);

        RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 2000,
            "BLUS: pan=%.1f° tilt=%.1f° | R=%.1f m | vuur@(%.1f, %.1f)",
            pan_cmd  * 180.0 / M_PI,
            tilt_cmd * 180.0 / M_PI,
            R_nozzle, fire_x_, fire_y_);
    }

    void publish(rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr & pub, double val)
    {
        std_msgs::msg::Float64 msg;
        msg.data = val;
        pub->publish(msg);
    }

    // ── Members ───────────────────────────────────────────────────────────────
    rclcpp::Subscription<visualization_msgs::msg::Marker>::SharedPtr fire_sub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr          odom_sub_;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr              pan_pub_;
    rclcpp::Publisher<std_msgs::msg::Float64>::SharedPtr              tilt_pub_;
    rclcpp::Publisher<visualization_msgs::msg::Marker>::SharedPtr     arc_pub_;
    rclcpp::TimerBase::SharedPtr                                      timer_;

    std::mutex mutex_;
    double robot_x_ = 0.0, robot_y_ = 0.0, robot_yaw_ = 0.0;
    bool   has_odom_ = false;
    double fire_x_   = 0.0, fire_y_ = 0.0;
    bool   fire_detected_ = false;
    std::chrono::steady_clock::time_point last_fire_seen_;
};

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<HoseController>());
    rclcpp::shutdown();
    return 0;
}
