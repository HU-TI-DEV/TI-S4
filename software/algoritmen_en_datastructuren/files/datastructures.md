


```python
import numpy as np

# Create a numpy array
numbers = np.array([10, 20, 30, 40, 50])
print("The array:", numbers)

# Access elements by index
print("First element:", numbers[0])
print("Last element:", numbers[-1])

# Modify an element
numbers[2] = 99
print("After modifying third element:", numbers)
```


```python
def demo_basic():
    print("# Basic creation")
    a = {1, 2, 3, 4}
    b = set([3, 4, 5, 6])
    print("a:", a)
    print("b:", b)
    print()

def demo_operations():
    a = {1, 2, 3, 4}
    b = {3, 4, 5, 6}
    print("# Set operations")
    print("union (a | b)         :", a | b)
    print("intersection (a & b)  :", a & b)
    print("difference (a - b)    :", a - b)
    print("difference (b - a)    :", b - a)
    print("symmetric difference  :", a ^ b)  # items in either a or b but not both
    print()

def demo_mutation_and_membership():
    s = {10, 20, 30}
    print("# Mutation & membership")
    print("initial s:", s)
    s.add(40)
    print("after add(40):", s)
    s.discard(20)
    print("after discard(20):", s)
    # discard does not raise if element missing; remove would raise
    try:
        s.remove(99)
    except KeyError:
        print("remove(99) would raise KeyError (element not present).")
    print("is 30 in s?", 30 in s)
    print("is 99 in s?", 99 in s)
    print()

```



```python

```