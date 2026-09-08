# Oefenproject Recap C++ Deel I

Oefeningen bij de les [Recap C++ Deel I](../recap_cpp_1.md). Bij elke oefening draait het om dezelfde drie vragen: *waar staat mijn data, wie is er eigenaar van, en hoe lang leeft het?*

Het project is een gewoon CMake-project met een devcontainer, dezelfde basis als het project van vorige week. Warnings en sanitizers staan al aan.

## Opstarten

1. `git pull` (of kloon de repository).
2. Open **deze map** (`software/cpp/recap_1`) als workspace in VSCode: *File > Open Folder*.
3. `Ctrl+Shift+P` > **Dev Containers: Reopen in Container**. De eerste keer duurt dit even.
4. CMake Tools configureert automatisch. Kies in de statusbalk onderaan een *launch target* (bijvoorbeeld `01_functies`), klik op *Build* en daarna op *Run* of *Debug* (`F5`).

Liever de terminal?

```bash
cmake -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build
./build/01_functies
```

## De oefeningen

| | Bestand | Onderwerp | Klaar als |
|---|---|---|---|
| 1 | `src/01_functies.cc` | `clamp`, `swap` by reference en by pointer | het programma eindigt met `alles OK` |
| 2 | `src/02_pointers.cc` | `findMax`, `findValue`, `reverse` met `[begin, end)` pointers | idem, plus het experiment onderaan gedaan |
| 3 | `src/03_bughunt.cc` | **acht verstopte bugs** opsporen met warnings, sanitizers en de debugger | alle bugs gevonden, gefixt en beschreven |

Elk bestand begint met een uitleg en bevat `TODO`'s. De `main()` controleert je werk met `assert`. De warnings over *unused parameter* verdwijnen zodra je de functies implementeert.

## Gereedschap

**Warnings** (`-Wall -Wextra`) staan aan. Lees ze. Twee van de acht bugs in de bug hunt geeft de compiler al weg.

**Sanitizers** (`-fsanitize=address,undefined`) staan aan in de Debug build. Het programma controleert zichzelf tijdens het draaien en stopt bij de **eerste** fout met een rapport. Fix die ene bug, bouw, draai opnieuw.

**Debugger:** `F5` start de huidige CMake-target in de debugger. Zet een breakpoint op de regel uit het sanitizer-rapport en bekijk de call stack en de variabelen.

**Valgrind** werkt niet samen met AddressSanitizer. Wil je valgrind gebruiken, configureer dan een tweede build zonder sanitizers:

```bash
cmake -B build-valgrind -DENABLE_SANITIZERS=OFF
cmake --build build-valgrind
valgrind --leak-check=full ./build-valgrind/03_bughunt
```

## Een sanitizer-rapport lezen

Zo'n rapport ziet er intimiderend uit, maar alles wat je nodig hebt staat in de eerste regels:

```text
==1234==ERROR: AddressSanitizer: heap-use-after-free on address 0x602000000010
READ of size 4 at 0x602000000010 thread T0
    #0 0x5555 in readTemporarySensor src/03_bughunt.cc:82      <- hier ging het fout
    #1 0x5555 in main src/03_bughunt.cc:118

0x602000000010 is located 0 bytes inside of 32-byte region
freed by thread T0 here:
    #0 0x7f00 in operator delete(void*)
    #1 0x5555 in readTemporarySensor src/03_bughunt.cc:81      <- hier is het vrijgegeven

previously allocated by thread T0 here:
    #0 0x7f00 in operator new(unsigned long)
    #1 0x5555 in readTemporarySensor src/03_bughunt.cc:80      <- hier is het aangemaakt
```

Lees van boven naar beneden:

1. **Wat:** het soort fout (`heap-use-after-free`, `heap-buffer-overflow`, `double-free`, `signed integer overflow`, ...).
2. **Waar:** de bovenste regel van de eerste stack trace die in *jouw* code zit.
3. **Wanneer vrijgegeven** en **wanneer aangemaakt:** de volgende twee stack traces. Daaruit volgt meestal meteen de fix.

Bij een geheugenlek (`LeakSanitizer: detected memory leaks`) staat er alleen waar het geheugen is aangemaakt: de vraag is dan wie het had moeten opruimen.
