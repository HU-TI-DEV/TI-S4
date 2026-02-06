# Recap C++

Jullie hebben C++ al gehad in S2 en S3.  Alleen we weten dat C++ soms best lastig kan zijn. Voordat we de meer geavanceerdere zaken ingaan in S4 willen we daarom graag de basis nog een keer goed bekijken
Veel van de meer 'geavanceerdere' onderwerpen zoals design patterns, templates en lambda's, - die we wat later in het semester gaan behandelen,- bouwen uiteraard voort op de basis.
B
We doen dit aan de hand van quizjes, oefeningen in de klas en uiteraard live coderen zodat we samen zien hoe code werkt en waarom het zo werkt.

## Onderwerpen recap les 1

- Functions
- References
- Pointers
- Memory allocation (new/delete)
- Undefined behavior (gebeurt al vrij snel als je met de onderwerpen hierboven aan de slag gaat..)

## Gebruikte IDE

Jullie hebben in de voorgaande semesters al met C++ gewerkt, je kan in je favoriete IDE blijven werken. Aangezien we vanuit HU Jetbrains producten zoals PyCharm kunnen gebruiken, kan je CLion ook proberen, het komt uit dezelfde familie als PyCharm en is gebruiksvriendelijk. 

## Quiz

We beginnen de les met een Wooclap quiz, waarna we de antwoorden bespreken.

## Oefeningen ter voorbereiding

1. Schrijf een functie `int clamp(int value, int min, int max);` die:
   - `min` teruggeeft als `value < min`
   - `max` teruggeeft als `value > max`
   - en anders `value` teruggeeft
2. Schrijf een functie `void swapValues(int& a, int& b);` die twee ints `a` en `b` verwisselt.
3. Schrijf een functie `int findMax(const int* arr, int size);` die een pointer krijgt naar een integer array en de maximum waarde teruggeeft. Gebruik hierbij pointer arithmetic (dus geen `arr[index]`)
4. Schrijf een functie `int* createArray(int n, int value);` die dynamisch een array van `n` integers alloceert, alle elementen op `value` initialiseert en een pointer teruggeeft naar deze array. Gebruik hierbij `new []`. Laat ook zien hoe je deze functie correct aanroept en dat je de geheugen weer goed opruimt.
5. In de volgende stukje code, wat is het probleem en hoe kan je het oplossen? `int& getValue() {
    int x = 10;
    return x;
}`
