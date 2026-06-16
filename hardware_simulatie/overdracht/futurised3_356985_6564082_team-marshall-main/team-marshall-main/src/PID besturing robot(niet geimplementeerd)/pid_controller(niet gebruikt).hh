#pragma once

#include <algorithm>
#include <chrono>

class PIDController {
public:
    // De 'Constructor': hiermee stel je de gevoeligheid (Kp, Ki, Kd) en de grens van de I-terrm in.
    PIDController(double kp, double ki, double kd, double integralLimit)
        : kp_(kp), ki_(ki), kd_(kd), integralLimit_(integralLimit) {}

    // Reset de geschiedenis van de controller (handig als de robot een tijdje heeft stilgestaan)
    void reset() {
        integral_ = 0.0;
        previousError_ = 0.0;
        initialized_ = false;
    }

    // De belangrijkste functie: bereken de nieuwe sturing op basis van de 'fout' (error)
    double update(double error) {
        const auto now = std::chrono::steady_clock::now();

        // De allereerste keer dat we dit aanroepen, kunnen we nog geen snelheidsverandering (D) berekenen
        if (!initialized_) {
            initialized_ = true;
            lastUpdate_ = now;
            previousError_ = error;
            return kp_ * error; // Geef alleen de P-actie terug
        }

        // Bereken hoeveel tijd (dt) er is verstreken sinds de vorige meting (in seconden)
        const double dt = std::chrono::duration<double>(now - lastUpdate_).count();
        lastUpdate_ = now;
        
        // Als de tijd stilstond, hergebruiken we de basisfunctie om gekke sprongen te voorkomen
        if (dt <= 0.0) {
            return kp_ * error;
        }

        // 1. De P-term (Proportioneel): Reageert op de fout van NU. (kp_ * error)
        
        // 2. De I-term (Integraal): Kijkt naar het VERLEDEN. Tel de fouten over de tijd bij elkaar op.
        // 'std::clamp' zorgt ervoor dat dit getal niet oneindig groot wordt (anti-windup).
        integral_ = std::clamp(integral_ + error * dt, -integralLimit_, integralLimit_);

        // 3. De D-term (Afgeleide): Kijkt naar de TOEKOMST. Hoe snel verandert de fout?
        const double derivative = (error - previousError_) / dt;
        previousError_ = error;

        // Tel P, I en D bij elkaar op voor het uiteindelijke motorcommando!
        return (kp_ * error) + (ki_ * integral_) + (kd_ * derivative);
    }

private:
    double kp_;                 // Factor voor de huidige fout
    double ki_;                 // Factor voor opgestapelde fouten
    double kd_;                 // Factor voor de veranderingssnelheid
    double integralLimit_;      // Maximale grens voor de I-term
    double integral_ = 0.0;     // De opgestapelde fout
    double previousError_ = 0.0;// De fout van de vorige meting
    bool initialized_ = false;  // Houdt bij of de eerste meting al is gedaan
    std::chrono::steady_clock::time_point lastUpdate_; // Tijdstip van de vorige meting
};