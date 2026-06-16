# Sprint verslag sprint 5
# Nautilus

### Inhoud[](toc-id)
- [Sprint doel](#sprint-doel)
- [Sprint planning](#sprint-planning)
    - [Feedback teambegeleider](#feedback-teambegeleider)
- [Daily Scrum](#daily-scrum)
- [Sprint review](#sprint-review)
    - [Feedback teambegeleider/ Product owner](#feedback-teambegeleider-product-owner)
    - [Persoonlijke reflectie](#persoonlijke-reflectie)
    - [Peer Assessment](#peer-assessment)
- [Sprint retrospective](#sprint-retrospective)
    - [Feedback teambegeleider](#feedback-teambegeleider-1)


    
---

## Sprint doel

- De arm kan naar een bepaald coördinaat bewegen.
- Vision stuurt coördinaten terug naar robotarm controller
- Nieuw model op basis van nieuwe verkregen afbeelding robosub
- Model maken voor de schuif die we gaan bewegen
- Documentatie verder afronden

## Sprint planning

    Datum : 22-04-2026  
    Afwezig: 
Link naar het scrumboard: [link](https://github.com/orgs/2025-TICT-TV2SE4-24-3-V/projects/5)

Beschikbare capaciteit: 40 uren.



### Feedback teambegeleider


## Daily Scrum

| Datum:     | Afwezig:    | Taken gedaan                                                                                                                                                                                                      | Taken niet af:                                                                             | Taken te doen                                                                                                                                                                                                                                                                                              | blokkades                                                                               |
  |------------|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| 04-05-2026 | Ying, David, Jorn | Luuc: ALDS 2 opdracht 1 en een deel van 2. <br> Aya: vooronderzoek voor deepdive                                                                                                                                  | Luuc: Niets, want in vakantie niet gepland. Aya: ook niks, want niks ingeland in vakantie. | Luuc: ALDS 2, inverse kinematica code doornemen. Aya: ALDS 1 t/m opdracht 2.                                                                                                                                                                                                                               | Luuc: zat in de vakantie in de vakantiemodus.                                           |
| 06-05-2026 | Niemand | Jorn: niet zo veel, begin gemaakt ALDS 1 <br> Aya: ALDS 1 af <br> Ying: ALDS 2 opgave 1 en 2 <br> Luuc: hetzelfde als Ying <br> David: K-means clustering                                                         | Luuc: inverse kinematica code doornemen                                                    | Luuc: ALDS 2 afmaken <br> David: ALDS 2 afmaken <br> Ying: diepte halen uit depth camera verbeteren, onderzoek coords vinden of ALDS 2. <br> Aya: ALDS 2 opdracht 1. Jorn: ALDS 1 afmaken                                                                                                                  | David: probeerde de C++ file zonder CMake te runnen, dit resulteerde in linker errors.  | 
| 07-05-2026 | Niemand | Luuc: ALDS 2 opdracht 2 afgerond met plots. <br> David: ALDS 2 afgerond, begin coördinaten script gemaakt <br> Jorn: ALDS 1 t/m opdracht 2 <br> Ying: positie t.o.v. de depth camera <br> Aya: ALDS 2 opdracht 1. | Luuc: ALDS 2 opdracht 3. <br> Jorn: ALDS 1 opdracht 3 en 4. <br> David <br>                | Luuc: ALDS 2 opdracht 3, documentatie doorkammen en updaten, begin aan CV2 <br> Jorn: ALDS 1 afmaken, daarna CV2. Aya: ALDS 2 hopelijk afmaken <br> Ying: wereldcoördinaten ophalen, ALDS 2 afmaken                                                                                                        | Jorn: Python interpreter werkte niet mee <br> Ying: heeft per ongeluk dingen verwijderd | 
|11-05-2026 | David | Luuc: ALDS 2 volledig afgerond, documentatie doorgekamd. <br> Jorn: ALDS 1 <br> Ying: wereldcoords ophalen door depth camera. <br> Aya: niks                                                                      | Luuc: OpenCV2 start maken. Aya: ALDS 2.                                                    | Luuc: gaat langs Bart voor hydrodynamics, Opdracht 1 van CV2, documentatie aanpassen. <br> Jorn: ALDS 2 opdracht 1 en 2. <br> Ying: code netjes maken en updaten, waar nodig klassendiagram updaten. ALDS 2 opdracht 3 maken. <br> Aya: inverse kinematics code doornemen en samenvatten, ALDS 2 opgave 2. | Luuc: filmen lustrum in het weekend <br> Aya: persoonlijke redenen                      |
| 12-05-2026 | David, Luuc, Ying | Luuc: NF requirements geupdate na de vraag van Colin. <br> Jorn: ALDS 2 opdracht 1, begin aan onderzoek inverse kinematics <br> David: Submodelv4 <br> Ying: Code voor project gepushed naar GitHub <br> Aya: FABRIK paper doorgelezen.                                                                     | Luuc: OpenCV2 start maken, hydro test controleren met Bart. <br> David: Minder progressie dan gewenst op coordinaten robotarm. <br>  Aya: ALDS2, andere IK papers.                                                  | Luuc: gaat met IK testen zodat we morgen tijdens de presentatie iets te laten zien hebben <br> Jorn: ALDS 2 opdracht 2, 3, verder aan onderzoek IK. <br> Ying: ALDS afronden en de presentatie voor morgen voorbereiden. <br> David: Verder met coordinaten robotarm <br> Aya: inverse kinematics code doornemen en samenvatten, ALDS 2 opgave 2. <br> Aya: ALDS2 | Luuc: werk en bestuurs/commissievergaderingen <br>                    |

## Sprint review

### Product:

#### Wat ging goed?

- Ying heeft vision mooi voor elkaar gekregen, mooie basis om op voort te bouwen

#### Wat ging minder?

- Kinematics lukte niet goed, was voornamelijk onderzoek uitgevoerd
- Tempo lag te laag


### Individuele inleveringen

Luuc: 
ALDS 1 en ALDS 2 afgetekend, ik had meer willen doen, maar er zit vooruitgang in.

Aya:
ALDS1 is afgetekend, hoewel ik een begin heb gemaakt aan ALDS2 heb ik die helaas nog niet af gekregen

Jorn:
Gazebo 3 PID afgetekend (eindelijk), ALDS 1 af en ALDS 2 gedeeltelijk af, had meer willen doen en ga dit ook zeker doen volgende sprint

Ying: zie persoonlijke reflectie

### Persoonlijke reflectie

### Luuc

Deze sprint was wat mij betreft een beetje mislukt, het tempo was te laag en we hadden weinig overzicht over wat we deden. Als scrum-master neem ik daar extra verantwoordelijkheid voor, ik heb dat ook iets te laks aangepakt. Ik heb op projectvlak weinig weten uit te voeren, qua persoonlijk wel het een en ander weten af te tekenen. Al met al was het een beetje gemengd voor mij, maar het is jammer dat het project een beetje viel.

### David 

Ik heb niet extreem veel gedaan ik wou aan het einde nog een aantal dingen doen maar dat ging niet helemaal als gepland kortom deze sprint te relaxed aan gedaan volgende sprint gas erop

### Jorn
Ik vond deze sprint over het algemeen erg traag en ik vind dat er niet genoeg is gebeurt in sommige aspecten. Zelf is mijn contributie aan het project ook weer zeer minimaal geweest, en ik ga mezelf forceren om volgende sprint meer te doen voor het project.

### Aya
Ik heb de afgelopen sprint niet heel veel gedaan, gedeeltelijk vanwege de vakantie, al heb ik wel eindelijk ALDS1 afgekregen. Qua groepsproject ben ik best tevreden over de vooruitgang vooral op het gebied van vision (thank you Ying!).


### Ying

Ik ben blij met de progressie die ik heb gemaakt op het gebied van vision, zoals objectdetectie en het verkrijgen van coördinaten.
Ik ben minder blij met de voortgang van mijn persoonlijke opdrachten. Ik heb alleen ALS1 laten aftekenen en ALDS2 is bijna af.
In de volgende sprint wil ik, op basis van de feedback van Colin en Bart, een valve met een hendel maken in Gazebo en deze herkennen met OpenCV, zodat kan bepalen of de valve open is.
Ik wil ook ALDS2, ALDS3 en Computer Vision afronden in de volgende sprint en beginnen met mijn deepdive-onderzoek.

## Sprint retrospective

### Mad

Luuc: ik merkte, vooral bij mezelf, dat ik wat lakser ben geweest in het proces. Dit leidde er toe dat we niet goed wisten waar we mee bezig waren. Dit mede dankzij de meivakantie reset, vrije dagen en afwezigheid teamgenoten. Afwezigheid teamgenoten maakt ook dat het lastiger is om te tracken waar iedereen mee bezig is.

David: ik kon niet heel goed zien waar iedereen mee bezig was. 

Jorn: idem

Ying: idem.

### Sad 

Luuc: hetzelfde als bij mad. 

### Glad

David: we hebben een presentatie voorbereid, net als vorige keer, we staan niet met lege handen voor de opdrachtgever.

Ying: we doen de standup nu beter, is nu standaard elke dag.

### Verbeterpunten retro:

- Scrumboard vaker updaten en doornemen
- Ons aan voorgenomen taken houden, meer updates via daily standup. Op die wijze ook minder langs elkaar werken.
- Minimaal 1 issue voor het project oppakken per dag, indien haalbaar.

