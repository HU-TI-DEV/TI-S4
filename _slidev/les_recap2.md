---
theme: ./slidev-theme-ti
output: ../software/cpp/recap_cpp_2.pdf
hideInToc: true
---

# Recap C++ part 2

## OOP & Templates

---
layout: table-of-contents
hideInToc: true
---

# Programma

---
hideInToc: true
---

# Doel

Na deze les begrijp je (beter, of opnieuw, of alsnog):

- Classes, wat?
- Inheritance, hoe?
- Destructors, huh?
- Templates, hoeveel?
- Template specializations, wanneer?

---

# OOP; herhaling

Object-Oriented Programming draait om het modelleren van je probleem als objecten:

<v-clicks>

- **Encapsulation:** data en gedrag samen in één class
- **Abstraction:** interface tonen, implementatie verbergen
- **Inheritance:** gedrag/structuur hergebruiken via een parent-child relatie
- **Polymorphism:** dezelfde interface, ander gedrag

</v-clicks>

---
layout: two-cols
hideInToc: true
---

# Classes

Een class beschrijft:

- **members**: data (attributes) die bij het object horen
- **methods**: functies die op die data werken
- **constructor(s)**: hoe een object geïnitialiseerd wordt

```cpp
class Vehicle {
protected:
    string brand;

public:
    Vehicle(const string& brand)
        : brand(brand) {}

    void print() const {
        cout << brand << endl;
    }
};
```

::right::

# Access modifiers

- **public:** overal toegankelijk
- **protected:** class zelf + afgeleide classes
- **private:** alleen de class zelf

<br>

Vuistregel:
- members zo **restrictief mogelijk** houden
- alleen public maken wat echt naar buiten moet

<br>

<v-click>

Dit is **encapsulation** in de praktijk: interne details verbergen, alleen een
duidelijke interface tonen.

</v-click>

---
hideInToc: true
layout: two-cols
---

# Quiz: welke constructor compileert?

<br>Gegeven de klasse `Vehicle`:

```cpp
class Vehicle {
protected:
    string brand;
public:
    Vehicle(const string& brand)
        : brand(brand) {}
};
```

Welke van de twee `Car`-constructors hiernaast compileert?

::right::

<br>

**Optie A**

```cpp
class Car : public Vehicle {
private:
    int horsepower;
public:
    Car(const string& brand, int hp)
        : brand(brand), horsepower(hp) {}
};
```

**Optie B**

```cpp
class Car : public Vehicle {
private:
    int horsepower;
public:
    Car(const string& brand, int hp)
        : Vehicle(brand), horsepower(hp) {}
};
```

---
hideInToc: true
layout: two-cols
---

# Quiz: antwoord

<v-clicks>

- **Optie B is correct.**
- `brand` is een member van `Vehicle`, niet van `Car`
- in de member-initializer-list van `Car` kun je alleen **eigen members** en de
  **basisklasse-constructor** aanspreken
- Optie A probeerde `brand` direct te initialiseren alsof het een member van `Car`
  is -> compiler error
- Optie B roept expliciet `Vehicle(brand)` aan: zo delegeer je de initialisatie
  van `brand` aan de basisklasse
- Dit heet **inheritance**

</v-clicks>

::right::

<br><br>

```cpp
class Vehicle {
protected:
    std::string brand;
public:
    Vehicle(const string& brand)
        : brand(brand) {}
};

// Optie B
class Car : public Vehicle {
private:
    int horsepower;
public:
    Car(const string& brand, int hp)
        : Vehicle(brand), horsepower(hp) {}
};
```

---
layout: two-cols
---

# Inheritance

Wat we net zagen heet **inheritance**, waarmee je een **derived** class laat overerven van een **base** class:

```cpp
class Vehicle {
protected:
    string brand;
public:
    Vehicle(const string& brand)
        : brand(brand) {}
};
```

::right:: 

<br><br><br><br>

```cpp
class Car : public Vehicle {
private:
    int horsepower;

public:
    Car(const std::string& brand, int horsepower) 
		: Vehicle(brand), horsepower(horsepower) {}
};
```
<v-clicks>

- `: public Vehicle` -> `Car` **is-a** `Vehicle`
- `Vehicle(brand)` roept de constructor van de parent aan

</v-clicks>

---
layout: two-cols
hideInToc: true
---

# Inheritance

Als we members gaan toevoegen kan dat bijvoorbeeld zo:

```cpp
class Vehicle {
protected:
    string brand;
public:
    Vehicle(const string& brand)
        : brand(brand) {}

	void print(){
		cout <<"This is a " << brand;
	}
};
```

```
# Vehicle myCar = Vehicle("Toyota");
# myCar.print();
# >>> "This is a Toyota"
```

::right:: 

<br><br><br><br>

```cpp
class Car : public Vehicle {
private:
    int horsepower;

public:
    Car(const std::string& brand, int horsepower) 
		: Vehicle(brand), horsepower(horsepower) {}
};
```
<br>
```
# Car myCar = Car("Honda", 120);
# myCar.print();
# >>> "This is a Honda"
```

<v-click>
Maar we willen die extra informatie natuurlijk ook! Hoe?
</v-click>

---
layout: two-cols
hideInToc: true
---

# Inheritance

Nou, zo:

```cpp
class Vehicle {
protected:
    string brand;
public:
    Vehicle(const string& brand)
        : brand(brand) {}

	virtual void print(){
		cout <<"This is a " << brand;
	}
};
```

```
# Vehicle myCar = Vehicle("Toyota");
# myCar.print();
# >>> "This is a Toyota"
```

::right:: 

<br><br>

````md magic-move
```cpp
class Car : public Vehicle {
private:
    int horsepower;

public:
    Car(const std::string& brand, int horsepower) 
		: Vehicle(brand), horsepower(horsepower) {}

	void print() override {
		cout <<"This is a " << brand;
		cout << " with " << horsepower << " hp!";
	}
};
```

```cpp
class Car : public Vehicle {
private:
    int horsepower;

public:
    Car(const std::string& brand, int horsepower) 
		: Vehicle(brand), horsepower(horsepower) {}

	void print() override {
		Vehicle::print();
		cout << " with " << horsepower << " hp!";
	}
};
```
````

```
# Car myCar = Car("Honda", 120);
# myCar.print();
# >>> "This is a Honda with 120 hp!""
```

<v-click>
Maar we mogen wat we eerder hadden geschreven natuurlijk gewoon hergebruiken :)
</v-click>

---
hideInToc: true
---

# Inheritance; meerdere afgeleide classes

Zelfde principe voor een tweede voertuigtype:

```cpp
class Truck : public Vehicle {
    int horsepower;
public:
    Truck(const std::string& brand, int horsepower)
        : Vehicle(brand), horsepower(horsepower) {}

    void print() override {
        std::cout << brand << " (Truck), horsepower: " << horsepower;
    }

    void getHorsePower() override { return horsepower; };
};
```

<v-click>

`Car` en `Truck` delen dezelfde interface ( `print`, en nu ook `getHorsePower`), maar met eigen
implementatie. 
<br>Dat is **polymorphism**: zelfde interface, ander gedrag.

</v-click>

---

# Polymorphism in de praktijk

Met een array/vector van `Vehicle*` kun je alle voertuigen op dezelfde manier
behandelen, <br>ongeacht hun echte type:

```cpp
std::vector<Vehicle*> vehicles;
vehicles.push_back(new Car("Volkswagen", 150));
vehicles.push_back(new Car("Tesla", 300));
vehicles.push_back(new Truck("Scania", 8000));

int total = 0;
for (Vehicle* v : vehicles) {
    v->print();          // roept Car::print of Truck::print aan
    total += v->getHorsePower();
}
std::cout << "Totaal: " << total << std::endl;
```

<v-click>

Dit werkt alleen correct doordat `getHorsePower` en `print` **virtual** zijn: de
aanroep wordt op basis van het **echte type** (runtime) bepaald, niet op basis van
het pointer-type (`Vehicle*`).

</v-click>

---
hideInToc: true
---

# Polymorphism in de praktijk

Even tussendoor: weten we nog hoe het zat met die `operator->()`? 

````md magic-move
```cpp
std::vector<Vehicle*> vehicles;
vehicles.push_back(new Car("Volkswagen", 150));
vehicles.push_back(new Car("Tesla", 300));
vehicles.push_back(new Truck("Scania", 8000));

int total = 0;
for (Vehicle* v : vehicles) {
    v->print();          // roept Car::print of Truck::print aan
    total += v->getHorsePower();
}
std::cout << "Totaal: " << total << std::endl;
```

```cpp
std::vector<Vehicle*> vehicles;
vehicles.push_back(new Car("Volkswagen", 150));
vehicles.push_back(new Car("Tesla", 300));
vehicles.push_back(new Truck("Scania", 8000));

int total = 0;
for (Vehicle* v : vehicles) {
    (*v).print();          // roept Car::print of Truck::print aan
    total += (*v).getHorsePower();
}
std::cout << "Totaal: " << total << std::endl;
```
````

---

# Destructors

Een destructor ruimt resources op wanneer een object zijn lifetime verliest:

```cpp
class Garage {
    std::vector<Vehicle*> vehicles;
public:
    void addVehicle(Vehicle* v) { vehicles.push_back(v); }

    ~Garage() {
        for (Vehicle* v : vehicles)
            delete v;
    }
};
```

<v-clicks>

- zonder deze destructor: **memory leak**, de `Vehicle`-objects worden nooit vrijgegeven
- `Garage` bezit de voertuigen (ownership), dus `Garage` is verantwoordelijk voor het opruimen

</v-clicks>

---
hideInToc: true
---

# Destructors; het gevaar van niet-virtual

Wat gaat hier mis?

```cpp
class Vehicle {
public:
    ~Vehicle() { std::cout << "Vehicle destroyed" << std::endl; }
};

class Car : public Vehicle {
public:
    ~Car() { std::cout << "Car destroyed" << std::endl; }
};

Vehicle* v = new Car("Volkswagen", 150);
delete v; // wat wordt hier aangeroepen?
```

<v-click>

Alleen `~Vehicle()` wordt aangeroepen: `~Car()` wordt overgeslagen -> resources van
`Car` lekken mogelijk weg.

</v-click>

<v-click>

**Oplossing:** maak de destructor van de basisklasse `virtual`:
`virtual ~Vehicle() = default;`

</v-click>

---
hideInToc: true
---

# Check-in: OOP, Classes, Inheritance, Destructors

<v-clicks>

1. Wat is het verschil tussen `protected` en `private`?
2. Waarom moet `Vehicle` een pure virtual method hebben om abstract te zijn?
3. Waarom werkt polymorphism alleen via pointers/references (`Vehicle*`), niet via directe objecten?
4. Wat gaat er mis als een basisklasse-destructor niet `virtual` is?

</v-clicks>

<!--
Kernantwoorden:
1) protected: toegankelijk voor de class + afgeleide classes. private: alleen de class zelf.
2) Pure virtual (`= 0`) betekent: geen implementatie, class kan niet geïnstantieerd worden totdat een afgeleide class het invult.
3) Object slicing: bij directe objecten (by value) wordt alleen het Vehicle-deel gekopieerd, het afgeleide-type gaat verloren.
4) Alleen de destructor van het statische (pointer-)type wordt aangeroepen; de destructor van het echte (afgeleide) type wordt overgeslagen -> resource leaks.
-->

---
layout: center
hideInToc: true
---

# \<br>

Daarna:

# Templates

---

# Templates

Stel je wil een functie die de grootste van twee waarden teruggeeft, <br>voor
verschillende types (`int`, `double`, ...).

````md magic-move
```cpp
// Zonder templates -> voor elk type een aparte overload

int maxValue(int a, int b){
	return (a > b)? a : b;
}

double maxValue(int a, int b){
	return (a > b)? a : b;
}
```

```cpp
// Maar met templates:

template<typename T>
T maxValue(T a, T b) {
    return (a > b) ? a : b;
}

maxValue(3, 7);        // T = int
maxValue(3.5, 2.1);     // T = double
maxValue<std::string>("abc", "abd"); // T = std::string
```
````


<v-click>

De compiler genereert bij elke aanroep automatisch de juiste versie voor `T`.

</v-click>

---
hideInToc: true
---

# Templates; hoe werkt dit?

```text
maxValue(3, 7)
```

<v-clicks>

- de compiler ziet: `T = int`
- op compile time wordt een versie van `maxValue` gegenereerd voor `int`
- dit heet **template instantiation**

</v-clicks>

<br>

<v-click>

Voordeel: type-veilig én herbruikbaar

</v-click>

---

# Template specialization

Wat gebeurt er met `const char*`?

```cpp
maxValue("banaan", "appel");   // T = const char*
```

<v-click>

Standaard vergelijkt `a > b` de **adressen** van de strings, niet de inhoud. Dat is
vrijwel nooit wat je bedoelt.

</v-click>

<v-click>

**Oplossing:** een **template specialization** voor `const char*`:

```cpp
template<>
const char* maxValue<const char*>(const char* a, const char* b) {
    return (strcmp(a, b) > 0) ? a : b;
}
```

</v-click>

<v-click>

Zelfde naam en interface, maar voor dit specifieke type een aangepaste
implementatie die wél de inhoud vergelijkt.

</v-click>

---
hideInToc: true
---

# Template specialization; wanneer?

<v-clicks>

- het generieke template-gedrag is **incorrect** of **onlogisch** voor een specifiek type
- je wil een **geoptimaliseerde** implementatie voor een specifiek type
- vuistregel: schrijf eerst de generieke versie, specialiseer pas als een type
  problemen geeft

</v-clicks>

<br>

<v-click>

Zelfde patroon geldt trouwens ook voor class templates (niet alleen function
templates)

</v-click>

---
hideInToc: true
---

# Check-in: Templates

<v-clicks>

1. Wat genereert de compiler bij een template instantiation?
2. Waarom werkt de generieke `maxValue` niet correct voor `const char*`?
3. Wat is het verschil tussen een normale overload en een template specialization?

</v-clicks>

<!--
Kernantwoorden:
1) Een concrete versie van de functie/class voor het specifieke type T, op compile time.
2) Omdat `a > b` op pointers de adressen vergelijkt, niet de string-inhoud; daarvoor heb je strcmp nodig.
3) Een specialization deelt exact dezelfde template-naam/interface maar levert een aangepaste implementatie voor één specifiek type; een overload is een losse functie met een andere signature.
-->

---
hideInToc: true
---

# Afsluiting

- classes bundelen data en gedrag -> encapsulation en abstraction
- inheritance + virtual methods maken polymorphism mogelijk
- vergeet de **virtual destructor** niet bij polymorf gebruik van een basisklasse
- templates geven type-veilige herbruikbaarheid; specialization voor de uitzonderingen

Volgende stap: hierop bouwen we voort met design patterns, geavanceerdere templates
en lambda's.
