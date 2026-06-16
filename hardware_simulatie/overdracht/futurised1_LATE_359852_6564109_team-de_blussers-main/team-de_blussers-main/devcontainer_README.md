---

# Firefighting Tank Simulation

Gazebo project met Dev Container (image: `s4_2026`)

## Overzicht

Dit project gebruikt een VS Code Dev Container gebaseerd op de Docker image `s4_2026`.
Iedereen werkt in exact dezelfde containeromgeving om verschillen in installaties en versies te voorkomen.

Alle teamleden werken op Windows met VS Code.

---

# 1. Vereisten

Installeer vooraf:

* Docker Desktop (WSL2 backend ingeschakeld)
* Visual Studio Code
* VS Code extensie: Dev Containers
* Git
* MobaXterm

Controleer of Docker draait voordat je begint.

---

# 2. Repository clonen

Open een terminal (PowerShell of Git Bash):

```bash
git clone <repo-url>
```

Open daarna de map in VS Code.

---

# 3. Project openen in Dev Container

1. Open de map in VS Code
2. Klik linksonder op "Reopen in Container"
   of via Command Palette (ctrl + shift + p):
   `Dev Containers: Reopen in Container`

VS Code bouwt of start nu een container op basis van image `s4_2026`.

Wanneer de container gestart is, open je een terminal in VS Code.


---

# 4. Projectstructuur

```
Root/
├─ .devcontainer/        Container configuratie
├─ models/               Robotmodellen (SDF)
├─ worlds/               Simulatie werelden
├─ plugins/              Optionele C++ plugins
├─ test/                 Bevat een gazebo test file
├─ README.md
├─ devcontainer_README.md
└─ .gitignore
```

* `models/` bevat de tank/het voertuig (SDF).
* `worlds/` bevat de simulatie-omgeving.
* `plugins/` bevat eventuele besturingscode.
* `.devcontainer/` definieert de containeromgeving.

---

# 5. Simulatie testen

In de containerterminal:

```bash
cd test
gz sim robot.sdf
```
---

# 6. Werkwijze met branches

Werk nooit direct op `main`.

## Nieuwe feature starten

```bash
git checkout main
git pull
git checkout -b feature/<naam>
```

Voorbeelden:

```
feature/water-cannon
feature/arena-obstacles
feature/tank-tracks
```

---

# 7. Wijzigingen maken

Pas bestanden aan in:

* `models/`
* `worlds/`
* `plugins/`

Controleer wijzigingen:

```bash
git status
```

---

# 8. Committen

```bash
git add .
git commit -m "Korte duidelijke beschrijving van wijziging"
```

Voorbeeld:

```bash
git commit -m "Obstacle toegevoegd aan fire_arena"
```

---

# 9. Pushen naar GitHub

```bash
git push origin feature/<naam>
```

Daarna:

1. Ga naar GitHub
2. Maak een Pull Request
3. Laat een teamlid reviewen
4. Merge naar `main`

---

# 10. Updates van anderen binnenhalen

Voordat je verder werkt:

```bash
git checkout main
git pull
git checkout feature/<naam>
git merge main
```

Dit voorkomt merge conflicts.

---

# 11. Container afsluiten

De container stopt automatisch wanneer VS Code wordt afgesloten.

Belangrijk:

* De code staat in de lokale repository, niet in de container.
* Het verwijderen van de container verwijdert niet je projectbestanden.

Container opnieuw bouwen indien nodig:

Command Palette →
`Dev Containers: Rebuild Container`

---

# 12. Wat niet committen

Zie `.gitignore`. De git ignore regeld dit eigenlijk

Niet committen:

* build/
* *.so
* *.o
* *.log
* .vscode/

---

# 13. Standaard workflow samengevat

1. git checkout main
2. git pull
3. git checkout (-b) feature/<naam>
4. Wijzigingen maken
5. Testen in Gazebo
6. git add .
7. git commit
8. git push
9. Pull Request maken

---

