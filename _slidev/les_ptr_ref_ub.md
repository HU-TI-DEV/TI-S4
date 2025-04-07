---
theme: ./slidev-theme-ti
output: ../software/cpp/ptr_ref_ub.pdf
hideInToc: true
---

# Pointers, References, Undefined Behaviour

---
layout: table-of-contents
hideInToc: true
---

# Programma

---

# Undefined Behaviour; wat?

Wat is de uitkomst van het volgende stukje code?

````md magic-move
```cpp
int func(int k){
    return k+10;
}

int x = 12;
std::cout << func(x) << std::endl;
```

```cpp
int func(int k){
    return k+10;
}

int x = INT_MAX;
std::cout << func(x) << std::endl;
```
````

---
hideInToc: true
---

# Zijstapje; C-style array voor strings

```cpp
char[] t = "Hallo";

char* t = "Hallo";

void printSomething(char* p){printf("p: %s",p);}
```

---
hideInToc: true
---

# Undefined Behaviour; wat?

Wat is de uitkomst van het volgende stukje code?

````md magic-move
```cpp
char t[] = "Hallo";
t[1] = 'e';
```

```cpp
char *t = "Hallo";
t[1] = 'e';
```

```cpp
char t[] = "Hallo";
t[6] = '!';
```
````

---
hideInToc: true
---

# Undefined Behaviour; wat?

<v-clicks>

- Elke taal heeft beschreven gedrag
- Soms kan code wel compileren, maar is gedrag niet beschreven; Undefined
- Gedrag van code is niet te voorspellen; Undefined Behaviour
<br><br><br>
- (Uitkomst van) code onbruikbaar?

</v-clicks>

---

# Undefined Behaviour; het echte gevaar

- UB _ergens_ in je programma maakt het hele programma undefined
- Volgens de standaard: UB komt niet voor, dus mogen het negeren

<br>

Bijvoorbeeld: Signed Integer Overflow

````md magic-move
```cpp
bool f(int i) { return i+1 > 1; }
```

```cpp
bool f(int i) { return i+1 > 1; }

bool g(int i) {
    if (i == INT_MAX) return false;
    else return f(i);
}
```

```cpp
bool g(int i){ return true; }
```

```asm
f:
mov $0x1, %eax
retq

g:
mov $0x1, %eax
retq
```
```` 

---
hideInToc: true
---

# Undefined Behaviour; wat?

Voorbeelden:

- Signed integer overflow
- Array indexing buiten bounds
- Zero division
- Dereferencing null ptr
- Gebruik van objecten na lifetime

---
layout: two-cols
---

# Unspecified Behaviour; huh?

En ook; Implementation-defined behaviour. Verschil? Documentatie.

Unspecified behaviour:

- Hóeft niet gedocumenteerd te worden
- Order of Evaluation
```cpp
void f(int a, int b, int c){ ... }

int x = 12;
f(x, x++, x+20);
```

- String Literal Comparison

```cpp
char[] t = "Hallo";

std::cout << t == "Hallo" << std::endl;
```

::right::

<br><br><br><br>

Implementation defined behaviour:

- Móet wel gedocumenteerd worden
- Waarde van std::sizeof(int);
    - 32- of 64-bit
- Uit hoeveel bits een byte bestaat
    - Mééstal 8, maar niet altijd! 

---
layout: center
hideInToc: true
---

# \<br>

---
layout: end
---
