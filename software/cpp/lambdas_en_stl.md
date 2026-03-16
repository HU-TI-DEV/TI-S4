# Lambdas en STL
Link naar presentatie: [\[&\]( )->auto{} en STL](lambdas_en_stl.pdf)
Hieronder staan wat oefeningen waarmee je lambdas en STL functies kan oefenen.

# Oefening 1 – Filteren en Sorteren

Je krijgt:

```cpp
std::vector<int> numbers { 12, 5, 8, 130, 44, 3, 15, 67 };
```

Taken:

1. Verwijder alle getallen kleiner dan 10.
2. Sorteer de overblijvende getallen in dalende volgorde.
3. Print ze met `std::for_each`.

Vereiste algoritmen:
- `remove_if`
- `sort`
- `for_each`

---

# Oefening 2 – Eerste overeenkomst vinden

Je hebt:

```cpp
struct User {
    std::string name;
    int age;
};
```

En:

```cpp
std::vector<User> users {
    {"Alice", 22},
    {"Bob", 17},
    {"Charlie", 35},
    {"Diana", 15}
};
```

Taken:

1. Gebruik `find_if` om de eerste gebruiker jonger dan 18 te vinden.
2. Print zijn/haar naam.
3. Als er geen gevonden wordt, print "Geen minderjarigen".

Gebruik geen lussen.

---

# Oefening 3 – Capture by Value vs Reference

Je krijgt:

```cpp
std::vector<int> v {1, 2, 3, 4, 5};
int threshold = 3;
```

Taken:

1. Tel hoeveel getallen groter zijn dan `threshold` met `count_if`.
2. Verander daarna `threshold` naar 4.
3. Voer dezelfde `count_if` opnieuw uit:
   - Eerst met capture by value
   - Daarna met capture by reference

Observeer het verschil.

---

# Oefening 4 – Verwijderen op basis van externe conditie

Je hebt:

```cpp
std::vector<std::string> words {
    "apple", "banana", "kiwi", "pear", "watermelon"
};
size_t minLength = 5;
```

Taak:

Verwijder alle woorden korter dan `minLength`.

Je moet `minLength` capturen in de lambda.

---

# Oefening 5 – Aangepast sorteren

Gegeven:

```cpp
std::vector<std::string> words {
    "apple", "kiwi", "banana", "pear", "fig"
};
```

Taken:

1. Sorteer op lengte van de string (oplopend).
2. Als de lengtes gelijk zijn, sorteer alfabetisch.

Gebruik een custom comparator lambda.

---

# Oefening 6 – Transform + Remove

Gegeven:

```cpp
std::vector<int> nums {1,2,3,4,5,6,7,8,9};
```

Taken:

1. Maak een nieuwe vector met het kwadraat van elk getal via `transform`.
2. Verwijder alle gekwadrateerde getallen groter dan 30 met `remove_if`.

---

# Oefening 7 – Interviewstijl

Je hebt:

```cpp
struct Transaction {
    std::string id;
    double amount;
};
```

En:

```cpp
std::vector<Transaction> txs {
    {"T1", 120.5},
    {"T2", -50.0},
    {"T3", 75.0},
    {"T4", -10.0}
};
```

Taken:

1. Verwijder alle transacties met een negatief bedrag.
2. Sorteer de overblijvende transacties dalend op bedrag.
3. Bereken het totale bedrag met `accumulate`.

Gebruik geen manuele lussen.

---

# Oefening 8 – Partition vs Remove

Gegeven:

```cpp
std::vector<int> v {1,2,3,4,5,6,7,8,9};
```

Taken:

1. Gebruik `partition` om alle even getallen naar voren te verplaatsen.
2. Print de vector.
3. Vergelijk dit met het effectief verwijderen van oneven getallen met `remove_if`.

Begrijp het verschil:
- `partition` herschikt elementen
- `remove_if` verwijdert elementen (met erase)

---

# Uitdaging

Gegeven een vector van integers:

1. Verwijder duplicaten (gebruik geen `std::set`)
2. Verwijder alle even getallen
3. Sorteer dalend
4. Print de kwadraten

Je mag enkel STL-algoritmen gebruiken.
