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

- Elke taal heeft **beschreven gedrag**
- Soms kan code wel compileren, maar is **gedrag niet beschreven**; Undefined
- Gedrag van code is **niet te voorspellen**; Undefined Behaviour
<br><br><br>
- (Uitkomst van) code onbruikbaar?

</v-clicks>

---

# Undefined Behaviour; het echte gevaar

- UB **_ergens_** in je programma maakt het hele programma undefined
- Volgens de standaard: UB komt niet voor, dus mogen het negeren

<br>

Bijvoorbeeld: Signed Integer Overflow

````md magic-move
```cpp
bool f(int i) { 
    return i+1 > i; 
}
```

```cpp
bool f(int i) { 
    return i+1 > i; 
}

bool g(int i) {
    if (i == INT_MAX) return false;
    else return f(i);
}
```

```cpp
bool g(int i){ return true; }
```

```cpp
                                        //| x86 ASM
bool f(int i) {                         //| f:
    return i+1 > i;                     //| mov $0x1, %eax
}                                       //| retq
                                        //|
bool g(int i) {                         //| g:
    if (i == INT_MAX) return false;     //| mov $0x1, %eax
    else return f(i);                   //| retq
}                                       //|
```
````

---
hideInToc: true
---

# Undefined Behaviour; het echte gevaar

- UB **_ergens_** in je programma maakt het hele programma undefined
- Volgens de standaard: UB komt niet voor, dus mogen het negeren

<br>

Bijvoorbeeld: Signed Integer Overflow

````md magic-move
```cpp
void read_from_network(int size) {
    // Catch integer overflow.
    //
    if (size > size+1) errx(1, "packet too big");

    char *buf = malloc(size+1);
    if (buf == NULL)
    errx(1, "out of memory");

    read(fd, buf, size);
    // ... error checking on read.

    buf[size] = 0;
    process_packet(buf);
    free(buf);
}
```

```cpp
void read_from_network(int size) {
    // size > size+1 is impossible since signed
    // overflow is impossible. Optimize it out!
    // if (size > size+1) errx(1, "packet too big");

    char *buf = malloc(size+1);
    if (buf == NULL)
    errx(1, "out of memory");

    read(fd, buf, size);
    // ... error checking on read.

    buf[size] = 0;
    process_packet(buf);
    free(buf);
}
```
```` 

---
hideInToc: true
---

# Undefined Behaviour; het echte gevaar

- Probleem: Security Audits zien dit snel over het hoofd
- Hoe check je dan wel op signed integer overflow?
- Vóórdat je iets aanpast

```cpp
int a = <something>;
int x = <something>;
if (x > 0 && a > INT_MAX - x) { ... } // `a + x` would overflow
```

<v-click>

In het algemeen:
- Ja, je code werkt **nu** misschien
- Maar morgen nog? Op andere architectuur? Andere compiler?

</v-click>

---
hideInToc: true
---

# Undefined Behaviour; wat?

Voorbeelden:

- Signed integer overflow
- Out of bounds memory access
- Zero division
- Gebruik van ongeïnitialiseerde variabele
- Dereferencing null ptr
- Gebruik van objecten na lifetime

<br>

- En meer.. Helaas..
- Oplossingen zijn specifiek per geval

---
layout: two-cols
---

# Unspecified Behaviour; huh?

En ook; Implementation-defined behaviour. Verschil?

Unspecified behaviour:

- **Hóeft niet** gedocumenteerd te worden
- Order of Evaluation

```cpp 
#include <iostream>
void f(int a, int b, int c){ 
    printf("%d, %d, %d", a,b,c);
}

int main(){
    int x = 12;
    f(x, x++, x+20);
}

```

- String Literal Comparison

```cpp
char[] t = "Hallo";

std::cout << t == "Hallo" << std::endl;
```

::right::

<br><br><br><br>

Implementation defined behaviour:

- **Moet wel** gedocumenteerd worden
- Waarde van std::sizeof(int);
    - 32- of 64-bit
- Uit hoeveel bits een byte bestaat
    - Mééstal 8, maar niet altijd! 

---
hideInToc: true
---

# Proof is in the pudding;

```cpp {monaco-run}
#include <iostream>
void f(int a, int b, int c){ 
    printf("%d, %d, %d", a,b,c);
}

int main(){
    int x = 12;
    f(x, x++, x+20);
}
```

<img src="/OutputCE.png" style="display: block; margin: 10; width: 60%; height: auto;">

---
layout: center
hideInToc: true
---

# \<br>

---

# Pointers

<v-clicks>

Variabele voor het wijzen naar de plek van een object in het geheugen

Bijzonder: `nullptr`; pointer die (nog) nergens naar wijst

<br>

Pointers kunnen wijzen naar verschillende soorten geheugen:
  - **Stack-geheugen**: Voor lokale variabelen.
  - **Heap-geheugen**: Voor dynamisch gealloceerde objecten.
    - `malloc` & `free` in C
    - `new` & `delete` in C++

<br>

Wanneer dynamisch geheugen?
    
- Niet altijd duidelijk **hoeveel geheugen** je nodig hebt @ compile time
- Hele grote objecten wil je **niet in de stack** plaatsen
- Data structuren zonder **upper bound**

</v-clicks>

---
hideInToc: true
---

# Pointers

Pointers kunnen worden gebruikt voor:

<v-clicks>

- **Pointer arithmetic**: Navigeren door arrays of geheugenblokken.

```cpp
int a[]= {10, 20, 30, 40, 50, 60, 70, 80, 90, 100};
int len = sizeof(a)/sizeof(int);
int *x = a;
int i = 0;

for(i = 0; i < len; i++){
    printf("Address of subscript %d = %d Value = %d\n", i, x, *x);
    x++;
}
```

- **Function pointers**: Functies als argumenten doorgeven.

```cpp
void loop(unsigned int count, void(*func)()) {
    for (unsigned int i = 0; i < count; i++)
        func();
}
```

</v-clicks>

---
hideInToc: true
---

# Pointers

Gevaren van pointers:
- **UB met pointer arithmetic**: Non-array types, out of bounds memory access.
- **Memory leaks**: Geheugen dat niet wordt vrijgemaakt.
- **Null pointers**: Dereferencing kan leiden tot crashes.
- **Dangling pointers**: Wijzen naar vrijgemaakt geheugen.

<v-clicks>

```cpp
Class *object = new Class();
Class *object2 = object;

delete object;
object = nullptr;
// Waar wijst object2 heen?
```

```cpp
Object *method() {
  Object object;
  return &object;
}

Object *object2 = method();
// object bestaat niet meer, dus waar wijst object2 naar?
```

</v-clicks>

---

# References

<v-clicks>

- Een **reference** is een alias voor een bestaande variabele.
- Wordt gebruikt om een variabele door te geven zonder een kopie te maken.
- **Altijd gebonden aan een bestaand object**; kan niet `null` zijn zoals een pointer.

<br>

Voordelen van references:
- Makkelijker te gebruiken dan pointers.
- Geen risico op `null` of dangling references (tenzij via UB).
- Ideaal voor **pass-by-reference** in functies.

<br>

Gebruik van references:
- **Functieargumenten**: Vermijd kopiëren van grote objecten.
- **Returnwaarden**: Geef een alias terug naar een bestaand object.
- **Const references**: Voor veilige toegang zonder wijzigingen.

</v-clicks>

---

# Smart Pointers

<v-clicks>

- References zijn dus **niet altijd** een vervanging voor pointers
    - Voor dynamic memory management bieden ze geen oplossing

<br>

- Pointers zijn **té veelzijdig**:
    - Single object <> Arrays
    - Ownership <> non-ownership

<br>

- In plaats hiervan kun je **Smart Pointers** gebruiken:
    - .. Maar is te veel voor nu, en een les op zich
    - Sorry :(

</v-clicks>

---

# Verder lezen/kijken/luisteren

Undefined behaviour:

[Undefined Behavior in C++: What Every Programmer Should Know and Fear; Fedor Pikus](https://www.youtube.com/watch?v=k9N8OrhrSZw)

[Back To Basics: Undefined Behavior; Ansel Sermersheim & Barbara Geller](https://www.youtube.com/watch?v=NpL9YnxnOqM)

[Undefined Behavior is Not an Error; Barbara Geller & Ansel Sermersheim](https://www.youtube.com/watch?v=XEXpwis_deQ)

<br>

Pointers & References:

[What is the Difference Between a Pointer and a Reference C++](https://www.youtube.com/watch?v=sxHng1iufQE)

[Back to Basics: C++ Smart Pointers; David Olsen](https://www.youtube.com/watch?v=YokY6HzLkXs)

---
layout: end
---
