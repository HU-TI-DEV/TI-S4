// Oefening 2: pointers en pointer arithmetic
//
// Regels voor deze oefening:
//   - Geen arr[i] gebruiken, alleen *p, p + n, ++p, p != end.
//   - Geen std::vector of std::algorithm: dat mag straks bij de STL-les wel,
//     nu wil je begrijpen wat er onder ligt.
//
// Alle functies werken met een "begin" en "end" pointer, precies zoals de
// iteratoren van de STL: `end` wijst één voorbij het laatste element en
// mag NOOIT gedereferenced worden.

#include <cassert>
#include <iostream>

// 2a. Geef de grootste waarde terug uit [begin, end).
//     Preconditie: begin != end (minimaal één element). Wat doe je als dat
//     niet zo is? Documenteer je keuze.
int findMax(const int* begin, const int* end) {
    // TODO
    return 0;
}

// 2b. Geef een pointer terug naar het eerste element in [begin, end) dat
//     gelijk is aan `value`. Niet gevonden? Geef `end` terug.
//     (Dit is precies wat std::find doet.)
const int* findValue(const int* begin, const int* end, int value) {
    // TODO
    return end;
}

// 2c. Keer de volgorde van [begin, end) om, ter plekke, met twee pointers die
//     naar elkaar toe lopen.
void reverse(int* begin, int* end) {
    // TODO
}

// 2d. Deze functie krijgt een pointer naar const. Waarom compileert de regel
//     met "*begin = 0" niet? Haal hem weg en beantwoord de vraag in commentaar.
int countValue(const int* begin, const int* end, int value) {
    int count = 0;
    for (const int* p = begin; p != end; ++p) {
        // *begin = 0;
        if (*p == value) ++count;
    }
    return count;
}

int main() {
    int data[] = {3, 9, -2, 9, 7};
    const int size = sizeof(data) / sizeof(data[0]);
    int* begin = data;
    int* end = data + size;   // één voorbij het einde: mag je berekenen, niet lezen

    // 2a
    assert(findMax(begin, end) == 9);
    assert(findMax(begin, begin + 1) == 3);

    // 2b
    assert(findValue(begin, end, -2) == begin + 2);
    assert(findValue(begin, end, 9) == begin + 1);     // de eerste 9
    assert(findValue(begin, end, 100) == end);         // niet gevonden

    // 2c
    reverse(begin, end);
    assert(data[0] == 7 && data[1] == 9 && data[2] == -2 && data[3] == 9 && data[4] == 3);
    reverse(begin, end);
    assert(data[0] == 3 && data[4] == 7);

    // 2d
    assert(countValue(begin, end, 9) == 2);

    // Experiment (na afloop, met sanitizers aan): wat gebeurt er als je
    // findMax(begin, end + 1) aanroept? Lees het rapport en verklaar het.

    std::cout << "02_pointers: alles OK\n";
    return 0;
}
