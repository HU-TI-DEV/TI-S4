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
bool f(int i) { 
    return i+1 > 1; 
}
```

```cpp
bool f(int i) { 
    return i+1 > 1; 
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
    return i+1 > 1;                     //| mov $0x1, %eax
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

- UB _ergens_ in je programma maakt het hele programma undefined
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

- Hóeft niet gedocumenteerd te worden
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

- Móet wel gedocumenteerd worden
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
layout: end
---
