---
theme: ./slidev-theme-ti
output: ../software/algoritmen_en_datastructuren/3_hierarchische_datastructuren_en_grafen.pdf
hideInToc: true
---

# Hierarchische Datastructuren en Grafen

---
hideInToc: true
---

# Leerdoelen

Tot nu toe lineaire en associatieve structuren gezien. Nu voegen we toe:

- **Trees:** parent-child structuur
- **Grafen:** algemene netwerken zonder vaste hiërarchie

<br>

Na deze les begrijp je en pas je toe:

- wat een hiërarchische datastructuur is en waarom trees daar een kernvoorbeeld van zijn
- hoe een Binary Search Tree (BST) werkt voor search, insert en delete
- waarom balans in trees belangrijk is (AVL-intro)
- hoe grafen gemodelleerd worden als $G = (V, E)$
- welke keuzes je maakt bij grafen (gericht/ongericht, gewogen/ongewogen, representatie)

---
layout: table-of-contents
hideInToc: true
---

# Programma

---

# Trees

Een tree heeft:

- een **root** (startpunt)
- **children** per node
- **leafs** (nodes zonder children)

Bij een **binaire tree** heeft elke node maximaal 2 children.

```text
​
     [8]
    /   \
  [3]  [10]
 /   \       \
[1] [6]    [14]
```

---
layout: two-cols
hideInToc: true
---

# Terminologie

- **depth van een node:** afstand vanaf de root
- **height/depth van de tree:** langste pad naar een leaf
- **subtree:** tree met een child als nieuwe root
- **balans:** de verdeling van de diepte van een tree

<br>

```text
node n
depth(n) = aantal edges van root -> n
```

::right::

# Waarom relevant?

- complexiteit in trees hangt vaak af van depth
- in veel operaties geldt: $O(\text{depth}(T))$
- dus: ongebalanceerd vs gebalanceerd maakt groot verschil

<br><br><br>

<v-click>

# Voorbeelden uit de Reader

- integer-trees
- prefix trees (trie-idee) voor woorden

</v-click>

<!--
- bij prefix trees betekent dieper in de tree: langere prefix
- handig voor dictionary/autocomplete-achtige problemen
- zelfde structuur, ander type inhoud
-->

---

# Binary Search Tree (BST)

BST-regel per node met waarde $v$:

- links staan alleen waarden $< v$
- rechts staan alleen waarden $> v$

```text
​
		  [7]
	    /   \
	  [3]   [9]
   / \    /  \
[1] [5][8][10]
```

Zo kun je zoeken via hetzelfde principe als binary search.

<!--
Maar waarom dan een BST i.p.v. binary search? 
Updates are the key difference. Dynamische data BST is beter
Sorted array:
insert/delete is typically O(n) -> O(n) because elements must shift.
Balanced BST:
insert/delete is typically O(log ⁡n)

Array heeft betere cache locality (dus sneller in praktijk), minder memory overhead

RoT: read only? Array, dynamisch? BST
-->

---
layout: two-cols
hideInToc: true
---

# Search in een BST

```python
def bst_search(node, target):
	while node is not None:
		if target == node.value:
			return node
		if target < node.value:
			node = node.left
		else:
			node = node.right
	return None
```

::right::

# Complexiteit

- per stap ga je 1 niveau omlaag
- aantal stappen wordt begrensd door tree-depth
- dus: $O(\text{depth}(T))$

Welke complexiteit?

<v-click>

Bij goede balans: ongeveer $O(\log n)$

</v-click>

---
hideInToc: true
---

# Insert en delete in BST

**Insert:**
- volg dezelfde route als bij search
- voeg nieuwe node toe als leaf

**Delete (globaal):**
- leaf verwijderen: direct
- node met 1 child: child doorschuiven
- node met 2 children: vervang met inorder-successor (kleinste rechts)

<v-click>

Ook hier blijft de hoofdterm: $O(\text{depth}(T))$.

</v-click>

---
hideInToc: true
---

# Het probleem: ongebalanceerde trees

Als je gesorteerde waarden invoegt, kan een BST degenereren:

```text
[1] -> [2] -> [3] -> [4] -> [5]
```

Dan wordt depth ongeveer $n$.

Gevolg:

- search/insert/delete van ongeveer $O(\log n)$ naar $O(n)$

---
layout: two-cols
---

# AVL

AVL (Adelson-Velsky and Landis) houdt de tree in balans met rotaties.

Balansvoorwaarde (intuïtief):
- verschil in subtree-depth links/rechts per node maximaal 1

```text
balance_factor(node)
= depth(left) - depth(right)
```

::right::

# Rotaties

- single rotation (LL of RR)
- double rotation (LR of RL)

Doel:
- depth klein houden
- operaties dicht bij $O(\log n)$ houden

---
hideInToc: true
---

# Check-in: Trees

<v-clicks>

1. Waarom is een linked list een "speciale" tree-vorm?
2. Welke BST-eigenschap moet altijd gelden?
3. Waarom kan invoegvolgorde performance breken?
4. Wat is het doel van AVL-rotaties?

</v-clicks>

<!--
Kernantwoorden:
1) Elk element max 1 child in kettingstructuur.
2) Links < node < rechts.
3) Onbalans -> depth groeit naar n.
4) Depth verlagen en logaritmische performance behouden.
-->

---
layout: center
hideInToc: true
---

# \<br>

Daarna:

# Grafen

---

# Grafen

Een graaf modelleren we als:

$$G = (V, E)$$

- $V$: verzameling nodes (vertices)
- $E$: verzameling edges (verbindingen)

In tegenstelling tot trees is er geen vaste parent-child-hiërarchie nodig.

- **Undirected:** edge werkt twee kanten op
- **Directed:** richting is relevant -> $(u, v) \neq (v, u)$
- **Weighted:** edges hebben kosten/afstand -> routeplanning

---
layout: two-cols
---

# Representatie van grafen

**Adjacency list:**

A: [B, D], B: [C], C: [D], D: [], E: [A]

**Adjacency matrix:**

|From \ To | A| B| C| D| E|
|----------|--|--|--|--|--|
|A	       | 0|	1| 0| 1| 0|
|B	       | 0|	0| 1| 0| 0|
|C	       | 0|	0| 0| 1| 0|
|D	       | 0|	0| 0| 0| 0|
|E	       | 1|	0| 0| 0| 0|

::right::

<br> <br>
5 nodes met deze directed edges:

(A->B), (A->D), (B->C), (C->D), (E->A)

<br><br><br><br>

# Matrix vs list

- adjacency matrix: $O(|V|^2)$ geheugen
- adjacency list: $O(|V| + |E|)$ geheugen

Kies op basis van dichtheid van je graaf:

- dense graaf -> matrix soms handig
- sparse graaf -> list vaak efficiënter

---

# Traversal: BFS en DFS

```text
BFS: laag voor laag (queue)
DFS: diepte eerst (stack/recursie)
```

Typische toepassingen:

- bereikbaarheid
- componenten vinden
- paden/structuur inspecteren

Complexiteit (beide):

$$O(|V| + |E|)$$

---
layout: two-cols
hideInToc: true
---

# Conceptueel denken in grafen

Voor je algoritmes kiest, modelleer je eerst goed:

- wat zijn de nodes?
- wat zijn de edges?
- zijn edges gericht of ongericht?
- hebben edges een gewicht?

::right::

# Modellering bepaalt alles

- verkeerde modellering -> verkeerde oplossing
- juiste representatie -> eenvoudiger implementatie
- algoritmes volgen pas daarna

---
hideInToc: true
---

# Voorbeelden van graafmodellen

<v-clicks>

1. **Sociale netwerk-graaf**
- node = persoon
- edge = relatie

2. **Wegennet-graaf**
- node = kruispunt
- edge = wegsegment
- gewicht = afstand/tijd

3. **Taakafhankelijkheden**
- node = taak
- gerichte edge: taak A moet voor taak B

</v-clicks>

---
hideInToc: true
---

# Oefenvragen

1. Je hebt een continue stroom van geordende inserts; waarom is een pure BST dan risicovol?
2. Je modelleert een wegennet. Welke nodes, edges en gewichten kies je?
3. Wanneer is een adjacency matrix een betere keuze dan een adjacency list?
4. Geef een voorbeeld van een directed graaf uit de praktijk.

<!--
Kernantwoorden:
1) Geordende inserts maken een BST snel ongebalanceerd (kettingvorm), waardoor operaties van ~O(log n) naar O(n) kunnen gaan.
2) Nodes = kruispunten/steden, edges = wegsegmenten, gewichten = afstand/reistijd/kosten (afhankelijk van de vraag).
3) Bij dichte grafen of wanneer je heel vaak edge-existence checks doet; matrix geeft O(1) lookup maar kost O(|V|^2) geheugen.
4) Voorbeeld: Instagram/X-volgrelaties, of taakafhankelijkheden in een build-pipeline (A -> B betekent A eerst).
-->

---
hideInToc: true
---

# Afsluiting

Hiërarchische structuren en grafen vullen elkaar aan:

- trees geven geordende hiërarchie
- grafen geven flexibele netwerkmodellen
- balans en representatiekeuze bepalen performance
- algoritmekeuze volgt uit probleemstructuur

Volgende stap:
- in de volgende les: pathfinding-algoritmen
