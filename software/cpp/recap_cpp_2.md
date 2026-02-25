# Recap C++

Jullie hebben C++ al gehad in S2 en S3.  Alleen we weten dat C++ soms best lastig kan zijn. Voordat we de meer geavanceerdere zaken ingaan in S4 willen we daarom graag de basis nog een keer goed bekijken
Veel van de meer 'geavanceerdere' onderwerpen zoals design patterns, (geavanceerdere) templates en lambda's, - die we wat later in het semester gaan behandelen,- bouwen uiteraard voort op de basis.

We doen dit aan de hand van quizjes, oefeningen in de klas en uiteraard live coderen zodat we samen zien hoe code werkt en waarom het zo werkt.

## Onderwerpen recap les 2

- Templates
   - template specialization
- OOP
   - classes
   - inheritance
   - polymorphism
   - destructors
- 

## Gebruikte IDE

Jullie hebben in de voorgaande semesters al met C++ gewerkt, je kan in je favoriete IDE blijven werken. Als het goed is heb je een devcontainer opgezet, dat is ook de aanpak die we tijdens deze lessen hanteren.

## Quiz

We beginnen de les met een Wooclap quiz, waarna we de antwoorden bespreken.

## Oefeningen ter voorbereiding
1a.Schrijf een functie template `maxValue` die twee waarden vergelijkt en de grootste teruggeeft.
Test de functie met: `int`, `double`, `std::string`
1b. Breid `maxValue` uit met een template specialization voor `const char*`.

Probleem: bij `const char*` wordt standaard het adres vergeleken in plaats van de inhoud.
Zorg dat de specialisatie `strcmp` gebruikt.
2. Maak een abstracte klasse Shape met:

`virtual double area() const = 0;`

`virtual ~Shape();`

Maak twee afgeleide klassen: `Circle` en `Rectangle`

Gebruik polymorfisme via een `Shape*` array.

3. Oefening – Garage met verschillende voertuigen
Modelleer een Garage waarin zich 0 of meer voertuigen kunnen bevinden.

### Vereisten
#### Abstracte klasse Vehicle

- protected: std::string brand

- constructor met parameter

- `virtual double calculateTax() const = 0;`

- `virtual void print() const = 0;`

`virtual ~Vehicle();`

#### Afgeleide klassen
`Car`

extra attribuut: `int horsepower`

belasting = `horsepower * 0.5`

`Truck`

extra attribuut: `double maxLoad`

belasting = `maxLoad * 2`

`Garage`

Bevat een `std::vector<Vehicle*>`

Methods:

`void addVehicle(Vehicle* v);`

`double totalTax() const;`

`void printAll() const;`

Destructor moet alle voertuigen correct verwijderen

#### Test in main

Maak een garage

Voeg minstens:

2 auto’s

1 vrachtwagen

Print alle voertuigen

Print totale belasting
