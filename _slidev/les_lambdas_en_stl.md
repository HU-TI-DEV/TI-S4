---
theme: ./slidev-theme-ti
output: ../software/cpp/lambdas_en_stl.pdf
hideInToc: true
---

# Lambda's & <br>STL

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
hideInToc: true
---

# Lambda; wat?

````md magic-move
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

```cpp
int main () {
    std::vector<int> x = {2, 3, 5, 7, 11, 13};

    int center = 10;
    std::sort(x.begin(), x.end(), [=](int x, int y){ return abs(x - center) < abs(y - center); });

    std::for_each(x.begin(), x.end(), [](int v) { std::cout<<v<<std::endl; });

    return 0;
}
```
````

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

<v-click>Of wilt bewaren voor later

```cpp
int main(){
    auto func = []{std::cout << "Hallo Wereld" << std::endl;};
    func();
}
```
</v-click>

<v-click>
Een lambda is dus een soort functie, bestaande uit (minimaal):

````md magic-move

```cpp
[...]
// Capture clause ..
```

```cpp
[...]{...}
// Capture clause en een body
```

````
</v-click>

---
hideInToc: true
---

# Klein uitstapje; types

- In vorige slide; `auto` - waarom?
- Elke lambda heeft een uniek type


<v-click hide>

```cpp {monaco-run}
#include <iostream>
using namespace std;

int main(){
    auto x = 10;
    auto y = 20;
    cout << boolalpha << is_same<decltype(x), decltype(y)>::value << endl;
}

```

</v-click>
<v-after>

```cpp {monaco-run}
#include <iostream>
#include <typeinfo>
using namespace std;

int main(){
    auto x = []{return true;};
    auto y = []{return true;};
    cout << boolalpha << is_same<decltype(x), decltype(y)>::value << endl;
    cout << typeid(x).name() << " - " << typeid(y).name() << endl;
}
```

</v-after>

---

# Lambda; Capture Clause

Voor toegang tot buiten de scope

```cpp {monaco-run}
#include <iostream>
int main(){
    int x = 12;
    int y = 10;
    auto foo = [x,y]{std::cout <<"x+y by value: "<< x+y << std::endl;};
    auto bar = [&x,&y]{std::cout <<"x+y by reference: "<< x+y << std::endl;};
    x = 42;
    auto baz = [&x,y]{std::cout <<"x+y mixed: " << x+y <<std::endl;};
    y = 22;
    foo();
    bar();
    baz();
}
```

Je kunt ook álles capturen: `[=]` == alles by value, `[&]` == alles by reference

<!-- Interessant: wanneer vindt het capturen dus plaats? -->

---

# Lambda; verdere syntax?

- If it quacks like a duck, and walks like a duck, it must be a duck!
- Lambda al bijna een 'functie', maar mist nog e.e.a!

````md magic-move
```cpp
// Zoals parameters:
int main(){
    auto halve = [](int& x){return x/2;};
    int n = 20;
    std::cout << halve(n) << std::endl;
    // >> 10!
}
```

```cpp
// En een return type:
int main(){
    auto halve = [](int& x) ->int {return x/2;};
    int n = 20;
    std::cout << halve(n) << std::endl;
    // >> 10! 
}
```

```cpp
// Hoe fixen we dit?
int main(){
    auto halve = [](int& x) ->int {return x/2;};
    int n = 21;
    std::cout << halve(n) << std::endl;
    // >> 10?
}
```

```cpp
// Return type is niet nodig, maar is vooral voor leesbaarheid
int main(){
    auto halve = [](int& x){return x/2.0;};
    int n = 21;
    std::cout << halve(n) << std::endl;
    // >> 10.5!
}
```
````

# <br>

<v-click>

Trailing return types mogen overigens ook bij normale functies;

```cpp
auto halve(int& x) -> float {
    return x/2.0;
}
```

</v-click>

---
layout: center
---

# Lambda; waarom?

# \<br\>

---
layout: center
hideInToc: true
---

# \0


