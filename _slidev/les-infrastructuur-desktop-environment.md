---
title: Infrastructuur & Desktop Environment
output: ../infrastructuur/desktop_environment/files/les-infrastructuur-desktop-environment.pdf
theme: ./slidev-theme-ti
---

# Een applicatie bouwen

- Buildproces in C++: Preprocessen, Compileren, Assembleren & Linken
- Devcontainers en ontwikkelomgeving
- Introductie tot CMake
- Basis debug technieken

<!--
Speaker notes:
Welkom bij deze les over het bouwen van een applicatie in C++. Vandaag nemen we je stap voor stap mee door het buildproces, laten we zien hoe je een consistente ontwikkelomgeving kunt opzetten met devcontainers, hoe CMake hierbij een rol speelt en wat de basisprincipes van debuggen zijn.
-->

---

# Overzicht Buildproces

<br>

- **Preprocessen:** Macro-expansie, include-bestanden en conditionele compilatie
- **Compileren:** Vertalen van preprocessed code naar assembly
- **Assembleren:** Omzetten van assembly code naar objectcode
- **Linken:** Samenvoegen van objectbestanden tot een uitvoerbaar bestand

<br>

```plantuml
!theme cyborg
actor "Developer" as DEV

rectangle "Source Code\nmain.cc" as SRC
rectangle "Preprocessed code\nmain.ii" as PRE
rectangle "Assembly\nmain.s" as ASM
rectangle "Object code\nmain.o" as OBJ
rectangle "Executable\nmain.exe" as EXE

DEV -d-> SRC : Schrijf code
SRC -r-> PRE : Preprocess (includes, macros, defines)
PRE -u-> ASM : Compileren tot assembly
ASM -r-> OBJ : Assembleren tot object
OBJ -d-> EXE : Linken (symbolen zoeken, alles combineren)
```

<!-- Speaker notes:

Deze slide geeft een overzicht van alle stappen die betrokken zijn
bij het bouwen van een C++ applicatie. We zullen elk van deze
stappen verder uitsplitsen in de volgende slides.

-->

---

# Preprocessing

**Wat doet de preprocessor?**

- Vervangt macro’s en constante expressies
- Verwerkt `#include` statements: voegt header-bestanden in
- Voert voorwaardelijke compilatie uit via `#ifdef`, `#ifndef` etc.
- Verwijdert commentaar
- Eigenlijk alles waar een `#` voor staat heeft met de preprocessor
  te maken

<p></p>

```cpp
#include <iostream>
#define SQUARE(x) ((x) * (x))

int main() {
    std::cout << "4 kwadraat is " << SQUARE(4) << "\n";
    return 0;
}
```


---

# Preprocessing: Macro's

**Macro's in C++:**

- Gedefinieerd met `#define`
- Vervangen codefragmenten tijdens de preprocessing
- Worden vaak gebruikt voor herbruikbare code en constante waarden
<v-clicks>

- Zijn een slecht idee!
- Maar je moet wel weten wat ze zijn!

</v-clicks>
<v-click>

**Voorbeeld:**

````md magic-move

```cpp
#define SQUARE(x) ((x) * (x))
```

```cpp
#define SQUARE(x) ((x) * (x))

int main() {
    std::cout << "4 kwadraat is " << SQUARE(4) << "\n";
    return 0;
}
```
<!-- hieronder staat een lege regel met een leeg braille patroon character die ontzichtbaar is om de witregels te bewaren inslidev (⠀) -->
```cpp
⠀

int main() {
    std::cout << "4 kwadraat is " << ((4) * (4)) << "\n";
    return 0;
}
```

````
</v-click>

---
layout: center
---

# Waarom is dit een slecht idee?

<v-clicks>

- Ze zijn geen onderdeel van de taal
- Je kan ze niet debuggen
- Vervelende side effects
- Macros hebben geen namespace

</v-clicks>

---
layout: two-cols
---

# Wat dan wel?

```cpp
#define X = 5

#define SQUARE(x) ((x) * (x))

#import <iostream>

```

::right::

# <br>

```cpp
constexpr static int x = 5;

constexpr auto square(auto x) {return x * x;}

import std; // toekomstmuziek
```

---

# Voorwaardelijke Compilatie

**Wat is voorwaardelijke compilatie?**

- Wordt toegepast met `#ifdef`, `#ifndef`, `#if`, `#else` en `#endif`
- Laat toe dat bepaalde stukken code alleen worden gecompileerd als aan een voorwaarde is voldaan
- Veelgebruikt voor debug builds of platform-specifieke code


````md magic-move
```cpp
#define DEBUG

int main() {
#ifdef DEBUG
    std::cout << "Debug mode aan" << "\n";
#else
    std::cout << "Release mode aan" << "\n";
#endif
    return 0;
}
```
```cpp
int main() {
    std::cout << "Debug mode aan" << "\n";
    return 0;
}
```
````

Je kunt de macro `DEBUG` ook definiëren via de command line (of je buildsysteem), zonder deze in de code te zetten

```bash
g++ -DDEBUG -E main.cc -o main.ii
```

---

# Voorwaardelijke Compilatie: Voorbeeld met Logging
```cpp
#ifdef DEBUG
  #define LOG(msg) std::cout << "DEBUG: " << msg << "\n";
#else
  #define LOG(msg)
#endif

int berekenFactorial(int n) {
    LOG("Start berekenFactorial met n = " << n);
    int result = 1;
    for (int i = 1; i <= n; ++i) {
         result *= i;
         LOG("Intermediate result at i = " << i << " is " << result);
    }
    LOG("Eind berekenFactorial met result = " << result);
    return result;
}

int main() {
    std::cout << "Factorial van 5 is " << berekenFactorial(5) << "\n";
    return 0;
}
```

<Footnotes separator>
  <Footnote><a href="https://www.foonathan.net/2017/05/preprocessor/" target="_blank">Is the preprocessor still needed in C++? —Jonathan Müller</a></Footnote>
</Footnotes>


---

# Include Statements

**Wat doet `#include`?**

- Het voegt de inhoud van een opgegeven bestand in op de plaats van het `#include` statement
- Maakt code modulair en herbruikbaar door declaraties uit headers te importeren

```cpp
#include "myheader.hh"
```

---

# Include Transformatie: Voorbeeld

Stel je hebt een headerbestand `myheader.hh`:

```cpp
// myheader.hh
#ifndef MYHEADER_H
#define MYHEADER_H

#include <iostream>
void printMessage() {
    std::cout << "Hello from myheader!\n";
}

#endif // MYHEADER_H
```

**Originele code:**

```cpp
#include <iostream>
#include "myheader.hh"

int main() {
    printMessage();
    return 0;
}
```

---

# Include Transformatie: Voorbeeld

Stel je hebt een headerbestand `myheader.hh`:

**Na Preprocessing (vereenvoudigd):**

```cpp
#include <iostream> // let op wat hier gebeurd

// Inhoud van myheader.h
#ifndef MYHEADER_H
#define MYHEADER_H

#include <iostream> // let op wat hier gebeurd
void printMessage() {
    std::cout << "Hello from myheader!\n";
}

#endif // MYHEADER_H

int main() {
    printMessage();
    return 0;
}
```

---

# Handmatig Preprocessen

**Hoe laat je de compiler alleen pre-processen?**

- Gebruik de `-E` flag met GCC of Clang.
- Hiermee zie je de output na preprocessing zonder de code te compileren.

```bash
g++ -E main.cc -o main.ii
```

---

# Compileren

**Wat gebeurt er bij compileren?**

- De compiler zet de preprocessed code om in assembly-code
- Optimalisaties worden toegepast
- Er ontstaan waarschuwingen en fouten indien er syntaxfouten in de code zitten

**Codevoorbeeld:**

```cpp
int add(int a, int b) {
    return a + b;
}
```

**Compiler opdracht (GCC):**

```bash
g++ -S main.cc -o main.s
```

---
layout: two-cols
---

# Compileren

```cpp
int add(int a, int b) {
    return a + b;
}
```

::right::

# <br>

```asm
add(int, int):
        push    rbp
        mov     rbp, rsp
        mov     DWORD PTR [rbp-4], edi
        mov     DWORD PTR [rbp-8], esi
        mov     edx, DWORD PTR [rbp-4]
        mov     eax, DWORD PTR [rbp-8]
        add     eax, edx
        pop     rbp
        ret
```



<Footnotes separator>
  <Footnote><a href="https://godbolt.org/z/7xodvPf3n" target="_blank">Bekijk in Compiler Explorer</a></Footnote>
</Footnotes>

---

# Assembleren

**Wat gebeurt er bij assembleren?**

- De assembly-code wordt omgezet in objectcode (van text naar machinecode)
- Het resultaat is een objectbestand (.o of .obj) dat nog niet zelfstandig uitvoerbaar is
- Een object bestand bevat informatie over welke functies en variabele deze aanbied en nodig heeft

**Voorbeeld:**

Na compilatie krijg je een bestand `main.s`. De assembler zet dit om naar `main.o`

```bash
nasm -f elf64 -o main.o main.s 
```

---
layout: two-cols
---

# Voorbeeld

```asm
global _start

section .text

_start:
  mov rax, 1        ; schrijf functie
  mov rdi, 1        ; naar stdout
  mov rsi, msg      ; adres van string
  mov rdx, msglen   ; lengte van string
  syscall           ; roep kernel aan

  mov rax, 60       ; exit functie
  mov rdi, 0        ; 0 = succes
  syscall           ; roep kernel aan

section .rodata
  msg: db "Hello, world!", 10
  msglen: equ $ - msg
```

::right::

# <br>

```bash
objdump -D hello.o
```

```
Disassembly of section .text:

0000000000000000 <_start>:
   0:   b8 01 00 00 00          mov    eax,0x1
   5:   bf 01 00 00 00          mov    edi,0x1
   a:   48 be 00 00 00 00 00    movabs rsi,0x0
  11:   00 00 00
  14:   ba 0e 00 00 00          mov    edx,0xe
  19:   0f 05                   syscall
  1b:   b8 3c 00 00 00          mov    eax,0x3c
  20:   bf 00 00 00 00          mov    edi,0x0
  25:   0f 05                   syscall

```

# <br>

---

# Linking

**Wat gebeurt er bij linken?**

- Meerdere objectbestanden en bibliotheken worden samengevoegd tot één uitvoerbaar bestand
  - Statische objecten (.o, .a, .lib)
  - Dynamische objecten (.so, .dll)
- De linker zorgt voor het oplossen van symbolen (functies en variabelen die in verschillende bestanden of zelfs programmeertalen gedefinieerd zijn)
- Geeft alles een adres
- Zet alles in de juiste sectie
  - text / data / bss

**Voorbeeld:**

```bash
ld -o hello hello.o
objdump -D hello
```

---

# Name mangling

<div class="text-center">
C / Assembly: Geen overloading, interne naam == externe naam
</div>

<div class="grid grid-cols-2 gap-4">

```c
// C
void print_char(char c) {...}
void print_int(int x) {...}
void print_string(const char *s) {...}
```

```asm
; Assembler
print_char: ...
print_int: ...
print_string: ...
```
</div>

<div class="text-center">
C++: Overloading, interne naam == mangle(externe naam)
</div>

<div class="grid grid-cols-2 gap-4">

```cpp
// C++
void print(char c) {...}
void print(int x) {...}
void print(const char *s) {...}
```

```asm
; Assembler
_Z5printc: ...
_Z5printi: ...
_Z5printPKc: ...
```
</div>

<div class="text-center">
C++ met extern "C": Schakelt overloading en mangling uit
</div>

<div class="grid grid-cols-2 gap-4">

```cpp
// C++
extern "C" void print_char(char c) {...}
extern "C" {
    void print_int(int x) {...}
    void print_string(const char *s) {...}
}
```

```asm
; Assembler
print_char: ...

print_int: ...
print_string: ...
⠀
```
</div>

---

# Linking 

<div class="grid grid-cols-2 gap-4">
<div>
main.cc
```cpp
void print_bericht();
char bericht[] = "Hello";
int main() {
    std::cout
        << "Main: [" << bericht << "]"
        << " @ " << (size_t) bericht << "\n";
    print_bericht();
}
```


```plantuml
!theme cyborg
skinparam nodesep 10
skinparam ranksep 1
file main.cc
file bericht.cc
package objects {
  database stdlib.so
  database main.o
  database bericht.o
}
main.cc --> main.o: compile
bericht.cc --> bericht.o: compile

artifact main.exe
objects -> main.exe: link
```

</div>
<div>
bericht.cc
```cpp
char bericht[] = "Hello";
void print_bericht() {
    std::cout
        << "Func: [" << bericht << "]"
        << " @ " << (size_t) bericht << "\n";
}
```

stdout
```
Main: [Hello] @ 102032131358752
Func: [Hello] @ 102032131358758
```

- Twee kopieën in de sources
- Twee kopieën in de executable

</div>
</div>
<Arrow x1="320" y1="162" x2="540" y2="143" two-way />

---

# Linking 

<div class="grid grid-cols-2 gap-4">
<div>
main.cc
```cpp
#include "bericht.hh"
void print_bericht();
int main() {
    std::cout
        << "Main: [" << bericht << "]"
        << " @ " << (size_t) bericht << "\n";
    print_bericht();
}
```


```plantuml
!theme cyborg
skinparam nodesep 10
skinparam ranksep 1
file bericht.hh
file main.cc
file bericht.cc
package objects {
  database stdlib.so
  database main.o
  database bericht.o
}
bericht.hh -r-> main.cc: include
bericht.hh -r-> bericht.cc: include
main.cc --> main.o: compile
bericht.cc --> bericht.o: compile

artifact main.exe
objects -> main.exe: link
```

</div>
<div>
bericht.hh
```cpp
char bericht[] = "Hello";
```

bericht.cc
```cpp
#include "bericht.hh"
void print_bericht() {
    std::cout
        << "Func: [" << bericht << "]"
        << " @ " << (size_t) bericht << "\n";
}
```

stdout
```
Main: [Hello] @ 102032131358752
Func: [Hello] @ 102032131358752
```

- Een kopie in de sources
- Twee kopieën in de executable

</div>
</div>

---

# Linking 

<div class="grid grid-cols-2 gap-4">
<div>
main.cc
```cpp
void print_bericht();
extern char bericht[];
int main() {
    std::cout
        << "Main: [" << bericht << "]"
        << " @ " << (size_t) bericht << "\n";
    print_bericht();
}
```


```plantuml
!theme cyborg
skinparam nodesep 10
skinparam ranksep 1
file main.cc
file bericht.cc
package objects {
  database stdlib.so
  database main.o
  database bericht.o
}
main.cc --> main.o: compile
bericht.cc --> bericht.o: compile

artifact main.exe
objects -> main.exe: link
```

</div>
<div>
bericht.cc
```cpp
char bericht[] = "Hello";
void print_bericht() {
    std::cout
        << "Func: [" << bericht << "]"
        << " @ " << (size_t) bericht << "\n";
}
```

stdout
```
Main: [Hello] @ 102032131358752
Func: [Hello] @ 102032131358752
```

- Een kopie in de sources
- Een kopie in de executable
- Maar...

</div>
</div>

---

# Linking 

<div class="grid grid-cols-2 gap-4">
<div>
main.cc
```cpp
void print_bericht();
extern char bericht[];
int main() {
    std::cout
        << "Main: [" << bericht << "]"
        << " @ " << (size_t) bericht << "\n";
    print_bericht();
}
```


```plantuml
!theme cyborg
skinparam nodesep 10
skinparam ranksep 1
file main.cc
file bericht.cc
package objects {
  database stdlib.so
  database main.o
  database bericht.o
}
main.cc --> main.o: compile
bericht.cc --> bericht.o: compile

artifact main.exe
objects -> main.exe: link
```

</div>
<div>
bericht.cc
```cpp
int bericht = 42;
void print_bericht() {
    std::cout
        << "Func: [" << bericht << "]"
        << " @ " << (size_t) bericht << "\n";
}
```

stdout
```
Main: [

Program terminated with signal: SIGSEGV
```

- Voor de linker is een label maar een geheugenplekje

</div>
</div>

---

# Linking 

<div class="grid grid-cols-2 gap-4">
<div>
main.cc
```cpp
#include "bericht.hh"
void print_bericht();
int main() {
    std::cout
        << "Main: [" << bericht << "]"
        << " @ " << (size_t) bericht << "\n";
    print_bericht();
}
```


```plantuml
!theme cyborg
skinparam nodesep 10
skinparam ranksep 1
file bericht.hh
file main.cc
file bericht.cc
package objects {
  database stdlib.so
  database main.o
  database bericht.o
}
bericht.hh -r-> main.cc: include
bericht.hh -r-> bericht.cc: include
main.cc --> main.o: compile
bericht.cc --> bericht.o: compile

artifact main.exe
objects -> main.exe: link
```

</div>
<div>
bericht.hh
```cpp
char bericht[]; // declaratie (makkelijk)
```

bericht.cc
```cpp
#include "bericht.hh"
char bericht[] = "Hello" // definitie
void print_bericht() {
    std::cout
        << "Func: [" << bericht << "]"
        << " @ " << (size_t) bericht << "\n";
}
```

stdout
```
Main: [Hello] @ 102032131358752
Func: [Hello] @ 102032131358752
```

- Een kopie in de sources
- Een kopie in de executable
- Geen onenigheid!

</div>
</div>

---
layout: center
---

# \<br>

---

# Devcontainers & Ontwikkelomgeving

**Wat zijn devcontainers?**

- Docker containers die als complete ontwikkelomgeving fungeren.
- Bieden een consistente setup voor alle teamleden.
- Verminderen "it works on my machine" problemen.

**Hoe werken ze?**

- Gebruik de **Remote - Containers** extensie in VSCode.
- Start een devcontainer via de command palette.
- Gebruik de "Dev Container: New C++ Project" template als basis.

---

# CMake 

**Waarom CMake?**

- Cross-platform build systeem.
- Beheert buildprocessen via `CMakeLists.txt`.
- Integreert met VSCode voor betere code-completion en debugging.

**Voorbeeld van een CMakeLists.txt:**

```cmake
cmake_minimum_required(VERSION 3.10)
project(HelloWorld)

# Zorgt voor het genereren van compile_commands.json voor IntelliSense
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_executable(hello main.cc)
```

---

# Configuratie CMake voor Autocomplete

**Stap-voor-stap:**

1. **CMakeLists.txt aanpassen:** Voeg `set(CMAKE_EXPORT_COMPILE_COMMANDS ON)` toe.
2. **Build directory maken:**

   ```bash
   mkdir build && cd build
   cmake ..
   ```

3. **VSCode instellen:**  
   Open de Command Palette (`Ctrl+Shift+P`) en kies `C/C++: Edit Configurations (UI)` om het pad naar `build/compile_commands.json` in te stellen.

---

# Debuggen in C++

**Basisprincipes:**

- **Breakpoints:** Stop de uitvoering op een specifieke regel.
- **Step Over/Into:** Voer code regel voor regel uit.
- **Variabelen inspecteren:** Bekijk de waarde van variabelen tijdens runtime.

**Voorbeeldcode:**

```cpp
#include <iostream>

int main() {
    int a = 5;
    int b = 0;
    // Zet hier een breakpoint
    int c = a / b; // Fout: deling door nul
    std::cout << "Result: " << c << "\n";
    return 0;
}
```

---
layout: center
---

# \0
