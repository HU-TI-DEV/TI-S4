# Sprint verslag sprint 4
# Nautilus

### Inhoud[](toc-id)
- [Sprint doel](#sprint-doel)
- [Sprint planning](#sprint-planning)
    - [Feedback teambegeleider](feedback-teambegeleider)
- [Daily Scrum](#daily-scrum)
- [Sprint review](#sprint-review)
    - [Feedback teambegeleider/ Product owner](#feedback-teambegeleider-product-owner)
    - [Persoonlijke reflectie](#persoonlijke-reflectie)
    - [Peer Assessment](#peer-assessment)
- [Sprint retrospective](#sprint-retrospective)
    - [Feedback teambegeleider](#feedback-teambegeleider-1)


    
---

## Sprint doel

- PID controller per onderdeel van de robotarm toepassen
- Iedereen in de devcontainer laten werken
- Documentatie, met name activity diagram, key drivers, functionele decompositie, en klassendiagram
- Achterstand persoonlijke opdrachten bijwerken
- Begin maken met vision, onderzoek op welke manier wij dit toe willen passen.

## Sprint planning

    Datum : 13-04-2026  
    Afwezig: 
Link naar het scrumboard: [link](https://github.com/orgs/2025-TICT-TV2SE4-24-3-V/projects/5)

Beschikbare capaciteit: 16 uur per persoon per week (project, persoonlijke opdrachten niet meegenomen)

Dat betekent met de omvang van de issues: 5 taken per persoon per week



### Feedback teambegeleider



## Daily Scrum

|  Datum: | Afwezig:                     | Taken gedaan                                                                                                                                                                                                                                                                                                                                 | Taken niet af:                                                                                                                                         | Taken te doen                                                                                                                                                                                                                                                                                                                                                                           | blokkades                                                                                                                                                                                                                                                                |
  | --- |------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 13-04-2026 | Niemand                      | Luuc: Devcontainer met iGPU support <br> Ying: Reflectie op POP, ALDS 1 bijna. <br> Jorn: Mission booklet samengevat tot aan mission details, STL opdracht tot aan opdracht 4. <br> Aya: beide OpenCV opdrachten half. <br> David: Reflectie op POP, Algoritmes en Datastructuren 1, Onderzoek - draft inlevering.                           | Luuc: OpenCV <br> Ying: ALDS 1 <br> Jorn: STL overige 6 opdrachten                                                                                     | Luuc: OpenCV Hough Lines en color ranges, requirements updaten en usecases updaten. <br> Ying: ALDS 1 helemaal afmaken <br> Jorn: STL overige 6 opdrachten                                                                                                                                                                                                                              | Luuc: devcontainer ging stuk, pluspunt is dat hij nu geüpdatet is. <br> Aya: weet bij OpenCV niet hoe verder te gaan, gaat een vraag stellen aan Bart hierover                                                                                                           |
| 14-04-2026 | David                        | Luuc: OpenCV, ex Hough Circles. Documentatie devcontainer geüpdatet, iedereen kan er nu in werken. <br> Jorn: samenvatting mission booklet, C++ STL. <br> Ying: ALDS opdrachten. <br> Aya: geprobeerd de devcontainer                                                                                                                        | Luuc: Hough Circles, Requirements Bijwerken en Usecases bijwerken. <br> Ying: ALDS 1 stukjes                                                           | Luuc: gaat vandaag afmaken wat gisteren niet gelukt is. <br> Jorn: begin OpenCV, eindverslag samenvatten. <br> Ying: ALDS 1 Opdrachten bijwerken, onderzoek naar toepassing van Computer Vision.                                                                                                                                                                                        | Luuc: operatie broertje, beetje spanning daarvan. Werk en commissievergadering tot laat. <br> Ying: kon haar aandacht niet bijhouden gisteren.                                                                                                                           |
| 15-04-2026 | Jorn                         | Luuc: OpenCV, requirements updaten, key drivers toevoegen aan ontwikkeldocument <br> David: ALDS2 tot opdracht 2 <br> Aya: OpenCV afgemaakt <br> Ying: 1 vraag uit ALDS 1, Computer Vision uitzoeken, objectherkenning toegepast.                                                                                                            | Luuc: usecases bijwerken <br> David: ALDS 2 helemaal afronden <br> Aya: devcontainer installeren <br> Ying: ALDS1                                      | Luuc: usecases bijwerken, functionele decompositie proberen te maken, ALDS2 opdracht 1 en 2 <br> David: joint controller onderzoeken, begin PID uitzoeken. <br> Aya: kijken of ze de devcontainer werkend kan krijgen. <br> Ying: verder met computer vision, ALDS 1 afronden                                                                                                           | Luuc: stress. <br> David: ALDS 2 was best taai <br> Aya: haar Docker werkt niet goed, WSL is kapot gegaan                                                                                                                                                                | 
| 16-04-2026 | Niemand                      | Luuc: usecases geüpdatet, functionele decompositie gemaakt <br> David: joint control maken. <br> Ying: Camerabeweging in code geïmplementeerd <br> Jorn: samenvatting eindverslag, tot en met pagina 15 <br>  Aya: devcontainer werkt nu, docker werkt weer, OpenCV2 1 opdracht                                                              | Luuc: ALDS 2 opdracht 1 en 2 <br> David: joint control toepassen. <br> Ying: De camera laten stoppen indien een object gedetecteerd is. <br> Aya: niks | Luuc: peilmoment 2, Colin en Bart mailen, ALDS2 opdracht 1 en 2, hydrodynamica plugin testen <br> David: eigen opdrachten inhalen dit weekend (want het is donderdag), peilmoment 2   <br> Ying:  De camera laten stoppen indien een object gedetecteerd is, peilmoment 2. <br> Aya: peilmoment 2 <br> Jorn: Peilmoment 2, verschillende persoonlijke opdrachten, bepaalde documentatie | Luuc: nvt <br> David: de blauwe joint beweegt niet <br> Ying: camera laten stoppen wanneer object gedetecteerd is werkt nog niet. <br> Jorn: vriend uit Engeland ging terug naar huis, moest helpen met inpakken en wegbrengen. <br> Aya: nvt, want docker doet het weer |
| 20-04-2026 | Ying (heeft wel doorgegeven) | Ying: peilmoment 2, camera laten stoppen met bewegen wanneer hij het doelobject herkent, depth camera geïmplementeerd in SDF. <br> Jorn: OpenCV <br> David: OpenCV 1, tot laatste opdracht. <br> Aya: peilmoment 2, OpenCV 1 met experiment gedeelte. <br> Luuc: peilmoment 2, Hydrodynamics plugin getest, PID skeleton class zonder logica | Jorn: samenvattingen documentatie <br> Aya: een start maken met PID voor de robotarm. <br> Luuc: ALDS 2 opdrachten 1 en 2                              | Ying: Camera verplaatsen naar een andere plek. Onderzoeken hoe ik ook de richting van de afstand kan meegeven met de meting. <br> David: OpenCV 1 afmaken, documentatie voor joint control. <br> Luuc: ALDS 2 opdracht 1 en 2, Klassendiagram                                                                                                                                           | Ying: nvt <br> Jorn: internet werkte niet op zondag                                                                                                                                                                                                                      |

## Sprint review

### Product:

#### Wat ging goed?

#### Luuc: 

We hebben in deze sprint een mooie vooruitgang weten te boeken met het product, vooral op het gebied van het bewegen en vision zijn we lekker bezig geweest.

#### Aya: 

Vooruitgang ging goed, we zijn zeker verder gekomen. 
Het product krijgt mooi vorm. 

#### Ying:

Ik vind ook dat we een goede vooruitgang hebben geboekt, zie feedback van Aya en Luuc.

#### David:

JointControl deel ging vooral goed, ook qua onderzoeken gaan we nu lekker snel. Volgende sprint denk ik om die reden dat we nog meer progressie kunnen boeken.

#### Jorn:

We hebben goede progress gemaakt, dingen als JointControl en Vision zit vaart in. We gaan de goede kant op.

#### Wat ging minder?

#### Luuc: 

Voor hydronamics test had ik de natuurkunde beter door kunnen hebben, deze is nu van andere bronnen vrijwel klakkeloos overgenomen. Het resultaat klopt m.i. wel, maar het gaat vooral om begrip.

#### Ying:

Depth camera kan niet onderwater gebruikt worden, dat is jammer. Hier is niet helemaal goed over nagedacht voordat dit onderzocht werd.

#### David:

Het opzetten van de devcontainer ging soms stroef, ben ik best een tijdje mee bezig geweest. Vooral gezeur met WSL en Docker.

#### Jorn: 

Ik heb niet iets gehad waarvan ik dacht dat het echt verkeerd ging.

#### Aya:

Devcontainer was (zoals bij David) een gezeurtje om op te zetten, vooral ook door de eerder genoemde problemen met Docker en WSL.


### Individuele inleveringen

#### Luuc

Er zat niet veel vaart in de individuele inleveringen bij mij. Ik zie ook terug in het scrumboard dat we hier als team nog niet echt mee opgeschoten zijn. Dit komt voornamelijk omdat de focus van deze sprint op het project gefocust was.

Ik hoop in de vakantie een inhaalslag te kunnen doen op dit gebied.

#### Ying

Ik vind het goed dat ik in deze sprint iets voor vision heb gedaan. Ik moet meer tijd besteden aan mijn persoonlijke opdrachten.

#### Aya

OpenCV is eindelijk tot een satisfactory einde gebracht, en all things considered ben ik ook wel tevreden over de voortgang van het verantwoordingsdocument voor peilmoment 2. Verder heb ik vooral veel beginnen gemaakt aan opdrachten maar minder die ook echt af zijn gekomen.

#### David

Persoonlijke opdrachten zijn best prima verlopen, liep alleen weer met die devcontainer een beetje vast omdat ik daar een paar opdrachten in wou maken maar desondanks  heb ik prima vooruitgang kunnen boeken.

#### Jorn

Voor de inviduele inleveringen had ik meer kunnen doen, ik loop nog erg achter met de persoonlijke opdrachten en moet hierbij nog echt wel bijwerken. Ik ga voornamelijk in de vakantie bij werken, maar tot nu toe gaan de opdrachten die ik heb gedaan prima en ben ik nergens tegen aan gelopen.

### Persoonlijke reflectie

#### Luuc

Ik ben zeer tevreden over deze sprint, ondanks de kleine downs waren er zeker ook ups, voor het eerst heb ik echt het gevoel dat we met z'n allen goed betrokken zijn. We hebben als team goede vooruitgang kunnen boeken, ondanks de tijd die wij hadden. Qua documentatie waren Colin en Bart ogenschijnlijk tevreden, dus dat maakt mij ook blij. Daarnaast vind ik het best een eer dat Bart mijn devcontainer setup nu de "standaard" wil maken voor de klas (in overleg met Jan en Nick).

Wel ben ik nog ontevreden over de hoeveelheid persoonlijke opdrachten die ik maak, dit is iets dat vaker terugkomt en ik heb daar nu een support system voor. Ik hoop volgende sprint op technisch vlak nog een tandje bij te zetten, hoewel ik dit al heb gedaan (hydrodynamics testen).

#### Jorn

Ik vind dat ik persoonlijk meer had kunnen doen voor het groepsproject en voor de persoonlijke opdrachten, ik heb de focus nu vooral gehouden op het samenvatten van documentatie die aan ons is geleverd door Colin. Ik hoop de volgende sprint meer te kunnen doen aan taken gerelateerd aan de simulatie zelf. Verder ben ik erg tevreden met hoe deze sprint is verlopen.

#### David

Persoonlijke reflectie - Ik heb deze sprint wel een stuk meer  tijd in school kunnen stoppen dat was heel fijne en heb ook echt gemerkt dat ik een stuk meer af heb kunnen maken maar had daarnast wel een stuk meer aan mijn persoonlijke opdrachten willen werken.

#### Ying

Ik heb in deze sprint iets voor vision aan het groepsproject gedaan. Hier ben ik blij mee. In de volgende sprint wil ik hiermee doorgaan. Ik wil ook meer aan mijn persoonlijke opdrachten werken, omdat ik daar veel achterloop.

#### Aya

Ik ben heel tevreden met de afgelopen sprint en vind dat we goede vooruitgang hebben geboekt. Tegelijkertijd voelt het gebruik van het woord "we" enigszins onterecht, aangezien ik mijn eigen bijdrage ontoereikend vind. Ook mijn voortgang op het gebied van de persoonlijke opdrachten laat nog wat te wensen. Desalniettemin vind ik wel dat de sprint als geheel succesvol was



Het bepalen van de feedback gebeurt met de student in kwestie er bij (die mag ook vragen stellen ter verduidelijking). Het blijft echter wel de indruk van het team (is per definitie subjectief).

## Sprint retrospective

Dit is onze reflectie op het proces.

Verbeterpunten voorgaande retro:

- Taakverdeling, nog steeds een ding van vorige sprint. Dan weet iedereen waar hij/zij aan toe is.
- Presentatie voorbereiden voor de opdrachtgever, meer voorbereiden op meetings (issue maken op scrumboard!!)

Gebruikte retro methode: Mad, Sad Glad

### Mad - grote knelpunten:

#### Luuc 
Ik had niet echt grote knelpunten waar ik tegenaan liep

#### David
De devcontainer liep ik tegenaan, ik was best geïrriteerd nadat ik deze had opgezet.

#### Jorn

Hetzelfde als de sprint review, niet echt iets groots

#### Ying

Geen grote knelpunten

#### Aya

Mijn eigen bijdrage vond ik onvoldoende binnen het project

### Sad - aandachtspunten

#### Luuc

We zijn best laat begonnen met het maken van een sprint planning, waardoor wij functioneel een sprint hadden van een week. Hierdoor is er minder dan gepland afgekomen.

#### David

Ik ben het met Luuc eens over zijn punt, ik wilde iets meer aan eigen opdrachten zitten. 

#### Ying

Ik heb mijn planning niet helemaal goed uitgewerkt, waardoor ik alles last minute moest doen.

#### Jorn

Mijn sad is hetzelfde als Luuc, we zijn best laat begonnen met deze sprint.

#### Aya

Mijn sad is hetzelfde.


### Glad - successen

#### Luuc:

We hebben op het proces een grote vooruitgang geboekt t.o.v. vorige sprint, waardoor we nu op een rap tempo bezig zijn met het project.

Het verdelen van taken (en het aanmaken hiervan!) wordt nu door iedereen gedaan, waardoor iedereen wel iets oppakt op een dag. Dat zorgt voor incrementele, rappe voortgang.
#### David:

We hebben goed aan Colin kunnen laten zien wat we hebben gedaan. 

Het proces is nu voor iedereen duidelijk, wat we moeten doen en wat we gaan doen is nu duidelijk. Door dat gestructureerde werken hebben we in een korte tijd best wat progressie kunnen maken.

#### Jorn:

Ik vind het een geweldige vooruitgang dat we Colin tevreden hebben kunnen maken, ondanks dat we maar een week hadden deze sprint.

#### Aya:

Hetzelfde als Jorn, de progressie was goed voor de tijd die we hadden.

#### Ying:

We hebben een presentatie voorbereid voor de meeting, dat is een positieve ontwikkeling.

Daarnaast vind ik het goed dat we de taken nu op een goede manier verdelen, we hebben een bucket aan issues en we doen elke dag iets voor het project.

### Verbeterpunten uit de retro

- Sprint planning eerder maken


## Feedback opdrachtgever

Zie meeting notes