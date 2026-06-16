# Sprint verslag sprint 3
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

**v0.2.0 [](version-id)** Start document voor scrum uitleg en voorbeelden door HU IICT[](author-id).

---

## Sprint doel
    Het doel van deze derde sprint is om een basis klaar te zetten voor het project, door middel van een simpele arm te modelleren, en een work-environment en simulatie-environment op te zetten zodat we goed kunnen beginnen met werken aan het project.

## Sprint planning 

    Datum :    30-03-2026
    Afwezig: David
Link naar het scrumboard: [link](https://github.com/orgs/2025-TICT-TV2SE4-24-3-V/projects/5)
    
Beschikbare capaciteit: 40 uren.  


Het sprintdoel voor de komende sprint is: 
  - Begin robotarm in Gazebo maken 
  - Begin environment in Gazebo maken 
  - Functional en non-functional requirements opstellen 
  - Work environment opzetten in de team repository


### Feedback teambegeleider


Vorige week (tijdens de teamcoach meeting van 01-04-2026) gaf Hasan aan dat er te weinig progressie was in het project. Voornamelijk op het gebied van het proces had hij een aantal aanmerkingen. De aanmerkingen zijn als volgt:
- Het scrumboard was onoverzichtelijk, er was niet echt te zien wat ieder teamlid gedaan had en wat er was
- Daarnaast was er ook een gebrek aan een sprint backlog.
- Daarnaast was er een gebrek aan daily standups, deze waren niet daily helaas.

Na overleg met Hasan en het team hebben we de volgende concrete actiepunten ondernomen:
- Er is een scrum-master switch geweest, Luuc is nu in plaats van Jorn scrum-master.
- Het scrumboard is grondig hervormd, taken zijn nu opgedeeld in stukken van ongeveer 2-3 uur. De structuur is ook aangepast om overzichtelijker te zijn (voorbeeld: ipv één grote backlog met persoonlijke opdrachten wordt dit nu per sprint gedaan).
- Daily standups zijn nu dagelijks en in een uitgebreider format. 


## Daily Scrum

  |  Datum: | Afwezig: | Taken gedaan                                                                                                                                                                                                                                                                            | Taken niet af:                                                                                                                               | Taken te doen                                                                                                                                                                                                           | blokkades                                                                                                                                                         |
  | --- |----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  |  30-03-2026 | David, Ying | Sectie 31-3 toegevoegd door Luuc, nog nvt.                                                                                                                                                                                                                                              | Luuc: Onderzoek draft, POP. Jorn: Gazebo 3, STL, OpenCV, Algoritmes en datastructuren. Aya: C++ STL, Onderzoek draft                         | Sectie 31-3 toegevoegd door Luuc, nog nvt.                                                                                                                                                                              | N.v.t                                                                                                                                                             |
  |  31-03-2026 | Ying, Jorn | David: final versie arm. Luuc: README voor devcontainer, ALDS 1, OpenCV t/m color filter opdracht. Aya: OpenCV t/m color filter opdracht.                                                                                                                                               | Luuc: ROS onderzoek, bleek overbodig. OpenCV opdracht. Aya: OpenCV opdracht                                                                  | Luuc: OpenCV opdracht, documentatie devcontainer afronden. David: finale tweede versie arm. Aya: OpenCV afronden.                                                                                                       |
  |  01-04-2026 | David    | Luuc: Documentatie van de devcontainer afgemaakt. Ying: Documentatie gelezen tot pagina 20. Aya: Niks, geblokkeerd door bussen. Jorn: Niks.                                                                                                                                             | Luuc: OpenCV opdracht, onderzoek draft. Ying: OpenCV opdracht, onderzoek draft. Aya: OpenCV opdracht. Jorn: Gazebo 3, STL, Vision 1, ALDS 1. | Luuc: OpenCV opdracht. Ying: OpenCV opdracht, Onderzoek draft. Aya: OpenCV afronden. Jorn: Gazebo 3, STL, Vision 1, ADS 1.                                                                                              |
| 02-04-2026 | Niemand  | Luuc: David: final versie van de arm nu officieel af. Jorn: POP reflectie  Aya: OpenCV, behalve hough lines. Ying: overview systeem gelezen, korte samenvatting gemaakt                                                                                                           | Luuc: zie 01-04-2026 Jorn: zie 01-04-2026 Aya: OpenCV verder afmaken                                                                         | Luuc: zie 01-04-2026. David: environment met duidelijke documentatie maken. Jorn: zie 01-04-2026 Ying: OpenCV afmaken, onderzoeken hoe de base te roteren                                                               |                                                               | 
| 08-02-2026 (paar dagen niet ivm paasweekend) | niemand  | Luuc: Usecases, ontwikkeldocument start, POP persoonlijk, deel draft onderzoek en OpenCV. David: omgeving V2, en documentatie daarvoor.  Jorn: Gazebo 3, grotendeels. Ying: onderzoek draft ingeleverd, base roteren heeft Aya overgenomen. Aya: robotarm laten bewegen, start vision 2. | Luuc: deel draft onderzoek en OpenCV. Jorn: ongeveer hetzelfde gebleven tov 02-04-2026. Aya: vision 2                                        | Luuc: Draft onderzoek en OpenCV, usecasediagram, pull request voor devcontainer. David: een kleine GUI om joints te kunnen besturen. Jorn: STL opdracht. Ying: ALDS 1. Aya: vision 2 en joints updaten naar nieuwe sdf file. |  |
|09-04-2026 | David    | Jorn: Gazebo 3! <br> Luuc: draft onderzoek, usecasediagram, devcontainer nog meer gefixt <br> Ying: ALDS 1, opgave 1 en 2.                                                                                                                                                              | Luuc: OpenCV <br> Jorn: STL <br>                                                                                                             | Allen: sprint review / retro. <br> Jorn: STL. <br> Luuc: OpenCV  <br> Aya: CV2 <br> Ying: ALDS1, reflectie op POP | Luuc: ALV op donderdag |

## Sprint review
    Datum:      09-04-2026
    
### Product:
#### Wat ging goed?

#### Jorn
We hebben beweging in de arm gekregen, wat het doel was van de sprint

#### Luuc 
Zie [Jorn](#jorn)

#### Aya 
We hebben beweging in de arm gekregen, we zijn goed op weg om het product te realiseren. Het is nog niet af, maar we zijn wel lekker bezig.

#### Ying
Idem, we hebben af wat we hebben gepland

#### Wat ging minder? 

#### Jorn
Niet iedereen heeft evenveel input geleverd aan het product (ook verbonden aan het proces).

#### Luuc
Buoyancy test is niet uitgevoerd, dit is jammer.  
De functionaliteit van het product moet meer opgedeeld worden

#### Aya
Ik ben het eens met Jorn, ook omdat ik deels Ying haar onderdeel heb overgenomen, gezien het 

#### Ying
Hetzelfde.

---

### Individuele inleveringen

#### Luuc
Veel is gelukt, een paar dingen niet. Overall, goede progressie, maar wel verbetering in de pocket nog.

#### Aya 
Er zijn een aantal starts gemaakt, maar niks is ingeleverd

#### Jorn
Ik moet keihard aan de bak volgende sprint, er was een achterstand in deze is blijven oplopen. Ik heb onderzoek draft en reflectie POP ingeleverd.

#### Ying
IK heb onderzoek draft ingeleverd, OpenCV1. 

    
### Persoonlijke reflectie
    

#### Jorn
Ik had persoonlijk meer kunnen doen voor de persoonlijke- en groepsopdrachten. Ik ben wel erg tevreden met hoe het proces verloopt nadat ik de taak van scrummaster, na een zeer kort overleg, heb overgelaten aan Luuc. Ik ben erg positief over de progressie van het team over deze sprint, en de beweging van de arm is al een zeer belangrijke milestone die hierin bereikt is. Zoals eerder genoemd, wil ik de volgende sprint zo snel mogelijk alle achterstallige opdrachten bijwerken, en ook meer bijdragen aan het project door het maken van een betere taakverdeling.

#### Luuc
Ik ben over het algemeen positief over de voortgang die wij geboekt hebben als team in deze sprint, voornamelijk in de tweede week merkte ik dat we serieus aan de slag gingen om het project wat te maken. Ik merk ook dat door het overnemen van de taak scrummaster het proces nu een stukje soepeler verloopt, we doen daily standups, het board word geüpdatet, en iedereen weet zo ongeveer waar ze mee bezig moeten.
Wel had ik zelf iets meer willen doen deze sprint, vooral op technisch vlak heb ik weinig bijdrage geleverd, maar ik heb het idee dat dit deels gecompenseerd is door de administratieve zaken.

#### Ying
Ik vind dat ik deze sprint iets meer heb gedaan dan de vorige sprint, en dat vind ik goed.
Ik loop nog 4 opdrachten achter en ik heb nog niets ingeleverd voor het projectproduct, en dat vind ik minder fijn.
In de volgende sprint wil ik de achterlopende opdrachten afronden en iets inleveren voor het projectproduct

#### David
Ik heb deze sprint niet veel aan mijn persoonlijke opdrachten gedaan dat moet ik de komende sprint even inhalen maar dat lukt wel. voor groepsproject heb ik wel lekker wat kunnen doen dus volgende sprint gaat voor mij wat meer focus op de persoonlijke projecten liggen

#### Aya
Ik ben tevreden met de vooruitgang van het groepsproject afgelopen sprint, al kan ik helaas niet hetzelfde zeggen over de persoonlijke projecten. Ook de planning en het proces van het groepsproject zijn verbeterd, hoewel er wat betreft de taakverdeling nog ruimte voor verbetering is. Ik merk wel dat elke sprint een beetje beter gaat dan de vorige, dus hopelijk zet die trend zich voort.

### Peer Assessment
  Feedback van alle teamleden per student.
  Per student geef je aan:
   1) Wat ging er goed? Waar zit de kracht van die student?
   2) Waar zitten verbeterpunten/ontwikkelkansen?
   3) Krijgt de student een: 
  🤬 , ☹️, 😐 , 😀, 😁

| Persoon | Wat ging goed                                                                                                               | Wat ging minder goed | Smiley | 
|-----------|-----------------------------------------------------------------------------------------------------------------------------|--------------------|------------------------|
| Aya | De arm laten bewegen, hier zijn wij blij mee                                                                                |  | 😀 |
| Luuc | Heeft het initiatief genomen om de taak scrum-master op zich te nemen nadat het niet soepel verliep                         | Niet veel taken technisch voltooid voor het project | 😀 |
| Jorn | Scrum-masterschap overgegeven aan Luuc na overleg, dit toont een zekere vorm van bescheidenheid.                            | Niet veel gedaan voor het project | 😐/😀 | 
| Ying | Als eerste aan de slag gegaan met de gestelde taken, toont goed proactiviteit. Zelfde geldt voor de persoonlijke opdrachten | Zelfde als Luuc en Jorn, maar dat komt vooral door de taakverdeling | 😀|

Wij hebben David in de peer assessment niet meegenomen deze keer, omdat hij niet aanwezig was bij de peer assessment

Het bepalen van de feedback gebeurt met de student in kwestie er bij (die mag ook vragen stellen ter verduidelijking). Het blijft echter wel de indruk van het team (is per definitie subjectief). 

## Sprint retrospective
    Datum : 09-04-2026
    Afwezig: David
 
    Verbeterpunten voorgaande retro: -
    - Betere taakverdeling
    - daily stand-ups
    - Weekelijkse meeting 1 uur na de les
    
 
    Link naar retro bord: https://github.com/orgs/2025-TICT-TV2SE4-24-3-V/projects/5/views/9
        
    Retro methode: Mad, Sad, Glad

    Mad, grote knelpunten
    Jorn: niet echt iets, alles ging best goed
    Aya: ook niet echt iets
    Ying: ook niet echt iets
    Luuc: idem

    Sad / aandachtspunten
    Jorn: taakverdeling had nog steeds beter gekund, deze is nog steeds enigszins oneven. Ik heb het gevoel weinig gedaan te hebben voor het project
    Aya: idem, m.u.v. het laatste stuk
    Ying: bijna hetzelfde, volgende sprint wil ik meer doen qua inleveringen
    Luuc: hetzelfde als de rest, voornamelijk door de administratie (scrum-master switch, herindeling boards) heb ik weinig tijd overgehouden voor andere zaken.

    Glad, successen
    Jorn: de administratie is nu goed op orde, het proces verloopt soepeler.
    Aya: beetje hetzelfde als Jorn
    Ying: ik ben blij dat we meer contact hebben met elkaar, en dat we elkaar meer up to date houden over de voortgang
    Luuc: idem, samen met dat de sfeer steeds gezelliger word en dat we serieuzer aan de slag gaan, zonder oog voor elkaar (en de fun) te verliezen.

    Maximaal drie verbeterpunten uit de retro: 
    - Taakverdeling, nog steeds een ding van vorige sprint. Dan weet iedereen waar hij/zij aan toe is.
    - Presentatie voorbereiden voor de opdrachtgever, meer voorbereiden op meetings (issue maken op scrumboard!!)

    
### Feedback opdrachtgever (Colin)

Zie meeting notes.


### Feedback Bart

- Sprint verslag GEEN humor verwerken, dat leidt af
- Voor de rest: zeer grondig gedaan
- Let op de leesbaarheid van kopjes.
- Neem Collin mee in wat we gaan doen!!!!!!!!
- Daily standups zeer uitgebreid en goed uitgevoerd.