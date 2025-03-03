---
theme: ./slidev-theme-ti
output: ./../software/cpp/lambdas_en_stl.pdf
hideInToc: true
---

# Lambda's & <br> STL

---
layout: table-of-contents
hideInToc: true
---

# Programma

---
layout: two-cols
---

# Lambda; wat?

'Anonieme' functies; closures

<br>

Pre C++11

```cpp
int main () {
    std::vector<int> x = {2, 3, 5, 7, 11, 13};

    struct {
        int center; 
        bool operator()(int x, int y) const {
            return abs(x - center) < abs(y - center);
        }
    } comp = {10};

    std::sort(x.begin(), x.end(), comp);

    std::for_each(x.begin(), x.end(), printer);

    return 0;
}
```

::right::

# <br>

<br><br><br>

<v-click>
Post C++11

```cpp
int main () {
    std::vector<int> x = {2, 3, 5, 7, 11, 13};

    int center = 10;
    std::sort(x.begin(), x.end(), [=](int x, int y){
        return abs(x - center) < abs(y - center);
    });

    std::for_each(x.begin(), x.end(), [](int v) {
        std::cout<<v<<std::endl;
    });

    return 0;
}
```
</v-click>

<!-- code van: https://stackoverflow.com/a/3018737 -->
---

# Lambda; hoe?

Meest basale vorm

```cpp
int main(){
    []{std::cout << "Hallo Wereld" << std::endl;};
}
```
<v-click>Als je het ook nog uit wilt voeren
```cpp
int main(){ 
    []{std::cout << "Hallo Wereld" << std::endl;}();
}
```
</v-click>

<br><br>

<v-click>
Een lambda is dus een soort functie, bestaande uit (minimaal):

````md magic-move

```cpp
[...]
// Capture clause
```

```cpp
[...]{...}
// En een body
```

````
</v-click>

---

# Lambda; Capture Clause

- Voor toegang tot buiten de scope

---
layout: center
---

# Lambda; waarom? <br> \<br\>

---
layout: center
hideInToc: true
---

# \0


