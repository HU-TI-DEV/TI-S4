# Assignment: Devcontainer & Debugger met Moderne Logging en Conditionele Compilatie

In deze opdracht zet je een volledige C++ ontwikkelomgeving op in een devcontainer. De devcontainer moet automatisch alle benodigde tools en dependencies installeren, zodat je een C++ project met meerdere source files kunt bouwen en debuggen. In het project implementeer je een logging functionaliteit met moderne C++ technieken (zonder logging-macros voor de implementatie zelf), en de logger wordt conditioneel aan- of uitgezet via een macro die in de CMakeLists.txt wordt gedefinieerd (bijvoorbeeld ENABLE_LOGGING). Dit stelt je in staat om in debug builds extra informatie te tonen en in release builds de logging uit te schakelen.

---

## Doelstellingen

- **Devcontainer Setup:** Configureer een devcontainer die een complete C++ build environment installeert (met compiler, CMake, debugger, etc.).
- **Multi-Source Build:** Bouw een C++ project met meerdere bronbestanden (bijvoorbeeld `main.cc`, `Logger.cc`, `Logger.hh` en extra bestanden) en laat zien hoe je deze integreert in je `CMakeLists.txt`.
- **Moderne Logging:** Implementeer logging met moderne C++ technieken (bijv. via een Logger class die `std::clog` gebruikt) zonder gebruik te maken van macros voor de logging-logica.
- **Conditionele Compilatie:** Zorg ervoor dat de logging conditioneel wordt in- of uitgeschakeld afhankelijk van de build-configuratie. Definieer in de CMakeLists.txt een macro (bijv. ENABLE_LOGGING) voor debug builds zodat de logger alleen in debug mode actief is.
- **Debugging:** Zorg dat je devcontainer de mogelijkheid biedt om het project te debuggen, zodat je stap voor stap de uitvoering kunt volgen en de log output kunt inspecteren.

---

## Vereisten

1. **Devcontainer Configuratie:**
   - Maak een `.devcontainer` map met daarin een `devcontainer.json` en, indien nodig, een `Dockerfile`.
   - De devcontainer moet automatisch alle benodigde tools installeren (bijv. GCC/Clang, CMake, debugger, etc.).
   - Bij het openen van de devcontainer in VSCode werk je direct in een volledige C++ ontwikkelomgeving.

2. **CMake Build Configuratie:**
   - Zorg voor een `CMakeLists.txt` bestand dat meerdere source files integreert. Voorbeeldbestand:
     - `main.cc`: De entry point van je applicatie.
     - `Logger.cc` en `Logger.hh`: Bevatten de logging functionaliteit.
     - Eventueel extra source files met functies die elkaar aanroepen.
   - **Belangrijk:** Zorg dat je in de CMakeLists.txt conditionele compilatie instelt, bijvoorbeeld:
     ```cmake
     if(CMAKE_BUILD_TYPE STREQUAL "Debug")
         add_compile_definitions(ENABLE_LOGGING)
     endif()
     ```
   - Gebruik eventueel ook de instelling `set(CMAKE_EXPORT_COMPILE_COMMANDS ON)` voor betere VSCode ondersteuning.

3. **C++ Project en Logging:**
   - Bouw een applicatie waarin meerdere source files samenwerken en functies elkaar aanroepen.
   - Implementeer een Logger class op een moderne manier. De logger moet via conditionele compilatie (met behulp van de macro ENABLE_LOGGING) alleen logging uitvoeren in debug builds. Een voorbeeldimplementatie:

**Logger.hh**
```cpp
#pragma once
#include <iostream>
#include <string>

// Logt een bericht als ENABLE_LOGGING is gedefinieerd.
void log(const std::string& message);
```

**main.cc**
```cpp
#include "Logger.hh"
#include <iostream>
#include <string>

int berekenFactorial(int n) {
    log("Start berekenFactorial met n = " << n);
    int result = 1;
    for (int i = 1; i <= n; ++i) {
        result *= i;
        log("Intermediate result at i = " << i << " is " << result);
    }
    log("Eind berekenFactorial met result = " << result);
    return result;
}

int main() {
    std::cout << "Factorial van 5 is " << berekenFactorial(5) << "\n";;
    return 0;
}
```

- Het project moet tijdens de uitvoering logberichten genereren die de volgorde van functie-aanroepen en de tussenresultaten tonen. In release builds (zonder ENABLE_LOGGING) moet deze logging uitgeschakeld zijn.

4. **README.md:**
   - Voeg een duidelijke README toe met instructies over:
     - Hoe je de devcontainer bouwt en runt (bijv. via "Remote-Containers: Reopen in Container" in VSCode).
     - Hoe je de applicatie compileert en welke commando's je kunt gebruiken.
     - Hoe je de applicatie debugt en hoe de logberichten geïnterpreteerd kunnen worden.
     - Uitleg over hoe de conditionele compilatie van de logger is ingesteld (en hoe de macro ENABLE_LOGGING in Debug builds wordt toegevoegd).

## Succescriteria

De opdracht is geslaagd als:

- De devcontainer automatisch alle benodigde tools installeert en een volledige C++ build environment biedt.
- Het project succesvol compileert en de `CMakeLists.txt` meerdere source files correct integreert.
- Via de CMakeLists.txt kan je conditioneel de logging aan/uit zetten.
- Je kunt via de devcontainer de applicatie debuggen en stap-voor-stap de log output volgen en analyseren.

Veel succes en happy debugging!
