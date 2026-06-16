# Sprint verslag sprint 6
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



## Sprint planning

    Datum : 13-05-2026  
    Afwezig: 
Link naar het scrumboard: [link](https://github.com/orgs/2025-TICT-TV2SE4-24-3-V/projects/5)

Beschikbare capaciteit: 40 uren.



### Feedback teambegeleider


## Daily Scrum

|  Datum: | Afwezig:    | Taken gedaan                                                                                                                                                                                       | Taken niet af:                                       | Taken te doen                                                                                                                                                                                                                                                         | blokkades                                          |
  | --- |-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
|18-05-2026 | David (zonder reden), Aya | Luuc: een beetje aan deepdive <br> Jorn: een beetje aan deepdive. <br> Ying: ALDS 2                                                                                                                | Niks, want was in het weekend niks ingepland         | Luuc: deelvraag 1 en 2 van Deepdive beantwoorden. Jorn: hetzelfde. <br> Ying: Vision Valve detecteren                                                                                                                                                                 | Iedereen: heel lang weekend, iets te veel gechilld |
|19-05-2026 | Niemand :) | Luuc: deelvraag 1 en 2 deels <br> David: PID regeling bijna af <br> Ying: uitrekening hoek. <br> Jorn: nieuw deepdive onderwerp, deelvraag 3 uitgewerkt. <br> Aya: valve model maken               | David: PID <br> Luuc: deelvraag 2 deepdive uitwerken | PID voor project afronden, Vision 2 begin. <br> Luuc: misschien iets voor inverse kinematica (geen beloftes), deelvraag 2 en 3 uitwerken deepdive. <br> Ying: ALDS 3 opdracht 1 minimaal. <br> Jorn: DeepDive. <br> Aya: Valve afmaken, ALDS 2 afronden               | David: bug met PID.                                |
| 21-05-2026 | Niemand | Luuc: deepdive afgerond. <br> Ying: ALDS 2 af, handle code af, maar nog niet getest. <br> Aya: valve model gemaakt, deel van ALDS 2. <br> David: PID geïmplementeerd op de arm <br> Jorn: deepdive | Luuc: Inverse Kinematics :( | Luuc: inverse kinematics code omzetten naar C++. <br> Jorn: Forward kinematics toepassen. <br> David: tunen PID <br> Aya: ALDS 2 afmaken, onderzoek naar afstand berekenen met reguliere. <br> Ying: Hoek berekenen van de valve, K-means <br> Iedereen: peilmoment 3 |
## Sprint review

### Product:

#### Wat ging goed?

Aya heeft een valve gemaakt, vision kan nu de valve detecteren met positie en hoek. David heeft een PID regeling geïmplementeerd op de arm, waardoor we nu een werkende PID hebben. 
Hiermee is vision nu klaar!

Luuc heeft een begin gemaakt met Forward Kinematics, en een skeleton gemaakt voor de inverse kinematics. Forward Kinematics moet nog wel refactored worden, maar het begin is er.


#### Wat ging minder?

Inverse kinematics is nog niet af, we gaan FABRIK gebruiken, maar dat is nog niet geïmplementeerd.


### Individuele inleveringen

Luuc: DeepDive ging oké, moet alleen nog een verdiepende presentatie van 3 minuten doen. Voor de rest: weinig weten te realiseren, maar dat kan want ik was ziek.

Jorn: DeepDive. 

David: Ik heb Gazebo 3 weten af te ronden, ik ga crunchen.

Aya: ALDS 2, OpenCV heeft feedback.

Ying: ALDS 2 en 3 gemaakt en af laten tekenen.



### Persoonlijke reflectie

Luuc: moeizaam, dat is hoe ik het zou omschrijven deze sprint. Het hele proces liep de soep in door mijn ziekte, daarnaast mijn geboekte voortgang ook. Het enige waar ik echt goed aan heb kunnen werken (naast mijn DeepDive) is het forward kinematics stuk, maar ik hád Inverse Kinematics willen doen, wat ik nu niet heb kunnen doen. Lichtpuntje is wel: als dat werkt, is het project bijna af en dat geeft hoop.

Jorn: Mijn werkhouding deze sprint is weer zeer matig geweest, en ik heb, naast mijn deepdive, niet heel veel gedaan. Ik had graag meer progress willen maken op het inverse kinematics gedeelte van het groepsproject, en ga de komende anderhalve week hier veel tijd aan besteden. Verder is er niet veel te zeggen over vorige sprint.

David: Ik ben amper bezig geweest met school, meer dan dat is het eigenlijk niet, hierdoor heb ik het mezelf lekker druk gemaakt voor de komende sprint dus ik moet even knallen de komende laatste paar weken.

Ying: Door mijn uitstelgedrag heb ik deze sprint minder voortgang geboekt dan gepland. Ik heb alleen ALDS2 en ALDS3 afgerond. Daarnaast heb ik de K-Means-opdracht gedeeltelijk voltooid. De komende sprint moet ik echt beginnen met de Deep Dive.

Aya: Ondanks enige persoonlijke obstakels ben ik wel enigszins tevreden met mijn progress deze sprint. ik zal wel nog veel moeten doen volgende sprint, ook aan de persoonlijke opdrachten.

## Sprint retrospective


### Mad

Luuc: Daily standups zijn vrijwel helemaal niet gedaan, omdat bijna niemand aanwezig was of het overnam toen ik ziek was. Hierdoor was er weinig tot geen communicatie over de voortgang van de sprint, wat het moeilijk maakte om problemen tijdig te signaleren en op te lossen.

### Sad

David: de communicatie verliep moeizaam. Daarnaast was de motivatie ver te zoeken, omdat we best dichtbij het einde van het project zitten.

### Glad

Nee, we hebben dezelfde problemen als sprint 5 helaas.

### Verbeterpunten:
- Indien het niet anders kan, aanwezig zijn!!!
- Daily standups dagelijks, als Luuc niet aanwezig is, neemt David het over.
