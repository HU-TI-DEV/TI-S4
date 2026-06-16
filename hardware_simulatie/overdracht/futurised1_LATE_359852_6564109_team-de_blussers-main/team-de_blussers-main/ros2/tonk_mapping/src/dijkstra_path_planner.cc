// dijkstra_path_planner.cc
// Pathfinding node voor de Tonk robot
//
// De robot krijgt een doel binnen via /goal_pose en rijdt daar zelfstandig naartoe.
// De LiDAR bouwt een kaart van obstakels, Dijkstra zoekt de kortste route,
// en een simpele regelaar stuurt de robot langs de waypoints.
//
// Topics die we gebruiken:
//   /lidar/pointcloud  → obstakels in kaart brengen
//   /odom              → positie van de robot bijhouden
//   /goal_pose         → doel ontvangen van fire_navigator
//   /cmd_vel           → rijcommando's sturen
//   /map               → kaart publiceren naar RViz
//   /path              → geplande route tonen in RViz

#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/point_cloud2.hpp>
#include <sensor_msgs/point_cloud2_iterator.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <nav_msgs/msg/occupancy_grid.hpp>
#include <nav_msgs/msg/path.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <visualization_msgs/msg/marker.hpp>
#include <geometry_msgs/msg/transform_stamped.hpp>
#include <tf2/LinearMath/Quaternion.h>
#include <tf2/LinearMath/Matrix3x3.h>
#include <tf2_ros/buffer.h>
#include <tf2_ros/transform_listener.h>

#include <memory>

#include <algorithm>
#include <cmath>
#include <limits>
#include <map>
#include <queue>
#include <vector>

// grid instellingen: 450x300 cellen van 0.2m = 90x60m kaart
// dat is ruim genoeg voor de hele parkeergarage
static constexpr double GRID_RES      = 0.2;
static constexpr int    GRID_W        = 450;
static constexpr int    GRID_H        = 300;
static constexpr double GRID_ORIGIN_X = -45.0;  // linksonder hoek van de kaart
static constexpr double GRID_ORIGIN_Y = -30.0;

// hoe ver we obstakels opblazen zodat de robot er niet tegenaan rijdt
// de robot is 1.6m breed (halve breedte 0.8m) dus 1.0m harde grens = 0.2m marge.
// NB: groter (bv. 2.0m) sluit met de persistente SLAM-kaart de doorgangen dicht,
// waardoor de robot zichzelf insluit en halverwege stopt.
static constexpr double INFLATE_RADIUS = 1.0;  // harde grens, hier mag de robot niet komen
static constexpr double COST_RADIUS    = 0.6;  // zachte zone eromheen, passeerbaar maar duurder
static constexpr double ROBOT_RADIUS   = 0.5;  // vrije bubbel rond de robot (footprint-escape)
static constexpr double MAX_CELL_COST  = 4.0;  // hoe zwaar de zachte zone meetelt in de kosten
static constexpr double WAYPOINT_TOL   = 0.25; // binnen hoeveel meter ga je naar het volgende waypoint
static constexpr double GOAL_TOL       = 0.5;  // binnen hoeveel meter beschouwen we het doel als bereikt
static constexpr double MAX_LINEAR     = 0.6;  // maximale rijsnelheid in m/s
static constexpr double MAX_ANGULAR    = 2.0;  // maximale draaisnelheid in rad/s
static constexpr double KP_ANGULAR     = 2.0;  // hoe hard we bijsturen als we scheef rijden

// extra kostenzone rond gedetecteerde personen
static constexpr double PERSON_HARD_RADIUS = 0.8;  // hier mag de robot niet komen
static constexpr double PERSON_COST_RADIUS = 4.0;  // zachte zone eromheen, duurder maar passeerbaar
static constexpr double PERSON_TIMEOUT_S   = 2.0;  // persoon vergeten als de marker te oud is

class DijkstraPathPlanner : public rclcpp::Node
{
public:
    DijkstraPathPlanner() : Node("dijkstra_path_planner")
    {
        // use_external_map = true  -> kaart komt van een externe SLAM-node op /map,
        //                            en de robotpositie komt uit TF (global_frame -> base_frame).
        // use_external_map = false -> oude gedrag: zelf een grid bouwen uit /lidar/pointcloud
        //                            en de positie uit /odom halen.
        use_external_map_ = declare_parameter<bool>("use_external_map", false);
        global_frame_     = declare_parameter<std::string>("global_frame", "odom");
        base_frame_       = declare_parameter<std::string>("base_frame", "base_link");

        goal_sub_ = create_subscription<geometry_msgs::msg::PoseStamped>(
            "/goal_pose", 5,
            [this](geometry_msgs::msg::PoseStamped::SharedPtr m){ goalCallback(m); });

        person_sub_ = create_subscription<visualization_msgs::msg::Marker>(
            "/person_marker", 10,
            [this](visualization_msgs::msg::Marker::SharedPtr m){ personCallback(m); });

        map_pub_  = create_publisher<nav_msgs::msg::OccupancyGrid>("/map", 5);
        path_pub_ = create_publisher<nav_msgs::msg::Path>("/path", 5);
        cmd_pub_  = create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

        // De geïnflateerde costmap (de "heatmap" met kostgradient rond obstakels)
        // wordt altijd op /costmap gepubliceerd — ook in SLAM-modus, waar /map de
        // ruwe kaart van de map_accumulator is. Zo is de heatmap in RViz zichtbaar
        // ongeacht welke launch draait.
        costmap_pub_ = create_publisher<nav_msgs::msg::OccupancyGrid>("/costmap", 5);

        if (use_external_map_) {
            // SLAM-modus: kaart + pose komen van buiten.
            tf_buffer_   = std::make_unique<tf2_ros::Buffer>(get_clock());
            tf_listener_ = std::make_shared<tf2_ros::TransformListener>(*tf_buffer_);

            map_sub_ = create_subscription<nav_msgs::msg::OccupancyGrid>(
                "/map", 1,
                [this](nav_msgs::msg::OccupancyGrid::SharedPtr m){ mapCallback(m); });
        } else {
            // Klassieke modus: zelf mappen vanuit de lidar en pose uit /odom.
            lidar_sub_ = create_subscription<sensor_msgs::msg::PointCloud2>(
                "/lidar/pointcloud", 5,
                [this](sensor_msgs::msg::PointCloud2::SharedPtr m){ lidarCallback(m); });

            odom_sub_ = create_subscription<nav_msgs::msg::Odometry>(
                "/odom", 10,
                [this](nav_msgs::msg::Odometry::SharedPtr m){ odomCallback(m); });

            map_pub_ = create_publisher<nav_msgs::msg::OccupancyGrid>("/map", 5);
        }

        grid_.assign(GRID_W * GRID_H, 0);

        // regelloop draait op 20Hz
        ctrl_timer_ = create_wall_timer(
            std::chrono::milliseconds(50),
            [this](){ controlLoop(); });

        RCLCPP_INFO(get_logger(), "Dijkstra path planner gestart (%s)",
                    use_external_map_ ? "externe SLAM-kaart" : "eigen lidar-kaart");
        RCLCPP_INFO(get_logger(), "  Gebruik de RViz 'SetGoal' tool om een doel in te stellen");
        RCLCPP_INFO(get_logger(), "  Grid: %d x %d cellen @ %.2f m/cel", GRID_W, GRID_H, GRID_RES);
    }

private:
    // positie en richting van de robot bijhouden
    void odomCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        robot_x_ = msg->pose.pose.position.x;
        robot_y_ = msg->pose.pose.position.y;

        // quaternion omzetten naar yaw (draaihoek)
        tf2::Quaternion q(
            msg->pose.pose.orientation.x,
            msg->pose.pose.orientation.y,
            msg->pose.pose.orientation.z,
            msg->pose.pose.orientation.w);
        double roll, pitch;
        tf2::Matrix3x3(q).getRPY(roll, pitch, robot_yaw_);
        has_odom_ = true;
    }

    // SLAM-modus: positie van de robot uit TF halen (global_frame -> base_frame).
    // Geeft true als de transform beschikbaar was.
    bool updatePoseFromTF()
    {
        geometry_msgs::msg::TransformStamped tf;
        try {
            tf = tf_buffer_->lookupTransform(global_frame_, base_frame_, tf2::TimePointZero);
        } catch (const std::exception & e) {
            RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 2000,
                "Geen TF %s <- %s: %s", global_frame_.c_str(), base_frame_.c_str(), e.what());
            return false;
        }

        robot_x_ = tf.transform.translation.x;
        robot_y_ = tf.transform.translation.y;

        tf2::Quaternion q(tf.transform.rotation.x, tf.transform.rotation.y,
                          tf.transform.rotation.z, tf.transform.rotation.w);
        double roll, pitch;
        tf2::Matrix3x3(q).getRPY(roll, pitch, robot_yaw_);
        has_odom_ = true;
        return true;
    }

    // SLAM-modus: kaart komt binnen van de map_accumulator. We nemen de ruwe
    // occupancy-grid over en blazen de obstakels op voor de planning.
    void mapCallback(const nav_msgs::msg::OccupancyGrid::SharedPtr msg)
    {
        if (static_cast<int>(msg->info.width) != GRID_W ||
            static_cast<int>(msg->info.height) != GRID_H) {
            RCLCPP_WARN_THROTTLE(get_logger(), *get_clock(), 5000,
                "Kaart-afmeting (%ux%u) wijkt af van planner-grid (%dx%d); negeren.",
                msg->info.width, msg->info.height, GRID_W, GRID_H);
            return;
        }

        grid_.assign(msg->data.begin(), msg->data.end());
        inflateObstacles();
        publishMap(msg->header.stamp);  // geïnflateerde costmap → /costmap (heatmap)
        last_lidar_time_ = now();

        if (has_goal_ && updatePoseFromTF() &&
            (now() - last_plan_time_).seconds() > 0.5) {
            last_plan_time_ = now();
            planPath();
            publishPath(msg->header.stamp);
        }
    }

    void lidarCallback(const sensor_msgs::msg::PointCloud2::SharedPtr msg)
    {
        if (!has_odom_) return;

        last_lidar_time_ = now();

        buildOccupancyGrid(msg);
        publishMap(msg->header.stamp);

        // maximaal 2x per seconde herplannen, anders wisselt de route te snel
        // en gaat de robot heen en weer slingeren
        if (has_goal_ && (now() - last_plan_time_).seconds() > 0.5) {
            last_plan_time_ = now();
            planPath();
            publishPath(msg->header.stamp);
        }
    }

    // onthoud de wereldpositie van elke gedetecteerde persoon (alleen de CUBE-box,
    // niet het tekstlabel). De positie wordt later als kostenzone in de grid gezet.
    void personCallback(const visualization_msgs::msg::Marker::SharedPtr msg)
    {
        if (msg->type != visualization_msgs::msg::Marker::CUBE) return;
        persons_[msg->id] = { msg->pose.position.x, msg->pose.position.y, now() };
    }

    void goalCallback(const geometry_msgs::msg::PoseStamped::SharedPtr msg)
    {
        double new_x = msg->pose.position.x;
        double new_y = msg->pose.position.y;

        // als het doel nauwelijks veranderd is sturen we het pad niet opnieuw op
        // anders reset de robot zijn route elke 3 seconden en schok hij constant
        double delta = std::hypot(new_x - goal_x_, new_y - goal_y_);
        if (has_goal_ && delta < 0.3) return;

        goal_x_   = new_x;
        goal_y_   = new_y;
        has_goal_ = true;
        path_idx_ = 0;
        path_.clear();

        RCLCPP_INFO(get_logger(), "Nieuw doel: (%.2f, %.2f)", goal_x_, goal_y_);

        if (use_external_map_) updatePoseFromTF();
        if (has_odom_) {
            last_plan_time_ = now();
            planPath();
        }
    }

    // bouw een occupancy grid vanuit de lidar scan
    // lidar geeft punten relatief aan de robot, wij zetten ze om naar wereldcoordinaten
    //
    //   wereldpositie = roteer(lidar punt, robot_yaw) + robot_positie
    //
    void buildOccupancyGrid(const sensor_msgs::msg::PointCloud2::SharedPtr msg)
    {
        std::fill(grid_.begin(), grid_.end(), 0);

        const double cos_yaw = std::cos(robot_yaw_);
        const double sin_yaw = std::sin(robot_yaw_);

        sensor_msgs::PointCloud2ConstIterator<float> it_x(*msg, "x");
        sensor_msgs::PointCloud2ConstIterator<float> it_y(*msg, "y");

        for (; it_x != it_x.end(); ++it_x, ++it_y) {
            float lx = *it_x, ly = *it_y;
            if (!std::isfinite(lx) || !std::isfinite(ly)) continue;

            // lidar punt omzetten naar wereldcoordinaten
            double wx = cos_yaw * lx - sin_yaw * ly + robot_x_;
            double wy = sin_yaw * lx + cos_yaw * ly + robot_y_;

            // wereldcoordinaten omzetten naar gridcel
            int col = static_cast<int>((wx - GRID_ORIGIN_X) / GRID_RES);
            int row = static_cast<int>((wy - GRID_ORIGIN_Y) / GRID_RES);

            if (col >= 0 && col < GRID_W && row >= 0 && row < GRID_H) {
                grid_[row * GRID_W + col] = 100;
            }
        }

        // obstakels wat groter maken zodat de robot er niet tegenaan rijdt
        inflateObstacles();

        // gedetecteerde personen als extra kostenzone toevoegen
        updatePersonCost();
    }

    // markeer een dure zone rond elke (recent gedetecteerde) persoon, zodat Dijkstra een ruime boog om mensen heen plant:
    // binnen PERSON_HARD_RADIUS: volledig geblokkeerd (100)
    // daarbuiten tot PERSON_COST_RADIUS: passeerbaar maar duur
    void updatePersonCost()
    {
        const rclcpp::Time t_now = now();
        const int reach = static_cast<int>(
            std::ceil((PERSON_HARD_RADIUS + PERSON_COST_RADIUS) / GRID_RES));

        for (auto it = persons_.begin(); it != persons_.end(); ) {
            // oude detecties weggooien zodat er geen ghost detectes blijven staan
            if ((t_now - it->second.stamp).seconds() > PERSON_TIMEOUT_S) {
                it = persons_.erase(it);
                continue;
            }

            const int pc = static_cast<int>((it->second.x - GRID_ORIGIN_X) / GRID_RES);
            const int pr = static_cast<int>((it->second.y - GRID_ORIGIN_Y) / GRID_RES);
            ++it;

            for (int dr = -reach; dr <= reach; ++dr) {
                for (int dc = -reach; dc <= reach; ++dc) {
                    int nr = pr + dr, nc = pc + dc;
                    if (nr < 0 || nr >= GRID_H || nc < 0 || nc >= GRID_W) continue;

                    double d = std::hypot(dr, dc) * GRID_RES;
                    int8_t value;

                    if (d <= PERSON_HARD_RADIUS) {
                        value = 100;  // mag hier niet komen
                    } else if (d < PERSON_HARD_RADIUS + PERSON_COST_RADIUS) {
                        // hoe dichter bij de persoon, hoe duurder
                        double t = 1.0 - (d - PERSON_HARD_RADIUS) / PERSON_COST_RADIUS;
                        value = static_cast<int8_t>(5 + t * 90);
                    } else {
                        continue;
                    }

                    // hoogste waarde wint als zones overlappen met obstakels
                    int idx = nr * GRID_W + nc;
                    if (value > grid_[idx]) grid_[idx] = value;
                }
            }
        }
    }

    // blokkeer cellen rondom obstakels:
    //   - binnen INFLATE_RADIUS: volledig geblokkeerd (100)
    //   - daarbuiten tot COST_RADIUS: passeerbaar maar duurder (zodat Dijkstra het liever mijdt)
    void inflateObstacles()
    {
        const int total_cells = static_cast<int>(
            std::ceil((INFLATE_RADIUS + COST_RADIUS) / GRID_RES));
        std::vector<int8_t> result = grid_;

        for (int r = 0; r < GRID_H; ++r) {
            for (int c = 0; c < GRID_W; ++c) {
                if (grid_[r * GRID_W + c] != 100) continue;

                for (int dr = -total_cells; dr <= total_cells; ++dr) {
                    for (int dc = -total_cells; dc <= total_cells; ++dc) {
                        int nr = r + dr, nc = c + dc;
                        if (nr < 0 || nr >= GRID_H || nc < 0 || nc >= GRID_W) continue;

                        double d = std::hypot(dr, dc) * GRID_RES;
                        int8_t value;

                        if (d <= INFLATE_RADIUS) {
                            value = 100;  // mag hier niet komen
                        } else if (d < INFLATE_RADIUS + COST_RADIUS) {
                            // hoe dichter bij het obstakel, hoe duurder
                            double t = 1.0 - (d - INFLATE_RADIUS) / COST_RADIUS;
                            value = static_cast<int8_t>(5 + t * 85);
                        } else {
                            continue;
                        }

                        // hoogste waarde wint als meerdere obstakels overlappen
                        if (value > result[nr * GRID_W + nc]) {
                            result[nr * GRID_W + nc] = value;
                        }
                    }
                }
            }
        }
        grid_ = std::move(result);
    }

    // zoek het kortste pad van robot naar doel met het Dijkstra algoritme
    // we kijken in 8 richtingen (horizontaal, verticaal en diagonaal)
    // diagonaal is iets duurder dan recht (√2 vs 1)
    bool planPath()
    {
        path_.clear();
        path_idx_ = 0;

        // hulpfunctie om wereldcoordinaten om te zetten naar een gridindex
        auto toIdx = [&](double x, double y) -> int {
            int c = static_cast<int>((x - GRID_ORIGIN_X) / GRID_RES);
            int r = static_cast<int>((y - GRID_ORIGIN_Y) / GRID_RES);
            if (c < 0 || c >= GRID_W || r < 0 || r >= GRID_H) return -1;
            return r * GRID_W + c;
        };

        const int start = toIdx(robot_x_, robot_y_);
        int       goal  = toIdx(goal_x_,  goal_y_);

        if (start < 0 || goal < 0) {
            RCLCPP_WARN(get_logger(), "Start (%.2f,%.2f) of doel (%.2f,%.2f) buiten grid",
                        robot_x_, robot_y_, goal_x_, goal_y_);
            return false;
        }

        // Footprint-escape: maak een kleine vrije bubbel rond de robotpositie.
        // De robot staat hier fysiek al, dus deze cellen zijn per definitie bereikbaar.
        // Zonder dit kan de (geaccumuleerde) inflatie de robot insluiten -> geen pad
        // -> robot stopt halverwege. Zo kan hij altijd uit zijn eigen cel vertrekken.
        {
            const int esc = static_cast<int>(std::ceil(ROBOT_RADIUS / GRID_RES));
            const int scol = start % GRID_W, srow = start / GRID_W;
            for (int dr = -esc; dr <= esc; ++dr) {
                for (int dc = -esc; dc <= esc; ++dc) {
                    const int nr = srow + dr, nc = scol + dc;
                    if (nr < 0 || nr >= GRID_H || nc < 0 || nc >= GRID_W) continue;
                    if (std::hypot(dr, dc) * GRID_RES <= ROBOT_RADIUS)
                        grid_[nr * GRID_W + nc] = 0;
                }
            }
        }
        if (grid_[goal] == 100) {
            // het doel ligt in een obstakel (het vuur heeft geen lidar mesh
            // dus de afstand klopt niet altijd). We zoeken de dichtsbijzijnde vrije cel.
            int    best_idx  = -1;
            double best_dist = std::numeric_limits<double>::infinity();
            const int goal_col   = goal % GRID_W;
            const int goal_row   = goal / GRID_W;
            const int search_r   = static_cast<int>(std::ceil(3.0 / GRID_RES));

            // eerst proberen we een cel te vinden die helemaal vrij is
            for (int dr = -search_r; dr <= search_r; ++dr) {
                for (int dc = -search_r; dc <= search_r; ++dc) {
                    int nr = goal_row + dr, nc = goal_col + dc;
                    if (nr < 0 || nr >= GRID_H || nc < 0 || nc >= GRID_W) continue;
                    int nidx = nr * GRID_W + nc;
                    if (grid_[nidx] != 0) continue;
                    double d = std::hypot(dr, dc);
                    if (d < best_dist) { best_dist = d; best_idx = nidx; }
                }
            }
            // als de garage te vol is, accepteren we ook cellen die wel passeerbaar zijn
            if (best_idx < 0) {
                for (int dr = -search_r; dr <= search_r; ++dr) {
                    for (int dc = -search_r; dc <= search_r; ++dc) {
                        int nr = goal_row + dr, nc = goal_col + dc;
                        if (nr < 0 || nr >= GRID_H || nc < 0 || nc >= GRID_W) continue;
                        int nidx = nr * GRID_W + nc;
                        if (grid_[nidx] == 100) continue;
                        double d = std::hypot(dr, dc);
                        if (d < best_dist) { best_dist = d; best_idx = nidx; }
                    }
                }
            }
            if (best_idx < 0) {
                RCLCPP_WARN(get_logger(), "Doel in obstakel, geen bereikbare cel binnen 3 m gevonden");
                return false;
            }
            double sx = (best_idx % GRID_W + 0.5) * GRID_RES + GRID_ORIGIN_X;
            double sy = (best_idx / GRID_W + 0.5) * GRID_RES + GRID_ORIGIN_Y;
            RCLCPP_INFO_THROTTLE(get_logger(), *get_clock(), 2000,
                "Doel bijgesteld naar vrije cel (%.1f, %.1f)", sx, sy);
            goal = best_idx;
        }

        // 8 richtingen: links, rechts, boven, onder en de 4 diagonalen
        constexpr int    DX[8] = {-1, 0, 1, -1, 1, -1, 0, 1};
        constexpr int    DY[8] = {-1,-1,-1,  0, 0,  1, 1, 1};
        constexpr double DC[8] = {1.414, 1.0, 1.414, 1.0, 1.0, 1.414, 1.0, 1.414};

        const double INF = std::numeric_limits<double>::infinity();
        std::vector<double> dist(GRID_W * GRID_H, INF);
        std::vector<int>    prev(GRID_W * GRID_H, -1);

        // priority queue zodat we altijd de goedkoopste cel als eerste verwerken
        using PQNode = std::pair<double, int>;
        std::priority_queue<PQNode, std::vector<PQNode>, std::greater<PQNode>> pq;

        dist[start] = 0.0;
        pq.push({0.0, start});

        while (!pq.empty()) {
            auto [cost, idx] = pq.top(); pq.pop();

            if (idx == goal) break;
            if (cost > dist[idx]) continue;  // al een goedkopere route gevonden

            const int col = idx % GRID_W;
            const int row = idx / GRID_W;

            for (int d = 0; d < 8; ++d) {
                int nc = col + DX[d];
                int nr = row + DY[d];

                if (nc < 0 || nc >= GRID_W || nr < 0 || nr >= GRID_H) continue;

                const int nidx = nr * GRID_W + nc;
                if (grid_[nidx] == 100) continue;  // obstakel, overslaan

                // cellen dichtbij obstakels kosten extra zodat we liever ruimer gaan
                double cell_cost = (grid_[nidx] / 100.0) * MAX_CELL_COST * GRID_RES;
                double new_cost  = cost + DC[d] * GRID_RES + cell_cost;
                if (new_cost < dist[nidx]) {
                    dist[nidx] = new_cost;
                    prev[nidx] = idx;
                    pq.push({new_cost, nidx});
                }
            }
        }

        if (dist[goal] == INF) {
            RCLCPP_WARN(get_logger(), "Geen pad gevonden naar (%.2f, %.2f)", goal_x_, goal_y_);
            return false;
        }

        // pad terugvolgen via prev array en dan omdraaien
        for (int idx = goal; idx != -1; idx = prev[idx]) {
            double wx = (idx % GRID_W + 0.5) * GRID_RES + GRID_ORIGIN_X;
            double wy = (idx / GRID_W + 0.5) * GRID_RES + GRID_ORIGIN_Y;
            path_.emplace_back(wx, wy);
        }
        std::reverse(path_.begin(), path_.end());

        RCLCPP_INFO(get_logger(), "Pad gevonden: %zu waypoints, %.1f m",
                    path_.size(), dist[goal]);
        return true;
    }

    // regelloop op 20Hz: stuur de robot langs de waypoints
    // we gebruiken een proportionele regelaar:
    //   - hoe meer we scheef staan, hoe harder we bijdraaien
    //   - bij scherpe bochten rijden we ook langzamer
    void controlLoop()
    {
        geometry_msgs::msg::Twist cmd;  // standaard stilstaan

        if (use_external_map_) {
            // SLAM-modus: huidige robotpositie uit TF halen.
            updatePoseFromTF();
        } else if (last_lidar_time_.nanoseconds() > 0 &&
                   (now() - last_lidar_time_).seconds() > 1.0) {
            // klassieke modus: als de lidar >1s niets gestuurd heeft, leeg de vluchtige kaart
            std::fill(grid_.begin(), grid_.end(), 0);
            publishMap(now());
            last_lidar_time_ = rclcpp::Time(0, 0, RCL_ROS_TIME);
        }

        if (!has_goal_ || !has_odom_ || path_.empty()) {
            cmd_pub_->publish(cmd);
            return;
        }

        // sla waypoints over die we al voorbij zijn
        while (path_idx_ < path_.size()) {
            double dx = path_[path_idx_].first  - robot_x_;
            double dy = path_[path_idx_].second - robot_y_;
            if (std::hypot(dx, dy) > WAYPOINT_TOL) break;
            ++path_idx_;
        }

        // check of we het eindpunt bereikt hebben
        if (std::hypot(goal_x_ - robot_x_, goal_y_ - robot_y_) < GOAL_TOL) {
            RCLCPP_INFO(get_logger(), "Doel bereikt op (%.2f, %.2f)!", goal_x_, goal_y_);
            has_goal_ = false;
            cmd_pub_->publish(cmd);
            return;
        }

        if (path_idx_ >= path_.size()) {
            cmd_pub_->publish(cmd);
            return;
        }

        // bereken hoeveel we moeten bijsturen naar het volgende waypoint
        double dx = path_[path_idx_].first  - robot_x_;
        double dy = path_[path_idx_].second - robot_y_;

        double target_yaw = std::atan2(dy, dx);
        double yaw_err    = target_yaw - robot_yaw_;

        // hoekfout normaliseren naar -π tot π
        while (yaw_err >  M_PI) yaw_err -= 2.0 * M_PI;
        while (yaw_err < -M_PI) yaw_err += 2.0 * M_PI;

        // bij een grote hoekfout rijden we langzamer zodat we niet over de bocht schieten
        double forward = MAX_LINEAR * std::max(0.0, std::cos(yaw_err));

        cmd.linear.x  = std::clamp(forward,              0.0, MAX_LINEAR);
        cmd.angular.z = std::clamp(KP_ANGULAR * yaw_err, -MAX_ANGULAR, MAX_ANGULAR);

        cmd_pub_->publish(cmd);
    }

    void publishMap(const rclcpp::Time & stamp)
    {
        nav_msgs::msg::OccupancyGrid msg;
        msg.header.stamp        = stamp;
        msg.header.frame_id     = global_frame_;
        msg.info.resolution     = GRID_RES;
        msg.info.width          = GRID_W;
        msg.info.height         = GRID_H;
        msg.info.origin.position.x  = GRID_ORIGIN_X;
        msg.info.origin.position.y  = GRID_ORIGIN_Y;
        msg.info.origin.orientation.w = 1.0;
        msg.data.assign(grid_.begin(), grid_.end());

        // De geïnflateerde costmap (heatmap) altijd publiceren, zodat hij in RViz
        // zichtbaar is — ook in SLAM-modus waar /map de ruwe accumulator-kaart is.
        costmap_pub_->publish(msg);

        // In klassieke modus is /map zelf de geïnflateerde kaart.
        if (map_pub_) map_pub_->publish(msg);
    }

    void publishPath(const rclcpp::Time & stamp)
    {
        nav_msgs::msg::Path msg;
        msg.header.stamp    = stamp;
        msg.header.frame_id = global_frame_;

        for (auto & [x, y] : path_) {
            geometry_msgs::msg::PoseStamped ps;
            ps.header             = msg.header;
            ps.pose.position.x    = x;
            ps.pose.position.y    = y;
            ps.pose.orientation.w = 1.0;
            msg.poses.push_back(ps);
        }
        path_pub_->publish(msg);
    }

    rclcpp::Subscription<sensor_msgs::msg::PointCloud2>::SharedPtr  lidar_sub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr         odom_sub_;
    rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr goal_sub_;
    rclcpp::Subscription<visualization_msgs::msg::Marker>::SharedPtr person_sub_;
    rclcpp::Subscription<nav_msgs::msg::OccupancyGrid>::SharedPtr    map_sub_;
    rclcpp::Publisher<nav_msgs::msg::OccupancyGrid>::SharedPtr       map_pub_;
    rclcpp::Publisher<nav_msgs::msg::OccupancyGrid>::SharedPtr       costmap_pub_;
    rclcpp::Publisher<nav_msgs::msg::Path>::SharedPtr                path_pub_;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr          cmd_pub_;
    rclcpp::TimerBase::SharedPtr ctrl_timer_;

    // SLAM-modus: kaart van buiten (/map) + pose uit TF
    bool        use_external_map_ = false;
    std::string global_frame_     = "odom";
    std::string base_frame_       = "base_link";
    std::unique_ptr<tf2_ros::Buffer>            tf_buffer_;
    std::shared_ptr<tf2_ros::TransformListener> tf_listener_;

    // tijdstip van de laatste lidar scan en herplanning
    rclcpp::Time last_lidar_time_{0, 0, RCL_ROS_TIME};
    rclcpp::Time last_plan_time_{0, 0, RCL_ROS_TIME};

    // huidige positie van de robot
    double robot_x_   = 0.0;
    double robot_y_   = 0.0;
    double robot_yaw_ = 0.0;
    bool   has_odom_  = false;

    // huidig doel
    double goal_x_   = 0.0;
    double goal_y_   = 0.0;
    bool   has_goal_ = false;

    // geplande route als lijst van waypoints
    std::vector<std::pair<double, double>> path_;
    size_t path_idx_ = 0;

    // 2D kaart: 0 = vrij, 100 = geblokkeerd
    std::vector<int8_t> grid_;

    // gedetecteerde personen (wereldpositie + tijdstip) om een kostenzone te plaatsen
    struct PersonObs { double x; double y; rclcpp::Time stamp; };
    std::map<int, PersonObs> persons_;
};

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<DijkstraPathPlanner>());
    rclcpp::shutdown();
    return 0;
}
