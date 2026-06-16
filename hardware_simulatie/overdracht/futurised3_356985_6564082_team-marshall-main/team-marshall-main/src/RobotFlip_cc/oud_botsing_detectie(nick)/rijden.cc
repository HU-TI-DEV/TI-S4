#include <iostream>
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
const double LIMIT_FRONT = 1.3; 
const double LIMIT_REAR = 2.0; 

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

    for (int i = 0; i < num_samples; ++i) {
        double dist = _msg.ranges(i);
        
        // Negeer ruis of te verre data
        if (dist < 0.05) continue; 

        // SECTOR VOOR: Midden van de array (ca. index 400 t/m 600)
        if (i > num_samples * 0.4 && i < num_samples * 0.6) {
            if (dist < LIMIT_FRONT) danger_front = true;
        } 
        
        // SECTOR ACHTER: Begin en eind van de array (0-150 en 850-1000)
        else if (i < num_samples * 0.15 || i > num_samples * 0.85) {
            if (dist < LIMIT_REAR) danger_rear = true;
        }
    }

    front_blocked = danger_front;
    rear_blocked = danger_rear;

    // NOODSTOP LOGICA
     if ((currentState == RobotState::MOVING_FORWARD && front_blocked) ||
        (currentState == RobotState::MOVING_BACKWARD && rear_blocked)) {
        
        gz::msgs::Twist msg;
        
        // Bepaal de remrichting: 
        // Als we vooruit gaan -> ram op de achteruit (-16)
        // Als we achteruit gaan -> ram op de vooruit (16)
        double brakeForce = (currentState == RobotState::MOVING_FORWARD) ? -16.0 : 16.0;
        
        
        msg.mutable_linear()->set_x(brakeForce);
        pub.Publish(msg);

        
        msg.mutable_linear()->set_x(0.0);
        msg.mutable_angular()->set_z(0.0);
        pub.Publish(msg);

        currentState = RobotState::IDLE;
        std::cout << "\r[SYSTEEM] Noodstop actief! (Kracht: " << brakeForce << ")          " << std::flush;
    }
}


int main() {
    gz::transport::Node node;
    pub = node.Advertise<gz::msgs::Twist>("/cmd_vel");
    
   
    if (!node.Subscribe("/lidar", lidarCallback)) {
        std::cerr << "Fout bij abonneren op /lidar" << std::endl;
        return -1;
    }

    std::cout << "Limiet VOOR: " << LIMIT_FRONT << "m | Limiet ACHTER: " << LIMIT_REAR << "m\n";
    std::cout << "W: Vooruit, S: Achteruit, A/D: Draaien, Spatie: Stop, Q: Quit\n";

    while (true) {
        char keyInput = getKey(); 
        gz::msgs::Twist message;

        double linVel = 2.6; 
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