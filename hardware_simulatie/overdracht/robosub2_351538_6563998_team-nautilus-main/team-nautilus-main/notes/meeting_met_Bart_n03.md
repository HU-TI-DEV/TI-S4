Gesprek met Bart

_28/05/2026_

Aanwezig: Ying, Jorn, Aya

Welke intelligentie we gaan implementeren:
- PID
- Inverse Kinematics
- Vision

Vision is de enige die tot nu toe (grotendeels) werkt, maar het handvat kan nog niet gedetecteerd worden.
PID is geïmplementeerd, maar de waarden moeten nog gefinetuned worden.
Inverse Kinematics code wordt omgezet naar c++, maar dat is nog niet af.

De tijd dringt nu echt wel, en we lopen wel achter, de meeste groepjes kunnen nu al wat werkends laten zien. Currently we're not on course to pass it in one go, and will likely have to improve things in the improvement weeks.

Groepsdynamiek moet ook nog steeds aan gewerkt worden

Documentatie moet ook echt wel netjes en moet ook nog gebeuren


#### Vision 
Het handvat herkennen lukt nu nog niet, omdat de kleur te similar is en de vision het niet oppakt.

Voor nu geprobeerd om de witte kleur van het pijltje te herkennen, met hough-lines het handvat proberen te herkennen en met PCA (principal component analysis)

Probeer andere methoden bijvoorbeeld:
- Canny edge -> is al geprobeerd, maar nog verder mee proberen en testen
- Contrast verhogen
- Binary picture
