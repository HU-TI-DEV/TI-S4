---
theme: ./slidev-theme-ti
output: ../software/cpp/sp_dp.pdf
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

- Vorm van resource management
- Gebonden aan lifetime van een object

</v-clicks>

<v-click after>

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

- Dit kun je óók voor geheugen doen

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

<v-clicks>

3 typen Smart Pointers, uit de `<memory>` header:
- `std::unique_ptr`
    - Één eigenaar van de resource; geen kopieën mogelijk
    - Eigenaarschap doorgeven d.m.v. `std::move`
- `std::shared_ptr`
    - Meerdere eigenaren van de resource; kopieën mogelijk
    - Maakt gebruik van Reference Counting
- `std::weak_ptr`
    - Specifiek voor gebruik met `std::shared_ptr`
    - Draagt niet bij aan Reference Counting

</v-clicks>

---

# Smart Pointers; hoe?


---


