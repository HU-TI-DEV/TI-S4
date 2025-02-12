#include <iostream>

int main() {
    int a = 5;
    int b = 0;
    // Zet hier een breakpoint
    int c = a / b; // Fout: deling door nul
    std::cout << "Result: " << c << "\n";
    return 0;
}
 