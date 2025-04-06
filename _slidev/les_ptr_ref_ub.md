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

x = 12;
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

# Undefined Behaviour; wat?

<v-clicks>

- Elke taal heeft beschreven gedrag
- Soms kan code wel compileren, maar is gedrag niet beschreven
- Soms beschrijven compiler bouwers hoe de code werkt voor hun compiler..
- Uitkomst van code is niet te voorspellen; Undefined Behaviour (**UB**)
- Uitkomst van code onbruikbaar?

</v-clicks>

---

# Undefined Behaviour; wat?

Voorbeelden:

- Array indexing buiten bounds
- Zero division
- Signed integer overflow
- Dereferencing null ptr
- Gebruik van objecten na lifetime


---
layout: two-cols
---

# Unspecified Behaviour; huh?

En ook; Implementation-defined behaviour

Verschil? Documentatie.

Unspecified:

- Order of Evaluation
- String Literal Comparison

::right::

Implementation defined:

- Type van std::size_t
- Uit hoeveel bytes bepaalde typen bestaan

---

