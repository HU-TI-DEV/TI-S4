# VSCode C++ Setup

In deze handleiding vind je een stap-voor-stap uitleg om je
ontwikkelomgeving in te richten voor C++ met VSCode en Docker. We
behandelen de installatie van VSCode, Docker, en alle benodigde
tools en extensies (CMake, Git, compilers) en leggen uit hoe je een
devcontainer gebruikt. Dit omvat de juiste CMake-instellingen voor
optimale autocomplete (zoals het genereren van
`compile_commands.json`) en het installeren van de tools binnen de
container.
---

## 1. Installatie van Visual Studio Code (VSCode)

**Wat is het?**
VSCode is een krachtige, lichtgewicht code-editor die ondersteuning
biedt voor debugging, code-completion, en integratie met diverse
tools.

**Waarom?**
Een goede editor verbetert je workflow met handige features zoals
autocomplete, debugging integratie en aanpasbaarheid naar
persoonlijke voorkeuren.

**Hoe te installeren:**

- Ga naar de [officiële website van VSCode](https://code.visualstudio.com/) en download de versie die bij jouw besturingssysteem past (Windows, macOS of Linux).
- Volg de installatie-instructies.

**Meer informatie:**

- [VSCode Documentation](https://code.visualstudio.com/docs)

---

## 2. Installatie van Docker

**Wat is het?**
Docker is een platform waarmee je applicaties in containers kunt draaien. Dit zorgt voor een consistente en geïsoleerde ontwikkel- en runtimeomgeving.

**Waarom?**
Containers helpen je om afhankelijkheden en omgevingen te standaardiseren, wat vooral handig is bij C++ projecten waar libraries en toolversies cruciaal kunnen zijn.

**Hoe te installeren:**

- Bezoek de [Docker Get Started pagina](https://www.docker.com/get-started) en download de versie voor jouw OS.
- Volg de installatie-instructies.
- Controleer de installatie via de terminal:

  ```bash
  docker --version
  ```

**Meer informatie:**

- [Docker Documentation](https://docs.docker.com/get-started/overview/)

---

## 3. Installatie van Benodigde Tools: CMake, Git en Compilers

### CMake

**Wat is het?**
CMake is een build-systeem generator dat helpt bij het configureren en bouwen van je C++ projecten.

**Waarom?**
Het zorgt voor een platformonafhankelijke manier om build processen te beheren en is een van de meest gebruikte build systemen voor C++.

**Hoe te installeren:**

- Download de installer via de [CMake website](https://cmake.org/download/) of installeer via je package manager (bijv. `sudo apt-get install cmake` op Ubuntu).
- Controleer de installatie:

  ```bash
  cmake --version
  ```

**Meer informatie:**

- [CMake Getting Started](https://cmake.org/cmake/help/latest/guide/tutorial/index.html)

### Git

**Wat is het?**
Git is een versiebeheersysteem waarmee je de geschiedenis van je code kunt beheren.

**Waarom?**
Het helpt bij samenwerking en houdt wijzigingen in je code bij, zodat je gemakkelijk terug kunt naar een vorige versie indien nodig.

**Hoe te installeren:**

- Download Git van de [officiële Git website](https://git-scm.com/downloads) of installeer via je package manager.
- Controleer de installatie:

  ```bash
  git --version
  ```

**Meer informatie:**

- [Git Documentation](https://git-scm.com/doc)

### Compilers (GCC/Clang/MSVC)

**Wat is het?**
Compilers zoals GCC, Clang of MSVC zetten je C++ code om in uitvoerbare bestanden.

**Waarom?**
Zonder een compiler kun je je code niet bouwen of uitvoeren. De keuze voor een compiler hangt vaak af van je platform en persoonlijke voorkeur.

**Hoe te installeren:**

- **Op Windows:**
  - Installeer [MinGW](http://www.mingw.org/) of de [Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/).
- **Op macOS:**
  - Installeer Xcode Command Line Tools:

    ```bash
    xcode-select --install
    ```

- **Op Linux:**
  - Installeer GCC/Clang via je package manager:

    ```bash
    sudo apt-get install build-essential
    ```

- Controleer de installatie:

  ```bash
  g++ --version
  ```

**Meer informatie:**

- [GCC Documentation](https://gcc.gnu.org/onlinedocs/)
- [Clang Documentation](https://clang.llvm.org/docs/)

---

## 4. Installatie van VSCode Extensies

**Wat is het?**
Extensies voegen extra functionaliteit toe aan VSCode, omdat de
editor standaard niet veel ondersteuning biedt voor specifieke
programmeertalen. Deze ondersteuning kun je toevoegen met
extensies.

**Waarom?**
Ze zorgen voor betere code-completion, debugging en integratie met tools als CMake en Docker, en maken het werken in een devcontainer mogelijk.

**Welke extensies?**

- **C/C++ (van Microsoft):**
  Voor IntelliSense, debugging en linting.
- **CMake Tools:**
  Voor integratie met CMake, configuratie en bouwen van je project.
- **Docker:**
  Voor het beheren en werken met Docker containers.
- **Remote - Containers:**
  Voor het werken met VSCode in een Docker/devcontainer omgeving.

**Hoe te installeren:**

- Open VSCode en klik op de Extensions tab (`Ctrl+Shift+X`).
- Zoek naar de bovengenoemde extensies en klik op 'Install'.
- Herstart VSCode indien nodig.

**Meer informatie:**

- [C/C++ Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cpptools)
- [CMake Tools Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode.cmake-tools)
- [Docker Extension](https://marketplace.visualstudio.com/items?itemName=ms-azuretools.vscode-docker)
- [Remote - Containers Extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)

---

## 5. Werken met Devcontainers

**Wat is een Devcontainer?**
Een devcontainer is een Docker container die speciaal is ingericht
als ontwikkelomgeving. Hiermee kun je een consistente omgeving
creëren voor al je projecten, inclusief alle benodigde tools en
dependencies.

**Waarom?**

- Zorgt voor een identieke setup voor alle teamleden.
- Voorkomt "it works on my machine" problemen.
- Eenvoudig te reproduceren en te delen.

**Hoe te gebruiken:**

- Met de **Remote - Containers** extensie in VSCode kun je direct vanuit de editor een devcontainer openen.
- Je kunt de "Dev Container: New C++ Project" template gebruiken om snel een nieuwe omgeving op te zetten.
- In de devcontainer worden alle tools (CMake, Git, compilers) automatisch geïnstalleerd via de Dockerfile en `devcontainer.json`.
- Zorg er wel voor dat je weet hoe deze tools geïnstalleerd worden in een Docker omgeving, zodat je ze eventueel kunt aanpassen of uitbreiden.

**Meer informatie:**

- [VSCode Remote - Containers Documentation](https://code.visualstudio.com/docs/remote/containers)
- [Dev Container Spec](https://containers.dev/)

---

## 6. Configuratie van een CMake Project voor Optimale Autocomplete

**Wat is het?**
Het genereren van een `compile_commands.json` bestand via CMake, dat alle compileeropties bevat.

**Waarom?**
Dit bestand is cruciaal voor de C/C++ extensie in VSCode om accurate code-completion, linting en navigatie te bieden.

**Hoe te configureren:**

1. **CMakeLists.txt aanpassen:**
   - Open of maak het `CMakeLists.txt` bestand in de root van je project.
   - Voeg de volgende regel toe om het `compile_commands.json` bestand te genereren:

     ```cmake
     set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
     ```

   - Hierdoor maakt CMake bij het configureren van het project automatisch een bestand met compileercommando's aan.

2. **Project configureren en bouwen:**
   - Open een terminal in je projectmap en voer de volgende commando's uit:

     ```bash
     mkdir build && cd build
     cmake ..
     ```

   - Het `compile_commands.json` bestand wordt hierdoor aangemaakt in de `build` map.

3. **VSCode configureren:**
   - Open de Command Palette in VSCode (`Ctrl+Shift+P`) en zoek naar `C/C++: Edit Configurations (UI)`.
   - Stel bij "Compile Commands" het pad in naar jouw `build/compile_commands.json` bestand.

**Meer informatie:**

- [CMake: CMAKE_EXPORT_COMPILE_COMMANDS](https://cmake.org/cmake/help/latest/variable/CMAKE_EXPORT_COMPILE_COMMANDS.html)

---

## 7. Samenvatting en Verdere documentatie

Je hebt nu een volledige ontwikkelomgeving ingesteld met VSCode,
Docker en alle benodigde tools voor een professioneel C++ project.
Met de toevoeging van devcontainers kun je bovendien een
consistente en deelbare ontwikkelomgeving creëren. Deze setup zorgt
voor een gestroomlijnde workflow met debugging, autocomplete en een
betrouwbare build-infrastructuur.

**Verder lezen:**

- [VSCode Documentatie](https://code.visualstudio.com/docs)
- [CMake Tutorial](https://cmake.org/cmake/help/latest/guide/tutorial/index.html)
- [Docker Documentatie](https://docs.docker.com/get-started/overview/)
- [VSCode Remote - Containers](https://code.visualstudio.com/docs/remote/containers)
