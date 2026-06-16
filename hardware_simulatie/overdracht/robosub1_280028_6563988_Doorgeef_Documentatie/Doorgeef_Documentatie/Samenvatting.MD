<!-- markdown-link-check-disable -->

<div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
  <img src="https://www.hu.nl/-/media/hu/afbeeldingen/algemeen/hu-logo.ashx" alt="HU Logo" height="50" />
  
  <img src="https://robosub.nl/assets/logo.webp" alt="HU Robosub Logo" height="80" />
</div>


<br clear="all" />

# Samenvattingsdocument RoboSub team Narwal

## Projectomschrijving & Context

Dit project is uitgevoerd in samenwerking met [RoboSub](https://robosub.nl). Binnen de missie van Robosub staat het verkennen en beschermen van de onderwaterwereld centraal, waarbij de nadruk ligt op de ontwikkeling van autonome onderwaterrobots (AUVs) voor complexe onderzoekstaken en onderhoud. Een belangrijk onderdeel van de huidige competitie is de volgende operatie: de AUV moet volledig zelfstandig naar een onderwater valve navigeren, het handvat van deze valve grijpen en deze exact een kwartslag draaien. 

Wij hebben de opdracht gekregen om de arm module voor de robosub, die de actie moet uitvoeren, realistisch te modelleren in Gazebo zodat er in een digitale omgeving getest kan worden. 


## Inhoudsopgave
- [Projectomschrijving & Context](#projectomschrijving--context)
- [Systeemspecificaties & Eisen](#systeemspecificaties--eisen)
  - [Key Drivers](#key-drivers)
  - [Requirements](#requirements)
  - [Use Cases](#use-cases)
- [Onderzoek](#onderzoek)
  - [Gazebo](#gazebo)
  - [PID-Controller](#pid-controller)
  - [Vision](#vision)
  - [Inverse Kinematica](#inverse-kinematica)
- [Groepsproces Narwal](#groepsproces-narwal)
- [Systeemvereisten & Installatiehandleiding](#systeemvereisten--installatiehandleiding)
- [Aanbevelingen](#aanbevelingen)


## Systeemspecificaties & Eisen
Dit hoofdstuk beschrijft de fundamentele kaders en ontwerpeisen van de simulatieomgeving. Door de doelen (Key Drivers), criteria (Requirements) en processtappen (Use Cases) samen te bekijken, ontstaat een heldere blauwdruk van wat het systeem moet realiseren.

---
### Key Drivers
De keuzes binnen de het project worden geleid door drie prioriteiten die zijn afgestemd de opdrachtgever:

- __Realistisch:__ De simulatie moet het fysieke model, de kinematica en de dynamica natuurgetrouw nabootsen om bruikbaar te zijn. 
- __Overdraagbaarheid:__ De documentatie moet duidelijk zijn, zodat de volgende projectgroep van RoboSub hier direct op door kan bouwen.
- __Functionaliteit:__ De robotarm boet autonoom kunnen bewegen en trainbaar zijn om patronen te herkennen. 

_Bekijk alle key drivers en de stakeholder prioritering in het [Key Drivers Document](Systeemspecificaties_&_Eisen/Key_Drivers.md)._

---

### Requirements
 Het systeem is ontworpen rondom een set met RoboSub afgestemde eisen. 

- __Must Haves:__ De robotarm moet zich kunnen uitstrekken, de valve kunnen vastpakken, exact een kwartslag roteren en voorzien zijn van overdraagbare productdocumentatie.
- __Should Haves:__ De robotarm zou Real-time dynamica berekeningen, zwaartekracht/hydrauliek componenten, en een correct gepositioneerde camera voor objectdetectie moeten hebben.
- __Constraints:__ De RoboSub arm heeft fysieke grensen aan de hoeken die er gemaakt kunnen worden door de plaatsing onder de RoboSub. 

_Voor alle functionele en niet functionele eisen en constraints, zie het complete [Requirement Document](Systeemspecificaties_&_Eisen/Requirements.md)._

---

### Use Cases
Om de brug te maken tussen de eisen en de praktijk, zijn de handelingen opgedeeld in concrete scenario's. Denk hierbij aan de automatische aansturing, het exporteren van testdata en het visueel vergelijken van verschillende simulatieruns.

_De uitgeschreven use cases zijn te vinden in het [Use Cases Document](Systeemspecificaties_&_Eisen/Use_Cases.md)._

---


## Onderzoek
Voordat wij zijn gestart met de implementatie in Gazebo, is er diepgaand technisch onderzoek verricht op basis van de gestelde eisen. Dit hoofdstuk bundelt deze onderzoeken samen om een duidelijk beeld neer te zetten over de gemaakte conclusies. 

---
### Gazebo
Voor dit project wordt er gebruik gemaakt van het simulatieprogramma Gazebo. Om een solide basis te leggen, hebben we onderzocht hoe we binnen deze omgeving robotmodellen kunnen opbouwen en aansturen. 

Dit onderzoek richt zich specifiek op het maken van fysieke vormen (links) en het definiëren van de juiste gewrichten (joints).

- **Fysieke vormen (Links):** Elk component van de robotarm is opgebouwd uit drie fundamentele lagen: Visual (weergave), Collision (botsing) en Inertial (massa). Om de simulatie in deze fase simpel te houden wordt er gebruik gemaakt van geometrische basisvormen.
- **Gewrichten (Joints):** Na een comparatieve analyse van de beschikbare joint typen binnen Gazebo, is er gekozen voor revolute joints. Dit type sluit direct aan op de werkelijke hardware en stelt ons in staat om hoekbegrenzingen in radialen af te dwingen.
- __Plaatsing (Offset):__ Op advies van de opdrachtgever hebben we de scharnierpunten een klein stukje binnen de vormen geplaatst. Door deze overlap snijden de 3D blokken elkaar niet tijdens het buigen, wat trillingen en fouten in de simulator voorkomt.

Door te kiezen voor simpele basisvormen, realistisch begrensde scharnieren en de juiste overlap, staat er nu een stabiele robotarm van zeven gewrichten.


_Het volledige theoretische kader en verdere onderbouwing is te vinden in [Gazebo Basisopbouw & Verbindingen Onderzoek](Onderzoek/Gazebo_Basics.md)._

---

### PID-Controller

Na het opzetten van de stabiele basis, is onderzocht hoe de robotarm nauwkeurig en autonoom gepositioneerd kan worden om de valve te bedienen. 

Dit onderzoek richt zich op de theorie en implementatie van een PID-regelaar binnen Gazebo en de live aansturing van de gewrichten.

- __Position Control__: In plaats van snelheidssturing is er gekozen voor positiesturing. Gazebo heeft een ingebouwde PID-regelaar (`JointPositionController`) die direct op de hoogste frequentie van de physics engine rekent. Dit zorgt voor maximale stabiliteit, voorkomt trillingen en werkt als een actieve vergrendeling tegen externe onderwaterkrachten.
- __Toetsenbord Aansturing:__ Als stabiele tussenoplossing voor hardware beperkingen is er een Python script ontwikkeld dat toetsenbord- nputs live vertaalt naar hoeken in radialen. Deze gewenste hoeken worden via het `/cmd_pos` topic direct naar de ingebouwde PID-controller van Gazebo gestuurd.
- __Probleempunten & Optimalisatie:__ Voor nu is de communicatie opgezet via `os.system`. Omdat dit voor elk bericht een nieuw terminalproces start, veroorzaakt dit momenteel merkbare haperingen. 

De datastroom tussen de gebruiker, het Python-script en de simulator is als volgt opgebouwd:

![Datastroom toetsenbord input](Onderzoek/Images/User%20Input%20Management-2026-05-31-134859.png)
___Diagram 1:__ Datastroom RoboSub arm met toetsenbord input.<br >Opmaak van deze diagram is gegenereerd met behulp van Gemini AI en handmatig geverifieerd._



 #### __Aanbevelingen:__
 

Aan de hand van dit onderzoeken zijn er aanbevelingen opgesteld:


___
__Permanente API toevoegen__

De ingebouwde PID-regeling van Gazebo bewijst een stabiele basis te zijn voor nauwkeurige positionering. Om van deze testfase over te stappen naar een eindproduct, zijn de directe vervolgstappen geidentificeerd: de migratie van toetsenbord naar analoge controller input en het vervangen van `os.system` door een permanente API-koppeling om de communicatielijn open te houden.

---

__Migreren naar fysieke controller input__

Vanwege hardware beperkingen op de gebruikte laptop is er tijdelijk gekozen voor toetsenbord input. De basis in de code staat al. Dit kan functioneel worden omgeschreven naar een script dat continu de analoge assen van een fysieke controller uitleest, zodat de arm met een joystick bestuurd kan worden.

---

_Voor de volledige theoretische onderbouwing en implementatie ga naar [Gazebo PID-Regeling & Aansturing Onderzoek](Onderzoek/PID.MD)._

---

### Vision

Na het opzetten van de besturing, was een betrouwbare visuele waarneming vereist om objecten autonoom te kunnen detecteren. Dit onderzoek richt zich op de implementatie van een YOLO-gebaseerd detectiesysteem en de integratie hiervan met de robot pipeline.

* **Deep Learning (YOLOv5s)**: In plaats van een klassieke OpenCV-benadering is gekozen voor een deep learning model (YOLO). Dit model is getraind via 'Transfer Learning', wat zorgt voor hogere robuustheid tegen wisselende belichting, camerahoeken en achtergrondruis vergeleken met handmatige filter-algoritmen.
* **Confidence-gestuurde Detectie**: Elke detectie levert een confidence-score op. De pipeline filtert op basis van deze score, waardoor we onzekere detecties negeren en de betrouwbaarheid van de vervolgacties (het bewegen van de arm) waarborgen.
* **Probleempunten & Optimalisatie**:
* **Dataset Bias**: De huidige trainingsdata leunt te sterk op de 'groundplane' van de simulatie. Dit beperkt de generalisatie naar andere omgevingen; hertraining met een gevarieerdere dataset is vereist.
* **Model Efficiëntie**: Hoewel YOLOv5 functioneel is, biedt een overstap naar modernere architecturen (zoals YOLO11) aanzienlijke winst in inferentiesnelheid en precisie, wat cruciaal is voor real-time toepassingen.

#### __Aanbevelingen:__
Wij geven het volgende advies voor eventuele volgende stappen door:

---
__Dataset Herschrijven:__

 De huidige dataset is te specifiek en leunt te zwaar op de groundplane (de bodem van de simulatie), wat zorgt voor bias. Het is noodzakelijk om nieuwe data te verzamelen met meer variatie in camerahoeken, verlichting en achtergrondobjecten.

 ----

__Model Upgrade:__ 

Stap over van YOLOv5 naar een modernere architectuur (zoals YOLO11). Nieuwere modellen bieden een betere balans tussen inferentiesnelheid en nauwkeurigheid, wat de rekenbelasting op de hardware verlaagt.

---

__Versioning:__ 

Implementeer datamanagement (bijv. met DVC of strikte map-structuren) om versies van datasets en getrainde modellen consistent te houden.

---

### Inverse Kinematica

Voor het project moet de klauw van de robotarm naar een gewenst punt toe kunnen bewegen. Om de segmenten van de arm in de juiste posities te krijgen is er robot-kinematica voor nodig. Deze tak van kinematica bestudeert de bewegingen en coördinatieverandering van robotische onderdelen, zonder het in acht nemen van externe kracten. Bij Inverse Kinematica is het enigste informatie het beginpunt, het eindpunt, de lengtes van de segmenten en de limieten van de gewrichten. 

Om de hoeken te bepalen van de gewrichten is er een implementatie bedacht die zijn toepassing afleidt van cirkelintersectie. De kern van de methode is dat je 'alle' mogelijke posities van het base-segment en het segment gekoppelt aan de eindeffector mee neemt in het bepalen van de vorm van de kinematische ketting. 

In het geval van de Robosub robotarm hebben we te maken met vier verschillende gewrichten. De oplossing is te vinden in het onderzoek.

---

*Voor de volledige theoretische onderbouwing en implementatie ga naar [Vision & Valve Detectie Onderzoek](Onderzoek/Vision.md).*
## Groepsproces Narwal
Naast de technische realisatie vormden de planning en de onderlinge samenwerking een essentieel onderdeel van dit project. Hoewel dit proces niet direct invloed heeft op de werking van de code, biedt dit hoofdstuk waardevolle context over de projectvoortgang en gemaakte managementkeuzes. Toekomstige projectgroepen kunnen dit gebruiken als referentiekader bij organisatorische uitdagingen of knelpunten binnen het proces.

De belangrijkste leermomenten en documenten die wij als nuttig beschouwen voor vervolggroepen zijn hieronder genoteerd:

- __Leercurve Gazebo:__ In de opstartfase bleek de leercurve van de Gazebo-simulator steiler dan vooraf ingeschat. Het correct configureren van de physics engine en de plugin-koppelingen heeft relatief veel onderzoekstijd gekost. Dit is een belangrijk referentiekader voor toekomstige teams bij het inschatten van de benodigde tijd voor simulatievraagstukken.
- __Planning en planbord bijhouden:__ Gedurende het project merkten we dat we het planbord niet altijd even strak hebben bijgehouden. Ook hebben we grotere taken in het begin te weinig opgeknipt in kleinere, behapbare stukjes. Hierdoor verloren we soms het overzicht over wie wat aan het doen was en hoe ver we écht waren. Het goed bijhouden van het bord en het klein maken van taken is achteraf gezien cruciaal voor de rust in het team.
- __Communicatie & Notulen:__ Alle afspraken, feedback en goedgekeurde keuzes vanuit RoboSub zijn netjes vastgelegd. Dit is voor een volgend team de ideale handleiding om te begrijpen waarom bepaalde ontwerpkeuzes (zoals de overstap naar toetsenbordbesturing) destijds zijn gemaakt.

_Alle sprintverslagen zijn te vinden in de [Sprintverslagen map](Groepsproces/Sprint_verslagen/)._

_De notulen van de meetings tussen RoboSub en team Narwal zijn te vinden in de [Notulen map](Groepsproces/Notulen/)._


---

## Systeemvereisten & Installatiehandleiding
Dit hoofdstuk bevat de systeemvereisten en de stappen om de simulatieomgeving en de aansturing snel op te starten.

- Docker
- Gazebo

---

## Aanbevelingen
Op basis van onze resultaten adviseren wij een volgend team om aan de slag te gaan met de volgende onderdelen. De onderdelen zijn gerangschrikt op geschatte prioriteit:


### PID - Permanente API toevoegen
De ingebouwde PID-regeling van Gazebo bewijst een stabiele basis te zijn voor nauwkeurige positionering. Om van deze testfase over te stappen naar een eindproduct, zijn de directe vervolgstappen geidentificeerd: de migratie van toetsenbord naar analoge controller input en het vervangen van `os.system` door een permanente API-koppeling om de communicatielijn open te houden.

---
### Vision - Dataset Herschrijven

 De huidige dataset is te specifiek en leunt te zwaar op de groundplane (de bodem van de simulatie), wat zorgt voor bias. Het is noodzakelijk om nieuwe data te verzamelen met meer variatie in camerahoeken, verlichting en achtergrondobjecten.

 ----

### PID - Migreren naar fysieke controller input 
Vanwege hardware beperkingen op de gebruikte laptop is er tijdelijk gekozen voor toetsenbord input. De basis in de code staat al. Dit kan functioneel worden omgeschreven naar een script dat continu de analoge assen van een fysieke controller uitleest, zodat de arm met een joystick bestuurd kan worden.

---

### Vision - Model Upgrade

Stap over van YOLOv5 naar een modernere architectuur (zoals YOLO11). Nieuwere modellen bieden een betere balans tussen inferentiesnelheid en nauwkeurigheid, wat de rekenbelasting op de hardware verlaagt.

---

### Vision - Versioning

Implementeer datamanagement (bijv. met DVC of strikte map-structuren) om versies van datasets en getrainde modellen consistent te houden.

---

### Inverse Kinematica - Algoritme

Voor het onderdeel 'Inverse Kinematica' wordt er aangeraden om te kiezen voor een al bestaand algoritme om het probleem op te lossen. Een voorbeeld hiervan is FABRIK.

--- 

### Inverse Kinematica - Controlle

Voor het onderdeel 'Inverse Kinematica' wordt er aangeraden om naar een andere testmethode te kijken om de resultaten van de inverse kinematica te testen. 

--- 

### Overig - Hydrodynamica toevoegen
 In de huidige testfase is de zwaartekracht op 0 gezet en zijn er geen onderwaterkrachten actief. Zodra de besturing vloeiend werkt, moeten de hydrodynamische eigenschappen van Gazebo worden toegevoegd. Dit is noodzakelijk om de simulatie zo dicht mogenlijk bij de realiteit te krijgen. 

 ---
 ### Gazebo - Realistische 3D-modellen toevoegen
  Om de key driver Realistisch volledig te behalen, kunnen de simpele geometrische basisvormen in de SDF configuratie worden vervangen door de daadwerkelijke 3D ontwerpen van de RoboSub arm. 

  ---

