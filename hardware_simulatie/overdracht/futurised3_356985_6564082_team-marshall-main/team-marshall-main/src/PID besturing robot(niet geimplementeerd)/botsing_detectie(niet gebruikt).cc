#include <iostream>
#include <gz/msgs.hh>
#include <gz/transport.hh>
#include <termios.h>
#include <unistd.h>
#include <sys/select.h> 
#include <cmath>        

// Globale variabelen
gz::transport::Node::Publisher pub;
double kortste_afstand_voor = 999.0; 

// --- Terminal-toetsenlezer Hulpfuncties ---
bool kbhit() {
    struct timeval tv = {0L, 0L};
    fd_set fds;
    FD_ZERO(&fds);
    FD_SET(0, &fds);
    return select(1, &fds, NULL, NULL, &tv) > 0;
}

void setRawMode(bool enable) {
    static struct termios oldt, newt;
    if (enable) {
        tcgetattr(STDIN_FILENO, &oldt);
        newt = oldt;
        newt.c_lflag &= ~(ICANON | ECHO);
        tcsetattr(STDIN_FILENO, TCSANOW, &newt);
    } else {
        tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
    }
}

void lidarCallback(const gz::msgs::LaserScan &_msg) {
    int num_samples = _msg.ranges_size();
    double min_dist = 999.0;

    for (int i = num_samples * 0.4; i < num_samples * 0.6; ++i) {
        double dist = _msg.ranges(i);
        if (dist > 0.05 && dist < min_dist) {
            min_dist = dist;
        }
    }
    kortste_afstand_voor = min_dist;
}

int main() {
    gz::transport::Node node;
    pub = node.Advertise<gz::msgs::Twist>("/cmd_vel");
    node.Subscribe("/lidar", lidarCallback);

    setRawMode(true);

    std::cout << "====================================================\n";
    std::cout << " WASD BESTURING MET PROGRESSIEF REMMEN & NOODSTOP\n";
    std::cout << " Besturing: W/S (Snelheid), A/D (Sturen), SPATIE (Rem), Q (Stop)\n";
    std::cout << " Veiligheid: Robot remt hard af als een object binnen 1.0m komt!\n";
    std::cout << "====================================================\n\n";

    // Wat de gebruiker wil (Doelsnelheid)
    double target_linear = 0.0;
    double target_angular = 0.0;

    // Wat de robot daadwerkelijk rijdt op dit moment (Actuele snelheid)
    double current_linear = 0.0;
    double current_angular = 0.0;

    // Instellingen voor optrekken en sturen
    const double ACCELERATIE_STAP_LINEAIR = 0.5; 
    const double ACCELERATIE_STAP_ANGULAR = 0.75;

    // Instellingen voor het progressieve remmen
    double actuele_remkracht = 0.05; // Start zachtjes met remmen
    const double REM_TOENAME = 0.10; // Hoeveel de remkracht elke 50ms toeneemt (hoe hoger, hoe sneller hij maximaal remt)

    bool noodstop_actief = false;

    while (true) {
        if (kbhit()) {
            char c;
            if (read(STDIN_FILENO, &c, 1) > 0) {
                switch (c) {
                    case 'w': case 'W': target_linear += 2.5; break; 
                    case 's': case 'S': target_linear -= 2.5; break; 
                    case 'a': case 'A': target_angular += 1.5; break; 
                    case 'd': case 'D': target_angular -= 1.5; break; 
                    case ' ':           target_linear = 0.0; target_angular = 0.0; break; 
                    case 'q': case 'Q': 
                        {
                            gz::msgs::Twist stop_msg;
                            stop_msg.mutable_linear()->set_x(0.0);
                            stop_msg.mutable_angular()->set_z(0.0);
                            pub.Publish(stop_msg);
                        }
                        setRawMode(false);
                        std::cout << "\n\nProgramma gestopt door gebruiker.\n";
                        return 0;
                }
            }
        }

        // 1. Automatische Noodstop Controle
        // Activeer de doelsnelheid van 0.0 als we te dichtbij komen, zodat het progressieve remmen start
        if (kortste_afstand_voor <= 1.0) {
            if (target_linear > 0.0 || current_linear > 0.0) {
                target_linear = 0.0;
                noodstop_actief = true;
            }
        } else {
            noodstop_actief = false;
        }

        // Grenzen voor de doelsnelheid
        if (target_linear > 2.5)  target_linear = 2.5;
        if (target_linear < -2.5) target_linear = -2.5;
        if (target_angular > 1.5) target_angular = 1.5;
        if (target_angular < -1.5) target_angular = -1.5;

        // 2. Lineaire Snelheidsopbouw & Progressief Remmen
        bool is_aan_het_remmen = (target_linear == 0.0 && current_linear != 0.0);

        if (is_aan_het_remmen) {
            // Remkracht bouwt zich op: steeds harder remmen
            actuele_remkracht += REM_TOENAME; 

            if (current_linear > 0.0) {
                current_linear -= actuele_remkracht;
                if (current_linear < 0.0) current_linear = 0.0; // Voorkom dat hij achteruit schiet
            } else if (current_linear < 0.0) {
                current_linear += actuele_remkracht;
                if (current_linear > 0.0) current_linear = 0.0;
            }
        } else {
            // Reset de remkracht als we gas geven of op doelsnelheid zijn
            actuele_remkracht = 0.05; 

            // Normaal optrekken naar de doelsnelheid
            if (current_linear < target_linear) {
                current_linear += ACCELERATIE_STAP_LINEAIR;
                if (current_linear > target_linear) current_linear = target_linear;
            } else if (current_linear > target_linear) {
                current_linear -= ACCELERATIE_STAP_LINEAIR;
                if (current_linear < target_linear) current_linear = target_linear;
            }
        }

        // 3. Draaisnelheid (Links/Rechts) netjes opbouwen en afbouwen
        if (current_angular < target_angular) {
            current_angular += ACCELERATIE_STAP_ANGULAR;
            if (current_angular > target_angular) current_angular = target_angular;
        } else if (current_angular > target_angular) {
            current_angular -= ACCELERATIE_STAP_ANGULAR; 
            if (current_angular < target_angular) current_angular = target_angular;
        }

        // Verzenden naar Gazebo
        gz::msgs::Twist message;
        message.mutable_linear()->set_x(current_linear);
        message.mutable_angular()->set_z(current_angular);
        pub.Publish(message);

        // Status weergave
        if (noodstop_actief) {
            std::cout << "\r[!!! NOODSTOP !!!] Remt af voor object: " << kortste_afstand_voor << "m (Achteruitrijden S kan wel)    " << std::flush;
        } else {
            std::cout << "\r[Status] Doel L: " << target_linear 
                      << " | Actueel L: " << current_linear 
                      << " | Afstand: " << kortste_afstand_voor << "m    " << std::flush;
        }

        usleep(50000); // 20Hz loop
    }

    setRawMode(false);
    return 0;
}