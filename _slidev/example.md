---
theme: ./slidev-theme-ti
output: ./example-slides.pdf
---

# cover

## slidev-theme-academic

<Pagination classNames="text-gray-300" />


---
layout: table-of-contents
hideInToc: false
---

# table-of-contents

---
layout: index
indexEntries:
  - { title: "Curated cover image for Slidev", uri: 4 }
  - { title: "Curated cover image for Slidev", uri: 5 }
---

# index

`index` used as list of figures

---
layout: figure
figureCaption: Curated cover image for Slidev
figureFootnoteNumber: 1
figureUrl: https://cover.sli.dev
---

# figure

<Footnotes separator>
  <Footnote :number=1><a href="https://unsplash.com/collections/94734566/slidev" rel="noreferrer" target="_blank">Anthony Fu</a></Footnote>
</Footnotes>

---
layout: figure-side
figureCaption: Curated cover image for Slidev
figureFootnoteNumber: 1
figureUrl: https://cover.sli.dev
---

# figure-side

- Ensures figures are displayed nicely out of the box
- Allows placing the figure on the left or right
- Features an optional figure caption

<Footnotes separator>
  <Footnote :number=1><a href="https://unsplash.com/collections/94734566/slidev" rel="noreferrer" target="_blank">Anthony Fu</a></Footnote>
</Footnotes>

---
layout: center
class: "text-center"
---

# Footnotes & Footnote

<span class="font-extralight">
  <q>Give credit where credit is due</q>
  <sup>1</sup>
</span>

<Footnotes separator>
  <Footnote :number=1>Smart person</Footnote>
</Footnotes>

---
layout: center
class: "text-center"
---

# Pagination

<span class="font-extralight">Enabled by default</span>

<img
  class="absolute transform -bottom-1 -right-21.5 w-40"
  src="/box.svg"
/>

<p class="absolute font-extralight right-14 transform rotate-8 bottom-4">Here!</p>

---
layout: index
indexEntries:
  - { title: "GitHub", uri: "https://github.com/alexanderdavide/slidev-theme-academic" }
  - { title: "npm", uri: "https://www.npmjs.com/package/slidev-theme-academic" }
  - { title: "Slidev", uri: "https://sli.dev" }
indexRedirectType: external
---

# index

`index` used as a list of references

---

# JS

```js {monaco-run}

console.log("hello world")

```

---

# Code

```cpp {monaco-run}
#include <iostream>

int main() {
    int i = 1234567890;
    std::cout << "Hallo wereld " << __VERSION__;
}
```

---

<br>

```plantuml
!theme spacelab
state CurrentSite #pink {
    state HardwareSetup #lightblue {
       state Site #brown
        Site -[hidden]r-> Controller
        Controller -[hidden]-> Devices
    }
    state PresentationSetup{
        Groups -[hidden]-> PlansAndGraphics
    }
    state Trends #orange
    state Schedule #magenta
    state AlarmSupression
    Trends -> Schedule
    Schedule -> AlarmSupression
}
```
