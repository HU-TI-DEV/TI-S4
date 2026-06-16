#include "rotationControl.hpp"
#include <cmath>
#include <iostream>

// Berekent de benodigde gewrichtshoek om naar wereldpositie (obj_x, obj_y) te wijzen.
// atan2 geeft de hoek t.o.v. de X-as; de offset corrigeert voor de rustoriëntatie van de arm.
float world_pos_to_setpoint(float obj_x, float obj_y)
{
    float angle = std::atan2(obj_y - BASE_Y, obj_x - BASE_X);
    return angle - BASE_ORIENTATION_OFFSET;
}

RotationControl::RotationControl(gz::transport::Node& node,
                                 const MotorJointConfig& cfg) :
    base_pivot_("base_pivot", node, cfg)
{}

std::future<void> RotationControl::set_angle(const double& target_rad)
{
    return base_pivot_.setAngle(target_rad);
}

double RotationControl::get_angle() const
{
    return base_pivot_.getAngle();
}

std::future<void> RotationControl::move_to(const float& obj_x, const float& obj_y)
{
    const double current    = base_pivot_.getAngle();
    const float  target_rad = world_pos_to_setpoint(obj_x, obj_y);

    double diff = target_rad - current;

    // Normaliseer het verschil naar [-π, +π] zodat de arm altijd de kortste
    // kant op draait en nooit onnodig meer dan 180° roteert
    while (diff >  M_PI) diff -= 2.0 * M_PI;
    while (diff < -M_PI) diff += 2.0 * M_PI;

    // Tel het genormaliseerde verschil op bij de huidige positie zodat de
    // PID-regelaar een consistent absoluut doelwit krijgt
    const double target = current + diff;

    std::cout << "[RotationControl] Current: " << current
              << " rad, Target: "              << target_rad
              << " rad, Going to: "            << target << "\n";

    return base_pivot_.setAngle(target);
}