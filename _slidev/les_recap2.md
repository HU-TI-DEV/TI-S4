---
theme: ./slidev-theme-ti
output: ../software/cpp/recap_cpp_2.pdf
hideInToc: true
---

# Recap C++ Part 2

---
layout: table-of-contents
hideInToc: true
---

# Programma

---
hideInToc: true
---

# Waarom een recap?

C++ is een krachtige taal, maar veel onderwerpen bouwen op elkaar voort.

Vandaag herhalen we de basis voor de komende lessen:

- templates en specialization
- classes, inheritance en polymorphism
- virtual destructors en ownership

<br>

Daarna pas zijn onderwerpen als lambda's, design patterns en geavanceerde templates echt prettig te volgen.

---
layout: center
hideInToc: true
---

# Eerst: quiz

Bespreek daarna de antwoorden samen.

---

# Templates

Een template beschrijft een blauwdruk voor code die met meerdere types werkt.

```cpp {monaco-run}
#include <iostream>

template <typename T>
T maxValue(T first, T second) {
	return first > second ? first : second;
}

int main() {
	std::cout << maxValue(12, 7) << '\n';
	std::cout << maxValue(3.5, 4.2) << '\n';
}
```

De compiler maakt bij gebruik de passende functie, bijvoorbeeld `maxValue<int>`.

---
layout: two-cols
hideInToc: true
---

# Type deduction

Meestal leidt de compiler het type af uit de argumenten.

```cpp {monaco-run}
#include <iostream>
#include <string>

template <typename T>
T maxValue(T first, T second) {
	return first > second ? first : second;
}

int main() {
	std::cout << maxValue(12, 7) << '\n';
	std::cout << maxValue(3.5, 4.2) << '\n';
	std::cout << maxValue(
		std::string("Ada"), std::string("Bjarne")) << '\n';
}
```

::right::

# Een voorwaarde

De bewerking in de template moet bestaan voor type `T`.

In dit geval moet `T` vergelijkbaar zijn met `>`.

<v-click>

```cpp
struct Point {
	int x;
	int y;
};

Point a{1, 2};
Point b{3, 4};
// maxValue(a, b); // geen operator> voor Point
```

</v-click>

---

# Template specialization

Soms werkt de algemene template wel, maar doet hij niet wat je bedoelt.

````md magic-move
```cpp
template <typename T>
T maxValue(T first, T second) {
	return first > second ? first : second;
}

maxValue("appel", "peer");
```

```cpp
// const char* vergelijkt adressen, niet tekstinhoud.
template <>
const char* maxValue(const char* first, const char* second) {
	return std::strcmp(first, second) > 0 ? first : second;
}

maxValue("appel", "peer"); // "peer"
```
````

<v-click>

Voor `const char*` maken we dus bewust een gespecialiseerde versie.

</v-click>

---
hideInToc: true
---

# `const char*` vergelijken

```cpp {monaco-run}
#include <cstring>
#include <iostream>

template <typename T>
T maxValue(T first, T second) {
	return first > second ? first : second;
}

template <>
const char* maxValue(const char* first, const char* second) {
	return std::strcmp(first, second) > 0 ? first : second;
}

int main() {
	std::cout << maxValue("appel", "peer") << '\n';
}
```

`std::strcmp` geeft een positieve waarde als de eerste tekst alfabetisch later komt.

---
hideInToc: true
---

# Check-in: templates

<v-clicks>

1. Wanneer kan type deduction niet slagen?
2. Waarom is `const char*` een bijzonder geval voor `maxValue`?
3. Welke operator moet een type ondersteunen in onze algemene template?
4. Wanneer kies je een specialization in plaats van een tweede functienaam?

</v-clicks>

<!--
1) Als argumenten geen eenduidig type opleveren of de benodigde operatie ontbreekt.
2) > vergelijkt pointeradressen, niet de karakters.
3) operator>.
4) Als het concept hetzelfde blijft maar een type een afwijkende implementatie nodig heeft.
-->

---
layout: center
hideInToc: true
---

# Daarna: OOP

---

# Classes: data en gedrag

Een class combineert state met functies die op die state werken.

```cpp {monaco-run}
#include <iostream>
#include <string>

class Circle {
public:
	explicit Circle(double radius) : radius(radius) {}

	double area() const {
		return 3.14159 * radius * radius;
	}

private:
	double radius;
};

int main() {
	Circle circle(2.0);
	std::cout << circle.area() << '\n';
}
```

`private` beschermt de interne state; de public interface is het contract met de gebruiker.

---
layout: two-cols
hideInToc: true
---

# Inheritance

Verschillende objecten kunnen een gedeeld concept hebben.

```cpp
class Shape {
public:
	virtual double area() const = 0;
	virtual ~Shape() = default;
};

class Circle : public Shape {
public:
	explicit Circle(double radius) : radius(radius) {}
	double area() const override {
		return 3.14159 * radius * radius;
	}
private:
	double radius;
};
```

::right::

# Abstracte class

`= 0` maakt `area` een pure virtual function.

- `Shape` beschrijft de interface
- je maakt geen los `Shape` object
- elke concrete afgeleide class implementeert `area`

<v-click>

```cpp
// Shape shape; // fout: abstracte class
Circle circle(2.0); // prima
```

</v-click>

---

# Polymorphism

Via een `Shape*` mag je verschillende afgeleide types gelijk behandelen.

```cpp {monaco-run}
#include <iostream>

class Shape {
public:
	virtual double area() const = 0;
	virtual ~Shape() = default;
};

class Rectangle : public Shape {
public:
	Rectangle(double width, double height) : width(width), height(height) {}
	double area() const override { return width * height; }
private:
	double width;
	double height;
};

int main() {
	Shape* shape = new Rectangle(3.0, 4.0);
	std::cout << shape->area() << '\n';
	delete shape;
}
```

Door `virtual` kiest C++ tijdens runtime de `area` van `Rectangle`.

---
hideInToc: true
---

# Waarom een virtual destructor?

```cpp
class Shape {
public:
	virtual double area() const = 0;
	virtual ~Shape() = default;
};

Shape* shape = new Circle(2.0);
delete shape;
```

<v-click>

`delete` via een base pointer moet ook de destructor van de afgeleide class uitvoeren.

</v-click>

<v-click>

Zonder `virtual ~Shape()` is dit undefined behaviour zodra een derived class resources beheert.

</v-click>

---
layout: two-cols
hideInToc: true
---

# `override` helpt

```cpp
class Circle : public Shape {
public:
	double area() const override {
		return 3.14159 * radius * radius;
	}
};
```

`override` vertelt de compiler dat deze functie een virtual functie uit de base class moet overschrijven.

::right::

# Typfouten vangen

```cpp
class Circle : public Shape {
public:
	double Area() const override {
		return 0.0;
	}
};
```

Dit compileert niet: `Area` is iets anders dan `area`.

---
hideInToc: true
---

# Check-in: OOP

<v-clicks>

1. Wat betekent `= 0` achter een virtual functie?
2. Waarom gebruiken we `Shape*` voor polymorphism?
3. Wat gebeurt er zonder virtual destructor bij `delete` via een base pointer?
4. Welk probleem helpt `override` voorkomen?

</v-clicks>

<!--
1) Pure virtual function; de class is abstract.
2) Een pointer naar de base class kan naar ieder derived object wijzen.
3) De destructor van de derived class wordt mogelijk niet uitgevoerd: UB.
4) Een typefout of afwijkende signatuur die per ongeluk geen override is.
-->

---

# Oefening 1: `maxValue`

1. Schrijf een functietemplate `maxValue` voor twee waarden.
2. Test met `int`, `double` en `std::string`.
3. Voeg een specialization toe voor `const char*`.

```cpp
template <typename T>
T maxValue(T first, T second);

template <>
const char* maxValue(const char* first, const char* second);
```

Gebruik voor de specialization `std::strcmp` uit `<cstring>`.

---

# Oefening 2: Shapes

Maak een abstracte `Shape` class met:

```cpp
virtual double area() const = 0;
virtual ~Shape() = default;
```

Maak daarna:

- `Circle` met een radius
- `Rectangle` met width en height
- een array van `Shape*` om beide vormen te tonen

<v-click>

Roep voor elk element `area()` aan en verwijder daarna elk object.

</v-click>

---

# Oefening 3: Garage

Modelleer een garage met verschillende voertuigen.

```cpp
class Vehicle {
protected:
	std::string brand;
public:
	explicit Vehicle(std::string brand);
	virtual double calculateTax() const = 0;
	virtual void print() const = 0;
	virtual ~Vehicle() = default;
};
```

Maak `Car` en `Truck` als afgeleide classes.

---
layout: two-cols
hideInToc: true
---

# Garage: regels

**Car**

- extra attribuut: `int horsepower`
- belasting: `horsepower * 0.5`

**Truck**

- extra attribuut: `double maxLoad`
- belasting: `maxLoad * 2`

::right::

# Garage: interface

```cpp
class Garage {
public:
	void addVehicle(Vehicle* vehicle);
	double totalTax() const;
	void printAll() const;
	~Garage();
private:
	std::vector<Vehicle*> vehicles;
};
```

De destructor verwijdert alle voertuigen die de garage bezit.

---
hideInToc: true
---

# Garage: test in `main`

```cpp
int main() {
	Garage garage;
	garage.addVehicle(new Car("Volvo", 180));
	garage.addVehicle(new Car("Toyota", 110));
	garage.addVehicle(new Truck("DAF", 12.5));

	garage.printAll();
	std::cout << "Totale belasting: "
			  << garage.totalTax() << '\n';
}
```

<v-click>

Wie is eigenaar van de pointers nadat je `addVehicle` hebt aangeroepen?

</v-click>

---
hideInToc: true
---

# Afsluiting

- templates geven generieke code met typecontrole
- specialization lost een type-specifiek probleem op
- abstracte classes beschrijven een gemeenschappelijke interface
- polymorphism werkt via virtual functies
- een virtual destructor is nodig bij verwijderen via een base pointer

Volgende stap:

- deze bouwstenen gebruiken in modernere C++-patronen
