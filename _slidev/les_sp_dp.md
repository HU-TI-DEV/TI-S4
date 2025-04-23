---
theme: ./slidev-theme-ti
output: ../software/cpp/SmartPointers_DesignPatterns.pdf
hideInToc: true
---

# Smart Pointers & Design Patterns

---
layout: table-of-contents
hideInToc: true
---

# Programma

---

# RAII; herhaling

<v-clicks>

- Resource Acquisition Is Initialization
- Vorm van resource management
- Gebonden aan lifetime van een object

</v-clicks>

<v-click after>

<br>

```cpp
class FileHandler{
private:
    std::ofstream file; // gemanagede resource
public:
    // Resource Acquisition
    FileHandler(const std::string& filename){ ... } // Open file

    // Resource Release
    ~FileHandler(){ ... } // Close file
}
```

</v-click>

---
hideInToc: true
---

# RAII; stapje verder!


```cpp
template<typename T>
class PointerHandler{
private:
    T* ptr;
public:
    explicit PointerHandler(T* resource = nullptr) : ptr(resource){
        std::cout << "Resource managed!" << std::endl;
    }

    ~PointerHandler(){ 
        delete ptr; 
        std::cout << "Resource deleted!" << std::endl;    
    }

    ... //Operator overloads
}

int main(){
    {
        PointerHandler<int> intptr(new int(42));
    }
}
```

---

# Smart Pointers; wat?

- ... Dat is (deels) wat smartpointers zijn
- Taal feature voor RAII bij het managen van dynamische objecten
- (Met wat extra slimmigheden)

<br>

3 typen Smart Pointers, uit de `<memory>` header:
<v-clicks>

- `std::unique_ptr`
    - **Één eigenaar** van de resource; geen kopieën mogelijk
    - Eigenaarschap **doorgeven** d.m.v. `std::move`
- `std::shared_ptr`
    - **Meerdere eigenaren** van de resource; kopieën mogelijk
    - Maakt gebruik van **Reference Counting**
- `std::weak_ptr`
    - Specifiek voor gebruik met `std::shared_ptr`
    - Draagt **niet** bij aan Reference Counting

</v-clicks>

---

# Smart Pointers; hoe?

````md magic-move
```cpp
class Res {
private:
    std::string name;
public:
    Res(const std::string& name) : name(name){
        std::cout << name << " aangemaakt.\n";
    }
    ~Res() {
        std::cout << name << " verwijderd.\n";
    }
    void sayHello() const {
        std::cout << name << "!\n";
    }
};
```

```cpp
class Res {
private:
    std::string name;
public:
    Res(const std::string& name) : name(name){ ... }
    ~Res(){ ... }
    void sayHello() const { ... }
};
```

```cpp
class Res {
private:
    std::string name;
public:
    Res(const std::string& name) : name(name){ ... }
    ~Res(){ ... }
    void sayHello() const { ... }
};

int main() {
    // 1. std::unique_ptr: Één eigenaar
    {
        std::unique_ptr<Res> uniqueRes = std::make_unique<Res>("Unique");
        uniqueRes->sayHello();
        // Eigenaarschap doorgeven
        std::unique_ptr<Res> movedRes = std::move(uniqueRes);
        if (!uniqueRes) {
            std::cout << "uniqueRes is nu leeg.\n";
        }
        movedRes->sayHello();
    } // Resource wordt hier automatisch vrijgegeven
}
```

```cpp
class Res {
private:
    std::string name;
public:
    Res(const std::string& name) : name(name){ ... }
    ~Res(){ ... }
    void sayHello() const { ... }
};

int main() {
    // 1. std::unique_ptr: Één eigenaar
    {
        std::unique_ptr<Res> uniqueRes = std::make_unique<Res>("Unique");
        *uniqueRes.sayHello();
        // Eigenaarschap doorgeven
        std::unique_ptr<Res> movedRes = std::move(uniqueRes);
        if (!uniqueRes) {
            std::cout << "uniqueRes is nu leeg.\n";
        }
        *movedRes.sayHello();
    } // Resource wordt hier automatisch vrijgegeven
}
```

```cpp
class Res {
private:
    std::string name;
public:
    Res(const std::string& name) : name(name){ ... }
    ~Res(){ ... }
    void sayHello() const { ... }
};

int main(){
    // 2. std::shared_ptr: Meerdere eigenaren
    {
        std::shared_ptr<Res> sharedRes1 = std::make_shared<Res>("Shared");
        {
            std::shared_ptr<Res> sharedRes2 = sharedRes1; // Kopie delen
            sharedRes2->sayHello();
            std::cout << "Aantal eigenaren: " << sharedRes1.use_count() << "\n";
        } // sharedRes2 gaat uit scope, maar resource blijft bestaan
        std::cout << "Aantal eigenaren: " << sharedRes1.use_count() << "\n";
    } // Resource wordt hier vrijgegeven als de laatste eigenaar verdwijnt
}
```

```cpp
class Res {
private:
    std::string name;
public:
    Res(const std::string& name) : name(name){ ... }
    ~Res(){ ... }
    void sayHello() const { ... }
};

int main(){
    // 3. std::weak_ptr: Geen eigenaarschap
    {
        std::shared_ptr<Res> sharedRes = std::make_shared<Res>("Weak");
        std::weak_ptr<Res> weakRes = sharedRes; // Geen eigenaarschap
        if (auto lockedRes = weakRes.lock()) { // Controleer of resource nog bestaat
            lockedRes->sayHello();
        }
        sharedRes.reset(); // Resource vrijgeven
        if (weakRes.expired()) {
            std::cout << "Resource is niet meer beschikbaar.\n";
        }
    }
}
```
````

---

# Smart Pointers; de perfecte oplossing?

<v-clicks>

- Helaas :(
- Unique Ptrs zijn ⭐ **perfect** ⭐
- Weak Ptrs 'ook'
- Shared Ptrs gebruiken **éxtra geheugen** (reference counting)
- Shared Ptrs vragen **íets meer peformance** voor reference counting
- Weak Ptrs geen extra overhead, maar hebben Shared Ptrs nodig
- Shared Ptr reference counting is thread safe, maar resource access niet

</v-clicks>

<v-click after>

<br>

- Shared Ptrs kunnen Cyclic Dependency veroorzaken -> Memory Leak

</v-click>



---
hideInToc: true
---

# Smart Pointers; de perfecte oplossing?

- Shared Ptrs kunnen Cyclic Dependency veroorzaken

````md magic-move
```cpp
class B; // Forward declaration

class A {
public:
    std::shared_ptr<B> b_ptr; // Shared pointer naar B
    ~A() { std::cout << "A verwijderd\n"; }
};

class B {
public:
    std::shared_ptr<A> a_ptr; // Shared pointer naar A
    ~B() { std::cout << "B verwijderd\n"; }
};

int main() {
    auto a = std::make_shared<A>();
    auto b = std::make_shared<B>();

    a->b_ptr = b; // A wijst naar B
    b->a_ptr = a; // B wijst naar A
    // Beide objecten blijven bestaan omdat de reference count nooit nul wordt -> Memory Leak
}
```

```cpp
class B; // Forward declaration

class A {
public:
    std::shared_ptr<B> b_ptr; // Shared pointer naar B
    ~A() { std::cout << "A verwijderd\n"; }
};

class B {
public:
    std::weak_ptr<A> a_ptr; // Weak pointer naar A
    ~B() { std::cout << "B verwijderd\n"; }
};

int main() {
    auto a = std::make_shared<A>();
    auto b = std::make_shared<B>();

    a->b_ptr = b; // A wijst naar B
    b->a_ptr = a; // B wijst naar A, maar via weak_ptr
    // Nu worden beide objecten correct vrijgegeven, geen memory leak :)
}
```
```` 

---
layout: center
---

# \<br>

---

# Creational Design Patterns; wat?

- Voor het creëren van objecten
- Promoot flexibiliteit en DRY principe

Grofweg zijn er 5:
- Factory Method
- Abstract Factory
- Builder
- Prototype
- Singleton

---
hideInToc: true
---

# Creational Design Patterns; wat?

- Voor het creëren van objecten
- Promoot flexibiliteit en DRY principe

Grofweg zijn er 5:
- **Factory Method**
- Abstract Factory
- Builder
- Prototype
- **Singleton**

---

# CDP; Singleton

- Verzekert dat er maar één instantie van dat object is
- Biedt global access naar een resource

````md magic-move
```cpp
class Singleton{
private:
    ... // Een resource waar je toegang toe wilt controleren
public:
    Singleton(){ ... }
    void doSomething(){ ... }
};

int main(){
    Singleton A = new Singleton();
    A.doSomething();
}
```

```cpp
class Singleton{
private:
    ... // Een resource waar je toegang toe wilt controleren
public:
    Singleton(){ ... }
    void doSomething(){ ... }
};

int main(){
    Singleton A = new Singleton();
    A.doSomething();
    Singleton B = new Singleton();
    B.doSomething();
}
```

```cpp
class Singleton{
private:
    ... // Een resource waar je toegang toe wilt controleren
    Singleton(){ ... }; // Constructor is nu private!
    static Singleton* instance;
public:
    static Singleton* getInstance(){ ... } // Controleert dat er maar één instantie is
    void doSomething(){ ... }
};

int main(){
    Singleton* A = Singleton::getInstance();
    A->doSomething();
    Singleton& B = Singleton::getInstance(); // Dit is nu 'magisch' hetzelfde object
    B->doSomething();
}
```

```cpp
class Singleton{
private:
    ... // Een resource waar je toegang toe wilt controleren
    Singleton(){ ... }
    static Singleton* instance;
public:
    static Singleton* getInstance( ... ){ 
        if (instance == nullptr){
            instance = new Singleton();
        }
        return instance;
    }
    void doSomething(){ ... }
};
Singleton* Singleton::instance = nullptr;

int main(){
    Singleton* A = Singleton::getInstance();
    A->doSomething();
    Singleton* B = Singleton::getInstance(); // Toch niet magisch.. :(
    B->doSomething();
}
```

```cpp
class Singleton{
private:
    ... // Een resource waar je toegang toe wilt controleren
    Singleton(){ ... }
    static Singleton* instance;
public:
    static Singleton& getInstance( ... ){ 
        if (instance == nullptr){
            instance = new Singleton();
        }
        return *instance;
    }
    void doSomething(){ ... }
};
Singleton* Singleton::instance = nullptr;

int main(){
    Singleton& A = Singleton::getInstance();
    A.doSomething();
    Singleton& B = Singleton::getInstance(); // Toch niet magisch.. :(
    B.doSomething();
}
```

```cpp
class Singleton{
private:
    ... // Een resource waar je toegang toe wilt controleren
    Singleton(){ ... }
    static std::unique_ptr<Singleton> instance;
public:
    static Singleton& getInstance( ... ){ 
        if (!instance){
            instance = std::make_unique<Singleton>();
        }
        return *instance;
    }
    void doSomething(){ ... }
};

int main(){
    Singleton& A = Singleton::getInstance();
    A.doSomething();
    Singleton& B = Singleton::getInstance(); // Toch niet magisch.. :(
    B.doSomething();
}
```
```` 

---
hideInToc: true
---

# CDP; Singleton

- Zonder dure memory management;

```cpp
class Singleton {
private:
    Singleton() { ... }
public:
    static Singleton& getInstance() {
        static Singleton instance; // Gegarandeerd maar één keer
        return instance;
    }
    void doSomething() { ... }
};

int main() {
    Singleton& singleton = Singleton::getInstance();
    singleton.doSomething();
}
```

---
hideInToc: true
---

# CDP; Singleton

Krachtig, maar..

<v-click>

Nadelen, dus niet zonder controverse:

</v-click>

<v-clicks>

- Single Responsibility Principle
- Gevoelig voor Undefined Behaviour
- Globale State / Side Effects
- Hidden Dependencies
- Mogelijk niet Thread Safe

</v-clicks>



---

# CDP; Factory Pattern

- Stel, we willen een aantal objecten creëren

<v-click>

```cpp
class Colour; // Forward Declaration

class Drawable{
private:
    std::string Name; // Default onderdelen van een drawable object
    std::vector Pos; 
    Colour colour;
public:
    Drawable(std::vector Pos, Colour colour){ ... }
    virtual void draw const = 0;
}

class Rectangle : public Drawable{ ... }; // Implementeert specifieke onderdelen voor dit object
class Circle : public Drawable{ ... };
class Line : public Drawable{ ... };

int main(){
    Rectangle rect1 = Rectangle( ... );
    Rectangle rect2 = Rectangle( ... );
    Circle circ1 = Circle( ... );
    ...
}
```

</v-click>

---
hideInToc: true
---

# Kleine uitstap; Polymorfisme

- Het concept dat je een derived class pointer in een base class pointer kwijt kunt

````md magic-move
```cpp
class Drawable{ ... };
class Rectangle : public Drawable{ ... };
class Circle : public Drawable{ ... };

int main(){
    Drawable* obj = new Rectangle( ... );
    obj = new Circle( ... );
}
```

```cpp
class Drawable{ ... };
class Rectangle : public Drawable{ ... };
class Circle : public Drawable{ ... };

int main(){
    std::vector<Drawable*> drawables;
    drawables.push_back(new Rectangle( ... ));
    drawables.push_back(new Circle( ... ));
}
```

```cpp
class Drawable{ ... };
class Rectangle : public Drawable{ ... };
class Circle : public Drawable{ ... };

int main(){
    std::vector<Drawable*> drawables;
    drawables.push_back(new Rectangle( ... ));
    drawables.push_back(new Circle( ... ));

    for(auto obj : drawables){
        obj->draw();
    }
}
```

```cpp
class Drawable{ ... };
class Rectangle : public Drawable{ ... };
class Circle : public Drawable{ ... };

int main(){
    std::vector<std::unique_ptr<Drawable>> drawables;
    drawables.push_back(std::make_unique(Rectangle( ... )));
    drawables.push_back(std::make_unique(Circle( ... )));

    for(auto obj : drawables){
        obj->draw();
    }
}
```

```cpp
class Drawable{ ... };
class Rectangle : public Drawable{ ... };
class Circle : public Drawable{ ... };

int main(){
    std::vector<std::unique_ptr<Drawable>> drawables;
    drawables.push_back(std::make_unique(Rectangle( ... )));
    drawables.push_back(std::make_unique(Circle( ... )));

    for(auto *obj : drawables){
        obj.draw();
    }
}
```
````

---
hideInToc: true
---

# CDP; Factory Pattern

```cpp

Drawable* makeDrawable(std::ifstream & input){
    std::string name;
    std::vector pos;
    Colour colour;
    
    input >> name >> pos >> colour;

    if (name == "Circle"){ return new Circle( ... ); }
    if (name == "Rectangle"){ return new Rectangle( ... ); }
    ...
}

int main(){
    std::vector<Drawable*> drawables;

    while(true){
        drawables.push_back(makeDrawable(input));
    }
    
    for(auto drawable : drawables){
        drawable->draw();
    }
}
```

---
layout: end
---

