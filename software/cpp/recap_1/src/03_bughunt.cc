// Oefening 3: bug hunt
//
// Dit programma compileert en lijkt misschien zelfs te werken. Toch zitten er
// ACHT bugs in: geheugenfouten, dangling pointers/references en undefined
// behaviour. Elke functie bevat er precies één.
//
// Werkwijze:
//   1. Bouw in Debug met sanitizers aan (staat al zo in CMakeLists.txt).
//   2. Lees eerst de compiler-WARNINGS. Sommige bugs staan daar al in.
//   3. Draai het programma. Een sanitizer stopt bij de EERSTE fout die hij
//      tegenkomt en print een rapport: wat, waar, en waar het geheugen is
//      aangemaakt/vrijgegeven.
//   4. Fix die ene bug, bouw, draai opnieuw. Herhaal.
//   5. Sommige bugs geven geen rapport, alleen een verkeerde uitkomst. Vergelijk
//      de uitvoer met de verwachte waarden in main(). Gebruik de debugger.
//
// Noteer per bug: het symptoom, welk gereedschap hem vond (warning, ASan,
// UBSan, debugger, je eigen ogen) en de fix. Dat is je inleverwerk.

#include <climits>
#include <iostream>
#include <string>
#include <vector>

struct Sensor {
    std::string name;
    double value;
};

// Gemiddelde van een reeks metingen.
double berekenGemiddelde(const std::vector<int>& getallen) {
    int som = 0;
    for (size_t i = 0; i <= getallen.size(); ++i) {
        som += getallen[i];
    }
    return static_cast<double>(som) / static_cast<double>(getallen.size());
}

// Grootste meting.
const int& largest(const std::vector<int>& values) {
    int best = values[0];
    for (int v : values) {
        if (v > best) best = v;
    }
    return best;
}

// Som van de kwadraten 0² + 1² + ... + (n-1)².
int sumOfSquares(int n) {
    int* squares = new int[n];
    for (int i = 0; i < n; ++i) {
        squares[i] = i * i;
    }
    int total = 0;
    for (int i = 0; i < n; ++i) {
        total += squares[i];
    }
    return total;
}

// Plak woorden aan elkaar met een spatie ertussen.
std::string joinWords(const std::vector<std::string>& words) {
    std::string* copies = new std::string[words.size()];
    for (size_t i = 0; i < words.size(); ++i) {
        copies[i] = words[i];
    }
    std::string result;
    for (size_t i = 0; i < words.size(); ++i) {
        if (i > 0) result += ' ';
        result += copies[i];
    }
    delete copies;
    return result;
}

// Maak een tijdelijke sensor, lees hem uit en ruim hem op.
double readTemporarySensor() {
    Sensor* s = new Sensor{"tijdelijk", 21.5};
    delete s;
    return s->value;
}

// Eerste plus laatste meting, nadat er een extra meting is toegevoegd.
int firstPlusNewLast(std::vector<int> values) {
    int& first = values[0];
    values.push_back(100);
    return first + values.back();
}

// Zoek een sensor op naam. Niet gevonden: nullptr.
const Sensor* findSensor(const std::vector<Sensor>& sensors, const std::string& name) {
    for (const Sensor& s : sensors) {
        if (s.name == name) return &s;
    }
    return nullptr;
}

// Waarde van een sensor op naam.
double valueOf(const std::vector<Sensor>& sensors, const std::string& name) {
    return findSensor(sensors, name)->value;
}

// Eenvoudige checksum: alles bij elkaar optellen.
int checksum(const std::vector<int>& data) {
    int total = 0;
    for (int d : data) {
        total += d;
    }
    return total;
}

int main() {
    std::vector<int> metingen = {4, 8, 15, 16, 23, 42};

    std::cout << "gemiddelde:       " << berekenGemiddelde(metingen) << "   (verwacht 18)\n";
    std::cout << "largest:          " << largest(metingen) << "   (verwacht 42)\n";
    std::cout << "sumOfSquares:     " << sumOfSquares(4) << "   (verwacht 14)\n";
    std::cout << "joinWords:        " << joinWords({"pointers", "zijn", "leuk"}) << "   (verwacht: pointers zijn leuk)\n";
    std::cout << "temporary sensor: " << readTemporarySensor() << "   (verwacht 21.5)\n";
    std::cout << "first + new last: " << firstPlusNewLast(metingen) << "   (verwacht 104)\n";

    std::vector<Sensor> sensors = {{"temperatuur", 21.5}, {"druk", 1013.0}};
    std::cout << "valueOf(druk):    " << valueOf(sensors, "druk") << "   (verwacht 1013)\n";
    std::cout << "valueOf(licht):   " << valueOf(sensors, "licht") << "   (verwacht: nette foutafhandeling)\n";

    std::vector<int> groot = {INT_MAX, 1};
    std::cout << "checksum:         " << checksum(groot) << "   (verwacht: geen overflow)\n";

    std::cout << "03_bughunt: klaar\n";
    return 0;
}
