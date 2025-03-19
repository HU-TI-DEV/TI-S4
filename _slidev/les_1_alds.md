---
title: Complexiteit en Algoritmes
output: ../software/algoritmen_en_datastrucuren/1_complexiteit_en_algoritmes.pdf
theme: ./slidev-theme-ti
---

# Overzicht Les

- **Complexiteit**
- **Wat is een algoritme?**
- **Vergelijking C++/Python**

---

layout: two-cols
---

# Twee algoritmes, welke is beter?

```python
def max1(int_array):
    result = int_array[0]
    for x in int_array:
        if x > result:
            result = x
    return result
```

::right::

# <br>

```python
def max2(int_array):
    for x in int_array:
        is_max = True
        for y in int_array:
            if y > x:
                is_max = False
                break
        if is_max:
            return x
```

---

# Twee algoritmes, welke is beter?

Ik zeg:
- Max1 is beter, want je ziet toch dat het sneller is?

Maar wat bedoelen we precies met "beter"?
- **Runtime:** Hoe snel het algoritme werkt bij groeiende input.
- **Programmeertaal en Compiler:** De efficiëntie kan afhangen van de taal en optimalisaties.
- **Implementatie:** Kleine verschillen in implementatie (bijv. gebruik van iterators vs. indexering) kunnen effect hebben.

---

# Twee algoritmes, welke is beter?

Kunnen we dat kwantificeren?

- We kunnen meten hoeveel CPU-instructies er uitgevoerd worden.
- Maar belangrijker is de asymptotische groei, hoeveel X langzamer wordt mijn functie als de input veranderd.
- Dit vertelt ons hoe het algoritme schaalt als de inputgrootte toeneemt.

---

# Het betere algoritme

Wat boeit ons echt?
Hoe snel wordt de runtime groter naarmate de input toeneemt?

- **Constante factoren** worden in de Big‑O notatie genegeerd.
- We richten ons op de **worst-case** performance.
- Dit is essentieel voor grote inputs, waar de groeiende factor bepalend is.

---

# Het betere algoritme

Om de efficiëntie van een algoritme te bepalen:

- Analyseer de **worst-case** scenario's.
- Vergelijk de orde van groei:
  - O(1) is constant.
  - O(N) groeit lineair.
  - O(N²) groeit kwadratisch.

Deze abstractie helpt ons te bepalen welk algoritme beter schaalt, ongeacht de precieze constante factoren.

---

# Tijd complexiteit

Big‑O notatie geeft een abstracte maat voor de groei van de runtime als functie van de inputgrootte:

- **O(1):** Constante tijd
- **O(N):** Lineaire tijd
- **O(N²):** Kwadratische tijd
- **O(log N):** Logaritmische tijd
- **O(N log N):** Linearitmische tijd
- **O(2^N):** Exponentiële tijd
- **O(N!):** Faculteit tijd

Kleine optimalisaties of constante overhead tellen niet mee. We kijken naar de orde van de groei.

---
layout: two-cols
---

# Voorbeeld O(N) - Lineair

**C++:**

```cpp
#include <vector>
#include <iostream>

int sumElements(const std::vector<int>& vec) {
    int sum = 0;
    for (int x : vec) {
        sum += x;
    }
    return sum;
}

int main() {
    std::vector<int> v = {1, 2, 3, 4, 5};
    std::cout << "Sum: " << sumElements(v) << "\n";
    return 0;
}
```
::right::

# <br>

**Python:**

```python
def sum_elements(lst):
    total = 0
    for x in lst:
        total += x
    return total

lst = [1, 2, 3, 4, 5]
print("Sum:", sum_elements(lst))
```

---
layout: two-cols
---

# Voorbeeld O(N²) - Bubble Sort


**C++:**

```cpp
#include <vector>
#include <iostream>
#include <algorithm>

void bubbleSort(std::vector<int>& vec) {
    int n = vec.size();
    for (int i = 0; i < n - 1; ++i) {
        for (int j = 0; j < n - i - 1; ++j) {
            if (vec[j] > vec[j+1]) {
                std::swap(vec[j], vec[j+1]);
            }
        }
    }
}

int main() {
    std::vector<int> v = {5, 2, 9, 1, 5, 6};
    bubbleSort(v);
    for (int x : v) {
        std::cout << x << " ";
    }
    std::cout << "\n";
    return 0;
}
```

::right::

# <br>

**Python:**

```python
def bubble_sort(lst):
    n = len(lst)
    for i in range(n):
        for j in range(0, n - i - 1):
            if lst[j] > lst[j+1]:
                lst[j], lst[j+1] = lst[j+1], lst[j]
    return lst

lst = [5, 2, 9, 1, 5, 6]
print("Sorted:", bubble_sort(lst))
```

---
layout: two-cols
---

# Voorbeeld O(log N) - Binary Search

**C++:**

```cpp
#include <vector>
#include <iostream>

int binarySearch(const std::vector<int>& vec, int target) {
    int low = 0, high = vec.size() - 1;
    while (low <= high) {
        int mid = low + (high - low) / 2;
        if (vec[mid] == target) {
            return mid;
        } else if (vec[mid] < target) {
            low = mid + 1;
        } else {
            high = mid - 1;
        }
    }
    return -1;
}

int main() {
    std::vector<int> v = {1, 3, 5, 7, 9, 11};
    int target = 7;
    int index = binarySearch(v, target);
    std::cout << "Index of " << target << " is " << index << "\n";
    return 0;
}
```

::right::

# <br>

**Python:**

```python
def binary_search(lst, target):
    low, high = 0, len(lst)-1
    while low <= high:
        mid = (low + high) // 2
        if lst[mid] == target:
            return mid
        elif lst[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

lst = [1, 3, 5, 7, 9, 11]
target = 7
print("Index:", binary_search(lst, target))
```

---
layout: center
---
<!-- Break slide! -->
# \<br>

---
layout: two-cols
---

# STL Huiswerk Terugblik

- Lees alle karakters van deze file in, sla op in een geschikte container
- Tel en print hoeveel karakters de file bevat

```cpp
std::ifstream ifs{"bee.txt"};
std::string text{std::istreambuf_iterator<char>{ifs},
                 std::istreambuf_iterator<char>{}};

std::println("Aantal karakters: {}", text.size());
```

::right::

# <br>

```python
with open('bee.txt') as f:
    text = f.read()

print('Aantal karakters:', len(text))
```

<!-- Lees alle karakters van deze file in, sla op in een geschikte container
    Complexity CPP: O(N)
    Complexity Python: O(N)
Korte onderbouwing: In C++ wordt de hele file in één pass ingelezen via de istreambuf_iterator, en in Python leest f.read() de file volledig in één string, beide opereren in lineaire tijd met betrekking tot het aantal karakters.

Tel en print hoeveel karakters de file bevat
    Complexity CPP: O(1)
    Complexity Python: O(1)
Korte onderbouwing: Zowel in C++ (`std::string.size()`) als in Python (`len(text)`) kost het tellen van karakters O(1), omdat de lengte al bekend is na het inlezen (wat zelf O(N) was).
-->

---
layout: two-cols
---

# STL Huiswerk Terugblik

- Print hoeveel regels de file bevat
- Print hoeveel alfabetische karacters de file bevat

```cpp
auto line_count = ranges::count(text, '\n');
std::println("Aantal regels: {}", line_count);

auto alpha_count = ranges::count_if(text, [](unsigned char c) {
    return std::isalpha(c);
});
std::println("Aantal alfabetische karakters: {}", alpha_count);
```

::right::

# <br>

```python
print('Aantal regels:', text.count('\n'))

print('Aantal alphabetische karakters:',
      sum(c.isalpha() for c in text))
```

<!-- Tel en print hoeveel regels de file bevat en hoeveel alfabetische karakters de file bevat
    Complexity CPP: O(N)
    Complexity Python: O(N)
Korte onderbouwing: Beide operaties vereisen een enkele iteratie over alle karakters in de tekst (door te zoeken naar '\n' en het toepassen van isalpha), wat resulteert in een lineaire tijdscomplexiteit.
-->

---
layout: two-cols
---

# STL Huiswerk Terugblik

- Print of de file alleen maar letters en leestekens bevat
- Zet alle letters in de container om in kleine letters

```cpp
bool only_valid = ranges::all_of(text, [](unsigned char c) {
    return std::isprint(c) || std::isspace(c);
});
std::println("Bevat de file alleen letters, spaties en leestekens? {}",
             only_valid ? "Ja" : "Nee");

for (char& c : text) c = std::tolower(c);
```

::right::

# <br>

```python
print('Bevat de file alleen letters, spaties en leestekens?',
      all(c.isprintable() or c.isspace() for c in text))

text = text.lower()
```

<!-- Print of de file alleen maar letters, spaties en leestekens bevat en zet alle letters om in kleine letters
    Complexity CPP: O(N)
    Complexity Python: O(N)
Korte onderbouwing: Het controleren van elk karakter op printbaarheid (of whitespace) en het converteren naar kleine letters vereist dat elk karakter één keer wordt bekeken, wat resulteert in O(N) tijd.
-->

---
layout: two-cols
---

# STL Huiswerk Terugblik

- Tel in een geschikte container voor iedere letter (a..z) hoe vaak deze voorkomt in de tekst
    Druk deze container af:
        gesorteerd op lettervolgorde
        gesorteerd op hoe vaak een letter voorkomt

```cpp
std::vector letter_freq(std::from_range, views::iota('a', 'z' + 1)
    | views::transform([&](char l) { return std::pair{l, size_t{0}}; }));

for (char c : text 
            | views::filter([](unsigned char c){ return std::islower(c); }))
    letter_freq[c - 'a'].second++;

// gesorteerd op lettervolgorde
std::println("\nLetterfrequentie (alfabetische volgorde):");
for (const auto &p : letter_freq)
    std::println("{}: {}", p.first, p.second);

// gesorteerd op hoe vaak een letter voorkomt
ranges::sort(letter_freq, {}, &std::pair<char, size_t>::second);

std::println("\nLetterfrequentie (oplopend):");
for (const auto& p : letter_freq)
    std::println("{}: {}", p.first, p.second);
```

::right::

# <br>

```python
frequencies = {c: text.count(c) for c in ascii_lowercase}
print('\nLetterfrequentie (alphabetische volgorde):')
for c in ascii_lowercase:
    print(c, frequencies[c], sep=': ')

print('\nLetterfrequentie (oplopend):')
for c, freq in sorted(frequencies.items(), key=lambda x: x[1]):
    print(c, freq, sep=': ')
```

<!-- Tel in een geschikte container voor iedere letter (a..z) hoe vaak deze voorkomt in de tekst en druk dit af
    Complexity CPP: O(N)
    Complexity Python: O(N) (met een constante factor van 26)
Korte onderbouwing: In C++ wordt de tekst in één pass doorlopen en voor elk karakter de frequentie geüpdatet. In Python wordt voor elke van de 26 letters de count()-functie aangeroepen, wat resulteert in 26 * O(N) = O(N) (aangezien 26 een constante is).
-->


---
layout: two-cols
---

# STL Huiswerk Terugblik

- Bepaal welke woorden er in de tekst voorkomen
 - Druk de 10 meest voorkomende woorden af

```cpp
const auto is_word_char = [](char c) { return std::isalpha(c) || c == '\''; };

auto words_view = text
    | views::chunk_by([&](auto a, auto b) {return is_word_char(a) == is_word_char(b);})
    | views::filter([](auto r) { return std::isalpha(r[0]); })
    | views::transform([](auto r) { return std::string_view(r); });

std::unordered_map<std::string_view, size_t> word_freq;
for (const auto word : words_view) ++word_freq[word];

const size_t top_n{10};

std::vector<std::pair<std::string_view, size_t>> top_words(std::from_range, word_freq);
ranges::partial_sort(top_words, top_words.begin() + top_n, ranges::greater{}, &std::pair<std::string_view, size_t>::second);

std::println("\nTop {} meest voorkomende woorden:", top_n);
for (const auto [word, freq] : top_words | views::take(top_n))
    std::println("{:>10} : {:5}", word, freq);
```

::right::

# <br>

```python
top_n = 10
print(f'\nTop {top_n} meest voorkomende woorden:')
words = text.split()
word_frequencies = {word: words.count(word) for word in set(words)}
for word, freq in sorted(word_frequencies.items(), key=lambda x: x[1], reverse=True)[:top_n]:
    print(f'{word:>10} : {freq>5}')
```

<!-- Bepaal welke woorden er in de tekst voorkomen en druk de 10 meest voorkomende woorden af
    Complexity CPP: O(N) + O(W log(W)) (waarbij W het aantal woorden is)
    Complexity Python: O(N*K) in het slechtste geval (waarbij K het aantal unieke woorden is), maar doorgaans O(N) als K relatief klein blijft
Korte onderbouwing: In C++ wordt de tekst eerst lineair gescand om woorden te extraheren (O(N)) en vervolgens worden de frequenties geteld, waarna een gedeeltelijke sortering plaatsvindt. In Python splitst text.split() de tekst in O(N) en worden voor elke unieke woordfrequentie de count()-aanroepen uitgevoerd, wat de overhead kan verhogen als het aantal unieke woorden groot is.
-->

---

# Huiswerk

ALDS opdracht notebook

---
layout: center
hideInToc: true
---

# \0


