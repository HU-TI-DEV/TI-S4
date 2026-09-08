// Oefening 1: functies, by value en by reference
//
// Implementeer de functies hieronder. main() controleert je werk met asserts:
// het programma stopt met "Assertion failed" zolang iets niet klopt.
// Klaar = het programma draait door tot "01_functies: alles OK".

#include <cassert>
#include <iostream>

// 1a. Geef `min` terug als value < min, `max` als value > max, anders `value`.
int clamp(int value, int min, int max) {
    // TODO
    return value;
}

// 1b. Verwissel a en b via references.
void swapValues(int& a, int& b) {
    // TODO
}

// 1c. Verwissel de waarden waar a en b naar wijzen, via pointers.
//     Wat doe je als een van de twee nullptr is? Kies iets en documenteer het.
void swapPointers(int* a, int* b) {
    // TODO
}

// 1d. Deze functie is fout, maar compileert prima. Laat hem staan.
//     Vraag: waarom verandert er niets aan de argumenten van de aanroeper?
void swapBroken(int a, int b) {
    int t = a;
    a = b;
    b = t;
}

int main() {
    // 1a
    assert(clamp(5, 0, 10) == 5);
    assert(clamp(-3, 0, 10) == 0);
    assert(clamp(42, 0, 10) == 10);
    assert(clamp(0, 0, 10) == 0);
    assert(clamp(10, 0, 10) == 10);

    // 1b
    int x = 1;
    int y = 2;
    swapValues(x, y);
    assert(x == 2 && y == 1);

    // 1c
    swapPointers(&x, &y);
    assert(x == 1 && y == 2);

    // 1d: waarom slaagt deze assert? Schrijf het antwoord als commentaar hieronder.
    swapBroken(x, y);
    assert(x == 1 && y == 2);
    // Antwoord:

    std::cout << "01_functies: alles OK\n";
    return 0;
}
