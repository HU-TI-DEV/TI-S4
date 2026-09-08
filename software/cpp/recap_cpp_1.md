# Recap C++ Deel I: functies, references, pointers & geheugen

Jullie hebben C++ gehad in S2 en S3, en vorige week hebben we de ontwikkelomgeving opgezet (devcontainer, CMake, debugger). Voordat we dit semester de diepte in gaan met de STL, lambda's, templates en design patterns, herhalen we nog een keer wat echt belangrijk is.

## Leerdoelen

Na deze les kun je:

- uitleggen wanneer je een parameter by value, by reference of by `const&` doorgeeft;
- het verschil tussen een reference en een pointer benoemen en de juiste kiezen;
- met een `[begin, end)` paar pointers over een array lopen, en uitleggen waarom STL-iteratoren hetzelfde werken;
- van elke pointer of reference zeggen hoe lang het object leeft waar hij naar wijst;
- uitleggen wie geheugen opruimt op de stack, op de heap, en in een object dat eigenaar is (RAII);
- uitleggen wat undefined behaviour is en waarom "het werkt" niets bewijst;
- geheugenfouten en UB opsporen in je devcontainer met compiler-warnings, AddressSanitizer, UBSan en de debugger.

## Materiaal

- [Slides (pdf)](./recap_cpp_1.pdf)
- [Oefenproject `recap_1`](./recap_1/README.md): CMake-project met devcontainer, warnings en sanitizers al ingesteld.

## Oefeningen

Alles staat in [`recap_1/`](./recap_1/README.md):

| | Oefening | Onderwerp |
|---|---|---|
| 1 | `01_functies` | `clamp`, `swap` by reference en by pointer |
| 2 | `02_pointers` | `findMax`, `findValue`, `reverse` met `[begin, end)` pointers, `const` correct |
| 3 | `03_bughunt` | acht verstopte bugs opsporen met warnings, sanitizers en de debugger |

## Verder kijken

- [Back to Basics: Pointers and Memory, Ben Saks (CppCon)](https://www.youtube.com/watch?v=rqVWj0aVSxg)
- [cppreference: Undefined behavior](https://en.cppreference.com/w/cpp/language/ub)
- [AddressSanitizer](https://github.com/google/sanitizers/wiki/AddressSanitizer)
