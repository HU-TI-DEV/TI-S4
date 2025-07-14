---
title: Advanced Templates & Compile-Time Techniques
output: ../software/cpp/templates_en_compiletime.pdf
theme: ./slidev-theme-ti
---

<!-- Deze les behandelt functionele templates en specialisaties, variadic templates, SFINAE en if constexpr, constexpr/consteval en de introductie van type traits en concepts. We gebruiken een logger als doorlopend voorbeeld. -->

# Overzicht Les

- **Types**
- **Templates**
- **Variadic Templates**
- **SFINAE & if constexpr**
- **Constexpr / Consteval**
- **Type Traits & Concepts (C++20)** 

<!-- Overzicht van de onderwerpen die we vandaag behandelen. -->

---
layout: two-cols
---

# Types

**C++ (Statisch)**
- Types zijn compile-time vastgelegd
- Fouten worden vaak al tijdens compilatie ontdekt
- Templates genereren voor elk type een aparte instantie

```cpp
#include <iostream>

int main() {
    int a = 5;
    a = "Hello"; // Error
    std::cout << "a: " << a << "\n";
    return 0;
}
```

::right::

# <br>

**Python (Dynamisch)**
- Types worden pas tijdens runtime bepaald
- Flexibeler, maar typefouten kunnen later optreden
- Gebruik van `type()` en duck typing

```python
def print_value(x):
    print("Value:", x)
    print("Type:", type(x))

print_value(5)
print_value("Hello")
```

<!--
Leg uit dat C++ strikt type-veilig is door compile-time type-checking, terwijl Python flexibel is maar potentieel voor runtime fouten biedt. En dat we python voorbeeldjes er naast gaan houden voor snapvermogen
-->

---
layout: two-cols
---

# Templates

**Bepaal max van twee integers**

````md magic-move

```cpp
int max(int a, int b) {
    if (a > b) {
        return a;
    } else {
        return b;
    }
}

int max2(int a, int b) {
    return a > b ? a : b;
}
```

```cpp


float max2(float a, float b) {
    return a > b ? a : b;
}

std::string max2(std::string a,
                 std::string b) {
    return a > b ? a : b;
}

gz::math::Color max2(gz::math::Color a,
                     gz::math::Color b) {
    return a > b ? a : b;
}
```

````

::right::

# <br>

**<br>**

```python
def max(a, b):
    return a if a > b else b
```

---
layout: two-cols
---

# Functie templates

**Bepaal max van twee integers**
````md magic-move

```cpp
template <typename T>
T max(T a, T b) {
    return a > b ? a : b;
}

std::cout << max(11, 12) << "\n";
std::cout << max(2.71828, 3.14159) << "\n";
std::cout << max(gz::math::Color::Blue,
                 gz::math::Color(0.3, 0.4, 0.5)
             )
          << "\n";
```

```cpp
auto max(auto a, auto b) {
    return a > b ? a : b;
}

std::cout << max(11, 12) << "\n";
std::cout << max(2.71828, 3.14159) << "\n";
std::cout << max(gz::math::Color::Blue,
                 gz::math::Color(0.3, 0.4, 0.5)
             )
          << "\n";
```

````

::right::

# <br>

**<br>**

```python
def max(a, b):
    return a if a > b else b
```

---

# Functie templates gebruik

```cpp
template <typename T>
T max(T a, T b) {
    return a > b ? a : b;
}

std::cout << max<float>(42, 6.5) << "\n";
std::cout << max<int>(2.71828, 3.14159) << "\n";
std::cout << max(gz::math::Color::Blue,
                 gz::math::Color(0.3, 0.4, 0.5)
             )
          << "\n";
```

Je *kan* zelf template parameters opgeven.

(Er zitten overigens prima min en max in
`<algorithm>`, de STL les volgt later)

Elke template instantiatie is zijn eigen ding, daarom moeten ze in een header staan: https://godbolt.org/z/jY8sWMajn

---
layout: center
---

**Voordelen/Nadelen**

<v-clicks>

- Specifieke optimalisaties per type
- Kan leiden tot code bloat als er veel instanties worden aangemaakt

</v-clicks>

---
layout: two-cols
---

# Class templates & Template Value Parameters

- C++ templates kunnen niet alleen types, maar ook waarden als parameters nemen
- Voorbeeld: Het definiëren van een array met vaste grootte

```cpp
template<typename T, std::size_t N>
struct Array {
    T data[N];
};
```

https://godbolt.org/z/7hxjf5odq

::right::

**Gebruik**

`Array<int, 10>` definieert een array van 10 integers.

**Voordeel**
- Compile-time vastgelegde constante waarden kunnen maximaal geoptimaliseerd worden
  
**Toepassing**
- Gebruikt in containers zoals `std::array`.



<!-- Speaker notes: Bespreek dat template value parameters zorgen voor extra typeveiligheid en optimalisaties doordat de grootte en andere constanten al tijdens compilatie bekend zijn. -->

---

# vector\<bool>

- `std::vector<bool>` is een bekende specialisatie in de STL
- In plaats van een array van booleans (1 byte per bool) wordt een bit-packed representatie gebruikt

```cpp
template<typename T, std::size_t N>
class Array {
    T data[N];
};

template <std::size_t N>
class Array<bool, N> {
    unsigned char data[(N + 7) / 8];

    bool get(std::size_t i) const {
        return ((data[i / 8] >> (i % 8)) & 1) != 0;
    }

    void set(std::size_t i, bool b){
        if (b) {
            data[i / 8] |=  (1 << (i % 8));
        } else {
            data[i / 8] &= ~(1 << (i % 8));
        }
    }
};

```


<!-- Speaker notes: Bespreek dat deze specialisatie voordelen biedt in geheugenbesparing, maar dat het ook beperkingen met zich meebrengt in termen van interface en performance bij bitbewerkingen. -->

---

<!-- We beginnen met de basis van functie templates en hoe we deze kunnen specialiseren. -->

# Functie Templates & Specialisaties

```cpp
#include <iostream>

// Algemene template voor logging
template<typename T>
void log(const T& value) {
    std::cout << "Log: " << value << "\n";
}

// Specialisatie voor C-strings (const char*)
template<>
void log<const char *>(const char * const value) {
    std::cout << "Log (C-string): " << value << "\n";
}
```


---

<!-- Hier zien we hoe een generieke log-functie voor elk type kan werken, en hoe we via specialisatie een aangepaste implementatie voor C-strings aanbieden. -->

<!-- Nu introduceren we variadic templates om een logger te maken die meerdere argumenten kan verwerken. -->

# Variadic Templates: Logger voor Meerdere Argumenten

```cpp
#include <iostream>

template <typename... Args>
void log(Args&&... args) {
    (std::cout << ... << args) << '\n';
}
 
```

https://godbolt.org/z/hhfEen3sE

https://en.cppreference.com/w/cpp/language/parameter_pack.html

https://en.cppreference.com/w/cpp/language/fold


---
layout: center
---

# \<br>

---
zoom: .8
---

# SFINAE voorbeeld

```cpp
template<typename T>
struct is_integral_manual {
    static constexpr bool value = false;
};

template<> struct is_integral_manual<int> { static constexpr bool value = true; };
template<> struct is_integral_manual<unsigned long> { static constexpr bool value = true; };

template<bool isIntegral, typename T>
struct log_sfinae_helper;

template<typename T>
struct log_sfinae_helper<true, T> {
    static void log(const T& value) {
        std::cout << "Integral value: " << value << "\n";
    }
};

template<typename T>
struct log_sfinae_helper<false, T> {
    static void log(const T&) {
        std::cout << "Non-integral value\n";
    }
};

template<typename T>
void log_sfinae(const T& value) {
    log_sfinae_helper<is_integral_manual<T>::value, T>::log(value);
}
```

---

# SFINAE & if constexpr: Conditieel Compileren

```cpp
template <bool B, class T = void>
struct enable_if {};
 
template <class T>
struct enable_if<true, T> { using type = T; };

template <bool B, class T = void >
using enable_if_t = typename enable_if<B, T>::type;
```

---

# SFINAE & if constexpr: Conditieel Compileren

https://godbolt.org/z/MfP6ajM6n

```cpp
#include <iostream>
#include <type_traits>

template<typename T>
void log_if(const T& value) {
    if constexpr (std::is_arithmetic_v<T>) {
        std::cout << "Arithmetic: " << value << "\n";
    } else {
        std::cout << "Non-arithmetic type\n";
    }
}

template<typename T>
auto log_sfinae(const T& value) -> std::enable_if_t<std::is_integral_v<T>> {
    std::cout << "Integral value: " << value << "\n";
}

template<typename T>
auto log_sfinae(const T& value) -> std::enable_if_t<!std::is_integral_v<T>> {
    std::cout << "Non-integral value\n";
}
```

<!-- Met if constexpr evalueren we op compile-time of een type aritmetisch is. SFINAE (Substitution Failure Is Not An Error) helpt bij het kiezen van de juiste overload op basis van type-eigenschappen. -->

---

<!-- Tot slot introduceren we type traits en concepts om template parameters expliciet te specificeren. -->

# Type Traits & Concepts: Template Requirements

```cpp
#include <concepts>
#include <iostream>

// Definieer een concept dat vereist dat een type streamable is
template<typename T>
concept Streamable = requires(T a, std::ostream& os) {
    { os << a } -> std::convertible_to<std::ostream&>;
};

// Logfunctie met concept restrictie
template <Streamable T>
void log_concept(const T& value) {
    std::cout << "Concept log: " << value << "\n";
}
```

https://godbolt.org/z/GY5vbM5cn


<!-- Concepts maken onze templates explicieter en veiliger door compile-time eisen te stellen aan de types. We definiëren een 'Streamable' concept en gebruiken dit om een logfunctie te beperken tot types die gestreamd kunnen worden. -->


---
layout: center
---

# \0
