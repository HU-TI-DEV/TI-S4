#include <iostream>
#include <string>
#include <gz/msgs.hh>
#include <gz/transport.hh>
#include <termios.h>
#include <unistd.h>
#include <vector>

// Enum voor de verschillende statussen van de robot
enum class RobotState {
    IDLE,
    MOVING_FORWARD,
    MOVING_BACKWARD,
    TURNING
};

// Globale variabelen
gz::transport::Node::Publisher pub;
RobotState currentState = RobotState::IDLE;

// Obstakel vlaggen
bool front_blocked = false;
bool rear_blocked = false;

// Marges
const double LIMIT_FRONT = 1.0; 
const double LIMIT_REAR = 3.0;  

// getkey functie
char getKey() {
    char buf = 0;
    struct termios old = {0};
    if (tcgetattr(0, &old) < 0) perror("tcsetattr()");
    old.c_lflag &= ~ICANON;
    old.c_lflag &= ~ECHO; 
    old.c_cc[VMIN] = 1;
    old.c_cc[VTIME] = 0;
    if (tcsetattr(0, TCSANOW, &old) < 0) perror("tcsetattr ICANON");
    if (read(0, &buf, 1) < 0) perror("read()");
    old.c_lflag |= ICANON;
    old.c_lflag |= ECHO;
    if (tcsetattr(0, TCSADRAIN, &old) < 0) perror("tcsetattr ~ICANON");
    return buf;
}

void lidarCallback(const gz::msgs::LaserScan &_msg) {
    int num_samples = _msg.ranges_size();
    bool danger_front = false;
    bool danger_rear = false;
    double front_min = 999.0;   // dichtstbijzijnde afstand in de voor-sector
    double rear_min  = 999.0;   // dichtstbijzijnde afstand in de achter-sector

    for (int i = 0; i < num_samples; ++i) {
        double dist = _msg.ranges(i);

        // Negeer ruis of te verre data
        if (dist < 0.05) continue;

        // SECTOR VOOR: Midden van de array (ca. index 400 t/m 600)
        if (i > num_samples * 0.4 && i < num_samples * 0.6) {
            if (dist < front_min) front_min = dist;
            if (dist < LIMIT_FRONT) danger_front = true;
        }

        // SECTOR ACHTER: Begin en eind van de array (0-150 en 850-1000)
        else if (i < num_samples * 0.15 || i > num_samples * 0.85) {
            if (dist < rear_min) rear_min = dist;
            if (dist < LIMIT_REAR) danger_rear = true;
        }
    }

    front_blocked = danger_front;
    rear_blocked = danger_rear;

    // HEARTBEAT: print elke ~2s de gemeten afstanden, zodat je ziet dat de
    // detectie leeft en wat hij meet (ook als er niet geremd hoeft te worden).
    static int hb = 0;
    if (++hb % 20 == 0) {
        std::cout << "[status] lidar  voor=" << front_min << "m  achter=" << rear_min
                  << "m   (rem voor<" << LIMIT_FRONT << "m, achter<" << LIMIT_REAR << "m)"
                  << std::endl;
    }

    // Debug: meld alleen wanneer de detectie VERANDERT (niet elke scan spammen).
    static bool prev_front = false;
    static bool prev_rear = false;
    if (front_blocked != prev_front) {
        std::cout << (front_blocked
            ? ">> LIDAR: obstakel VOOR gedetecteerd (< 1.0m)"
            : "   LIDAR: voor weer vrij") << std::endl;
        prev_front = front_blocked;
    }
    if (rear_blocked != prev_rear) {
        std::cout << (rear_blocked
            ? ">> LIDAR: obstakel ACHTER gedetecteerd"
            : "   LIDAR: achter weer vrij") << std::endl;
        prev_rear = rear_blocked;
    }

    // NOODSTOP LOGICA: Als we een richting opgaan die geblokkeerd is
    if ((currentState == RobotState::MOVING_FORWARD && front_blocked) ||
        (currentState == RobotState::MOVING_BACKWARD && rear_blocked)) {

        gz::msgs::Twist stop_msg;
        stop_msg.mutable_linear()->set_x(0);
        stop_msg.mutable_angular()->set_z(0);
        pub.Publish(stop_msg);
    }
}

// VEILIGHEIDSFILTER: laat de pathfinding-snelheid (/cmd_vel_nav) door naar
// /cmd_vel, maar REM de lineaire beweging af als de lidar een obstakel ziet in
// de richting waarin de robot wil rijden. Draaien blijft altijd toegestaan,
// zodat de pathfinding nog om het obstakel heen kan sturen.
void cmdVelNavCallback(const gz::msgs::Twist &_msg) {
    static bool was_braking = false;
    double lin = _msg.linear().x();
    double ang = _msg.angular().z();

    gz::msgs::Twist out;
    out.mutable_angular()->set_z(ang);   // draaien altijd doorlaten

    bool braking = false;
    if (lin > 0.0 && front_blocked) {
        out.mutable_linear()->set_x(0.0);            // rem: niet vooruit het blok in
        braking = true;
    } else if (lin < 0.0 && rear_blocked) {
        out.mutable_linear()->set_x(0.0);            // rem: niet achteruit het blok in
        braking = true;
    } else {
        out.mutable_linear()->set_x(lin);            // vrij baan → pathfinding-snelheid
    }

    // Debug: meld het begin en einde van een noodstop (niet elke 0.1s spammen).
    if (braking && !was_braking) {
        std::cout << "########## NOODSTOP: botsingdetectie REMT de pathfinding af! "
                     "##########" << std::endl;
    } else if (!braking && was_braking) {
        std::cout << "---------- Vrij baan: pathfinding rijdt weer door. "
                     "----------" << std::endl;
    }
    was_braking = braking;

    pub.Publish(out);
}

// --- MAIN ---
// Standaard: pure veiligheidsfilter (samen met de pathfinding).
// Start met argument "--teleop" voor handmatige keyboard-besturing.
int main(int argc, char** argv) {
    bool teleop = (argc > 1 && std::string(argv[1]) == "--teleop");

    gz::transport::Node node;
    pub = node.Advertise<gz::msgs::Twist>("/cmd_vel");
    
    // Abonneer op het LiDAR topic
    if (!node.Subscribe("/lidar", lidarCallback)) {
        std::cerr << "Fout bij abonneren op /lidar" << std::endl;
        return -1;
    }

    // Abonneer op de gewenste snelheid van de pathfinding (via de ROS-bridge).
    if (!node.Subscribe("/cmd_vel_nav", cmdVelNavCallback)) {
        std::cerr << "Fout bij abonneren op /cmd_vel_nav" << std::endl;
        return -1;
    }

    std::cout << "Limiet VOOR: " << LIMIT_FRONT << "m | Limiet ACHTER: " << LIMIT_REAR << "m\n";

    // Standaard → draai als pure veiligheidsfilter:
    // /cmd_vel_nav -> (rem indien nodig) -> /cmd_vel.
    if (!teleop) {
        std::cout << "Veiligheidsfilter actief: pathfinding rijdt, ik rem bij obstakels."
                  << std::endl;
        gz::transport::waitForShutdown();
        return 0;
    }

    // Met --teleop → handmatige keyboard-besturing (overschrijft de filter).
    std::cout << "W: Vooruit, S: Achteruit, A/D: Draaien, Spatie: Stop, Q: Quit" << std::endl;

    while (true) {
        char keyInput = getKey(); 
        gz::msgs::Twist message;

        double linVel = 1.5; 
        double angVel = 1.0;

        if (keyInput == 'w') {
            if (!front_blocked) {
                currentState = RobotState::MOVING_FORWARD;
                message.mutable_linear()->set_x(linVel);
            } else {
                std::cout << "\r[BEVEILIGING] Kan niet vooruit!     " << std::flush;
                currentState = RobotState::IDLE;
            }
        } 
        else if (keyInput == 's') {
            if (!rear_blocked) {
                currentState = RobotState::MOVING_BACKWARD;
                message.mutable_linear()->set_x(-linVel);
            } else {
                std::cout << "\r[BEVEILIGING] Kan niet achteruit!    " << std::flush;
                currentState = RobotState::IDLE;
            }
        } 
        else if (keyInput == 'a') {
            currentState = RobotState::TURNING;
            message.mutable_angular()->set_z(angVel);
        } 
        else if (keyInput == 'd') {
            currentState = RobotState::TURNING;
            message.mutable_angular()->set_z(-angVel);
        } 
        else if (keyInput == ' ') {
            currentState = RobotState::IDLE;
            message.mutable_linear()->set_x(0);
            message.mutable_angular()->set_z(0);
        } 
        else if (keyInput == 'q') {
            break;
        }

        pub.Publish(message);
    }
    
    return 0;
}