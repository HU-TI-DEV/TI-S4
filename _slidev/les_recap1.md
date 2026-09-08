---
title: Recap C++ Deel I
output: ../software/cpp/recap_cpp_1.pdf
theme: ./slidev-theme-ti
hideInToc: true
---

# Recap C++ Deel I

functies, pointers, references

<!--
Speaker notes (totaal ~60 min):
- Quiz: 15 min
- Aan de slag met het oefenproject, ik loop rond: 40 min
- Plenaire afsluiting: 5 min

Welkom. Jullie hebben C++ gehad in S2 en S3, en vorige week hebben we de devcontainer, CMake en de debugger opgezet. Vandaag gebruiken we die omgeving om de basis scherp te zetten. Geen college: een quiz, dan aan het werk. Uitleg krijg je als je vragen hebt, bij de quiz of bij de opdrachten.
-->

---
layout: table-of-contents
hideInToc: true
---

# Programma

---

# Recap

**Al gehad**

- S2: functies, by value / by reference, `vector`, structs, klassen
- S3: heap, `new` / `delete`, levensduur, rule of three, smart pointers
- Vorige week: devcontainer, CMake, debugger

**Vandaag: bij elke variabele, pointer of reference dezelfde drie vragen**

- Waar staat mijn data? Stack of heap?
- Wie is er eigenaar van?
- Hoe lang leeft het?

**Komt later**

- STL & lambda's: iteratoren zijn pointers, captures zijn by value / by reference
- Smart pointers & design patterns: geheugenbeheer zonder `new` / `delete`
- Pointers, references & UB: de diepte in

<!--
Speaker notes:
Dit is geen nieuwe stof. Het is dezelfde stof als in S2 en S3, maar nu met de drie vragen erbij die je bij elke variabele moet kunnen beantwoorden. Elke bug in de opdrachten van vandaag is een fout antwoord op een van deze drie vragen. Onderaan: waar het dit semester terugkomt.
-->

---
layout: chaptertitle
---

# Quiz

<!--
Speaker notes (15 min):
Acht vragen, één per slide. Laat ze 20 seconden nadenken, hand opsteken per antwoord, dan klik. Bij twijfel of discussie: dit is het moment voor uitleg. Noteer bij welke vragen het misgaat; daar loop je straks als eerste naartoe.
-->

---
hideInToc: true
---

# Wat print dit? (1)

```cpp
void inc(int x) { x++; }

int main() {
    int a = 5;
    inc(a);
    std::cout << a;
}
```

<v-click>

> `5`

`x` is een **kopie** van `a`.

</v-click>

<!--
Speaker notes:
By value: de functie krijgt een kopie. Dit moet iedereen kunnen.
-->

---
hideInToc: true
---

# Wat print dit? (2)

```cpp
void inc(int& x) { x++; }

int main() {
    int a = 5;
    inc(a);
    std::cout << a;
}
```

<v-click>

> `6` 

`x` is een **alias** van `a`: een andere naam voor hetzelfde geheugen.

</v-click>

<!--
Speaker notes:
By reference: geen kopie, een tweede naam. Vooruitwijzing: de capture clause van een lambda is exact dezelfde keuze.
-->

---
hideInToc: true
---

# Wat print dit? (3)

```cpp
int main() {
    int a = 5;
    int* p = &a;
    *p = 7;
    int& r = a;
    r++;
    std::cout << a;
}
```

<v-click>

> `8`

`p` en `r` verwijzen allebei naar `a`. Verschil: `p` is een eigen pointer van `a`, dus eigen adres, `r` is alleen een andere naam.

Gebruik alleen pointers als het nodig is!

</v-click>

<!--
Speaker notes:
Een pointer en een reference naar dezelfde variabele. Als hier vragen komen: een pointer heeft een eigen vakje met een adres erin, kan leeg zijn en kan veranderd worden. Een reference is een naam, moet altijd gebonden zijn en kan niet veranderd worden.
-->

---
hideInToc: true
---

# Wat print dit? (4)

```cpp
int main() {
    int arr[] = {10, 20, 30};
    int* p = arr;
    p++;
    std::cout << *p + *(p + 1);
}
```

<v-click>

> `50`

`p++` springt één **element** verder, niet één byte. `p[i]` is `*(p + i)`.

</v-click>

<!--
Speaker notes:
Pointer arithmetic werkt in elementen. Dit is de belangrijkste vooruitwijzing: een STL-iterator gedraagt zich als een pointer. Wie oefening 2 snapt, snapt std::find.
-->

---
hideInToc: true
---

# Wat print dit? (5)

```cpp
int main() {
    int* p = new int(5);
    int* q = p;
    delete p;
    std::cout << *q;
}
```

<v-click>

**Undefined behaviour.** Use after free. Print misschien `5`, misschien iets anders, misschien een crash, misschien velociraptors. 

</v-click>

<!--
Speaker notes:
Hier gaat het meestal mis: de helft zegt 5, en in de praktijk print het ook vaak 5. Dat is het gevaar. UB is niet hetzelfde als een crash, en het gevaarlijkste UB is het UB dat toevallig werkt. Daarom sanitizers in het oefenproject.
-->

---
hideInToc: true
---

# Wat print dit? (6)

```cpp
int& getValue() {
    int x = 10;
    return x;
}

int main() {
    int y = getValue();
    std::cout << y;
}
```

<v-click>

**Undefined behaviour.** `x` leeft op de stack van `getValue` en bestaat niet meer. De compiler **waarschuwt** hier; lees je warnings.

</v-click>

<!--
Speaker notes:
Dangling reference. Bij elke reference of pointer: hoe lang leeft het ding waar hij naar wijst? De vector-variant is subtieler en zit in de bug hunt, want die gaan ze in het project maken.
-->

---
hideInToc: true
---

# Wat print dit? (7)

```cpp
int main() {
    const int x = 5;
    int* p = &x;
    *p = 6;
    std::cout << x;
}
```

<v-click>

**Compileert niet.** `&x` is een `const int*`, dat past niet in een `int*`. `const` is een belofte die de compiler voor je bewaakt.

</v-click>

<!--
Speaker notes:
Const beschermt je: de compiler weigert. In oefening 2 krijgen ze const int* als parameter en moeten ze uitleggen waarom schrijven niet compileert.
-->

---
hideInToc: true
---

# Wat print dit? (8)

```cpp
void f(int a[]) {
    std::cout << sizeof(a);
}

int main() {
    int arr[10];
    std::cout << sizeof(arr) << " ";
    f(arr);
}
```

<v-click>

> `40 8`

een array **vervalt (decayed) tot een pointer** zodra je hem doorgeeft. In `f` is `a` gewoon een `int*`.

</v-click>

<!--
Speaker notes:
De klassieke valkuil. int a[] als parameter is int*. Vandaar begin/end in oefening 2, en vandaar de STL-containers.
-->

---
layout: chaptertitle
---

# Aan de slag

<!--
Speaker notes (40 min):
Vanaf hier werken zij en loop ik rond. Begin bij wie het project niet aan de praat krijgt, daarna bij de studenten die bij vraag 5 en 6 fout zaten.
-->

---

# Oefenproject `software/cpp/recap_1`

| | Bestand | Wat |
|---|---|---|
| 1 | `src/01_functies.cc` | `clamp`, `swap` by reference en by pointer |
| 2 | `src/02_pointers.cc` | `findMax`, `findValue`, `reverse` met `[begin, end)` |
| 3 | `src/03_bughunt.cc` | **acht verstopte bugs**: vind ze met warnings, sanitizers en debugger |

**Opstarten:** `git pull`, open de map `software/cpp/recap_1` in VSCode, *Reopen in Container*, CMake Tools: target kiezen, Build, Run of `F5`.

<!--
Speaker notes:
De README van het project legt uit hoe je een sanitizer-rapport leest en hoe je valgrind gebruikt. Bug 1 van de bug hunt is het berekenGemiddelde-voorbeeld van vorige week: toen met de debugger stap voor stap, nu vindt de sanitizer hem in één run. Wijs daarop als ze hem tegenkomen.
-->

---

# Verder kijken

- [Back to Basics: Pointers and Memory — Ben Saks (CppCon)](https://www.youtube.com/watch?v=rqVWj0aVSxg)
- [cppreference: Undefined behavior](https://en.cppreference.com/w/cpp/language/ub)
- [AddressSanitizer](https://github.com/google/sanitizers/wiki/AddressSanitizer)

---
layout: center
---

# \0
