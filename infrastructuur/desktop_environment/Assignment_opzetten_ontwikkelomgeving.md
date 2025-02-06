# Assignment: Ontwikkelomgeving met Docker en Git

In deze opdracht zet je een volledige ontwikkelomgeving op voor C++
binnen een Docker container en plaats je deze op een Git repository
(bijv. GitHub). De opdracht is geslaagd wanneer, na het uitvoeren
van `docker run`, de container een C++ applicatie start die "Hello
world" naar de commandline print.

---

## Doelstellingen

- **Docker Setup:** Leer hoe je een Docker container configureert als ontwikkelomgeving voor C++.
- **Git Repository:** Zorg dat je project volledig versiebeheer heeft.
- **CMake Project:** Bouw een eenvoudig C++ project met een CMakeLists.txt configuratie.
- **Automatische Build:** Configureer de Dockerfile zodat de container bij het opstarten de applicatie bouwt en uitvoert.

---

## Opdrachtvereisten

1. **Git Repository:**
   - Maak een nieuwe repository op GitHub (of een ander Git-platform).
   - Zorg dat alle projectbestanden gecommit en gepusht worden.

2. **Docker Setup:**
   - **Dockerfile:** Creëer een Dockerfile in de root van je repository.
   - De Dockerfile moet een geschikte Linux basisimage gebruiken (bijv. Ubuntu) en de volgende stappen bevatten:
     - Installatie van alle benodigde tools voor C++ ontwikkeling (zoals een compiler, CMake, build-essential, etc.).
     - Kopiëren van de projectbestanden in de container.
     - Configureren en bouwen van je C++ project via CMake.
     - Definiëren van een `ENTRYPOINT` of `CMD` zodat, bij het uitvoeren van `docker run`, de applicatie automatisch gestart wordt.

3. **C++ Applicatie:**
   - Maak een eenvoudige "Hello world" applicatie in C++.
   - Zorg voor een `CMakeLists.txt` bestand dat je project configureert.
   - Het eindresultaat moet zijn dat de applicatie bij het uitvoeren van `docker run` "Hello world" print in de commandline.

4. **Documentatie:**
   - Voeg een `README.md` bestand toe met een korte uitleg over:
     - Hoe je de container bouwt (bijvoorbeeld: `docker build -t hello_world .`).
     - Hoe je de container runt (`docker run hello_world`).
     - Een korte uitleg over de opzet van de Dockerfile en het project.

---

## Testscenario

Controleer lokaal je opdracht door:

1. De Docker image te bouwen:

```bash
docker build -t hello_world .
```

2. De container te runnen:

```bash
docker run hello_world
```
