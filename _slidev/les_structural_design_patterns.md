---
theme: ./slidev-theme-ti
output: ../software/cpp/structural_design_patterns.pdf
hideInToc: true
---

# Design Patterns: Structural

---
layout: table-of-contents
hideInToc: true
---

# Programma

---

# Design Patterns; Wat?

<v-clicks>

- 'Standaard' oplossing voor veelvoorkomende problemen
- Communicatie tool voor complexe design ideeën
- Helpt met leesbare, onderhoudbare code
- Separation of concerns

</v-clicks>

<img src="/design_patterns.png" style="position: absolute; bottom: 20px; right: 20px; width: 250px; height: auto;">

<Footnotes seperator>
    <Footnote>https://refactoring.guru/design-patterns</Footnote>
</Footnotes>

---

# Structural Design Patterns; Wat?

<v-clicks>

- Oplossingen voor problemen met hoe klassen en objecten grotere structuren vormen
- Versimpelen van relaties 
- Veelal; betere efficiëntie, flexibelere code
- Combineren van objecten voor nieuwe functionaliteit
- DRY principe

</v-clicks>

<v-after>

Een aantal hebben jullie al eens gezien;

</v-after>

<v-clicks>

- Adapter (Wrapper)
    - Zelfde gedrag, andere interface
    - S2; tekenen op verschillende displays
- Decorator
    - Zelfde interface, ander gedrag
    - S2; inverteren van een pin

</v-clicks>

---
layout: image-left
image: /proxy.png
---

# SDP; Proxy Pattern

Een placeholder object voor echte object om toegang tot het object te beperken of aan te passen.

Een aantal smaakjes:

<v-clicks>

- Remote Proxy
    - Handelt toegang tot remote objecten af
- Virtual Proxy
    - Crëert dure objecten on demand
- Protection Proxy
    - Controleert toegangsrechten tot objecten

</v-clicks>

<v-after>

<br>

Ook deze gebruiken jullie (hopelijk) stiekem al vaker: smart pointers

</v-after>

<Footnotes separator>
  <Footnote>https://refactoring.guru/design-patterns/proxy</Footnote>
</Footnotes>

---
hideInToc: true
layout: image
image: /flyweight_minecraft.png
---

<Footnotes separator>
    <Footnote>https://aaagameartstudio.com/blog/texturing-for-video-games/</Footnote>
</Footnotes>

---
layout: image-right
image: /flyweight_trees.png
---

# SDP; Flyweight Pattern

- Voor verbeteren van performance 
- Verminderen van geheugengebruik

<v-clicks>

Beide door het delen van gemeenschappelijke resources;
géén kopieën dus!

<br>

- Intrinsieke vs Extrinsieke state

<br>

- Kan verder uitgebreid worden met een Flyweight Factory; voor later!

</v-clicks>

<Footnotes separator>
    <Footnote>https://www.youtube.com/watch?v=Y2cWu14rAy0</Footnote>
</Footnotes>

---
hideInToc: true
layout: image
image: /flyweightnt.png
---

<Footnotes seperator>
    <Footnote>https://gameprogrammingpatterns.com/flyweight.html</Footnote>
</Footnotes>

---
hideInToc: true
layout: image
image: /flyweight_nuwel.png
---

<Footnotes seperator>
    <Footnote>https://gameprogrammingpatterns.com/flyweight.html</Footnote>
</Footnotes>

---

# SDP; en verder?

Paar standaard patronen niet behandeld;
- Facade
- Bridge
- Composite

Meer over te vinden;

- https://refactoring.guru/design-patterns/structural-patterns
- https://www.geeksforgeeks.org/structural-design-patterns/


---
layout: end
---
