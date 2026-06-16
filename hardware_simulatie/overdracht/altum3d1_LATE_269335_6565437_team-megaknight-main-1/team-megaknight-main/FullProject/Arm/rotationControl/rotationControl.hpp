#pragma once

#include "motorJoint.hpp"
#include <gz/transport/Node.hh>
#include <future>

// Positie van de basis van de arm in de wereld, staat op de oorsprong
constexpr float BASE_X                  = 0.0f;
constexpr float BASE_Y                  = 0.0f;

// De arm wijst in rust naar de positieve Y-as in plaats van de X-as,
// dus we corrigeren met 90° (π/2 rad)
constexpr float BASE_ORIENTATION_OFFSET = 1.5707963f;

// Berekent welke gewrichtshoek nodig is om de arm naar (obj_x, obj_y) te laten wijzen
float world_pos_to_setpoint(float obj_x, float obj_y);

// Regelt de horizontale rotatie van de arm via het basisgewricht (base_pivot)
class RotationControl
{
public:
    // Maximale hoek die het gewricht mag bereiken (~170°), voorkomt mechanische botsingen
    static constexpr double JOINT_LIMIT = 2.97;

    explicit RotationControl(gz::transport::Node& node,
                             const MotorJointConfig& cfg = {});

    // Stuurt het basisgewricht direct naar een opgegeven hoek in radialen
    std::future<void> set_angle(const double& target_rad);

    // Geeft de huidige hoek van het basisgewricht terug in radialen
    double get_angle() const;

    // Draait de arm naar de opgegeven wereldpositie via de kortste weg
    std::future<void> move_to(const float& obj_x, const float& obj_y);

private:
    MotorJoint base_pivot_;
};