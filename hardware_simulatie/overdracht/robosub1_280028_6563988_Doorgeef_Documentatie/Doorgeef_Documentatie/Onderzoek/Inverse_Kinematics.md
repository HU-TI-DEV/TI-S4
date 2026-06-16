# Theoretisch Kader & Implementatie: Inverse Kinematica voor de Robosub Robotarm 

## Begrippen:

* **Gewricht:** Draaipunt in een kinematische ketting.
* **Kinematische ketting:** Het geheel van gewrichtverbonden segmenten.
* **Eindeffector:** Het eindpunt van een kinematische ketting.
* **Degrees of Freedom (DOF):** Het aantal onafhankelijke bewegingskanten van de gehele kinematische ketting.

## Aanleiding

Dit document dient als overdracht voor de volgende ontwikkelaar die aan dit project zal gaan werken. Dit document behandelt de theoretische basis van inverse kinematica en de toepassing van inverse kinematica binnen dit project. 

Voor de RoboSub robotarm is de harde eis gesteld dat het systeem de robotarm autonoom naar een specifiek punt moet kunnen sturen. Dit onderzoek zal zich focussen op de methodes waarmee de juiste hoeken tussen de segmenten van de robotarm kunnen worden bepaald waarmee de eindeffector van de robotarm op het gewenste punt terecht komt. 

## Theoretisch Kader: Wat is kinematica?

Kinematica is een tak van de mechanica die zich bezig houdt met de beweging van objecten en het veranderen van hun positie, zonder rekening te houden met externe krachten. Afhankelijk van het vakgebied kan kinematica verschillende vormen hebben (Velocity, Contrained Systems, etc.). Dit onderzoek en de toepassingen bevinden zich in de tak van robot-kinematics ([*Robot Kinematics*](https://motion.cs.illinois.edu/RoboticSystems/Kinematics.html#Chapter_5_Robot_Kinematics_)). Deze tak van kinematica bestudeert de bewegingen en coördinatieverandering van robotische onderdelen, zonder het in acht nemen van externe kracten. Het focust op de coördinaten van de gewrichten, de lengtes van segmenten en de hoek tussen de segmenten. Binnen de algemene kinematica zijn er twee problemen/scenario's: **forward-** en **inverse-kinematica**. De scenario's verschillen van elkaar op al bekende informatie. In een scenario met de opdracht om de positie en de hoek van de eindeffector te bepalen aan de hand van de al bekende hoeken tussen segementen en de lengtes van de segmenten is er spraken van Forward kinematics. In een scenario met de opdracht om de vorm van de kinematische ketting te bepalen (hoeken tussen de segmenten) gegeven het coördinaat van de base en eindeffector en de lengtes van de segmenten, is er spraken van inverse-kinematics ([*Forward and Inverse Kinematics: Explained*](https://irisdynamics.com/articles/forward-and-inverse-kinematics)).

![kinematicchain](/Doorgeef_Documentatie/Onderzoek/Images/Inverse_Kinematics/KinematicChain.png) </br>
*Afbeelding 1*
 
Naasts een verschil in voorkennis is er ook een verschil in de oplossing. Voor een forwards-kinematisch probleem is er altijd één of geen oplossing. Voor een inverse-kinematisch probleem zijn er mogelijk meerdere oplossingen. Het aantal hangt af van een aantal factoren, waaronder de bewegingsvrijheid van de gewrichten. Om tot een oplossing te komen voor een inverse-kinematisch probleem zijn er twee soorten oplossingen: annalytisch en numeriek. Binnen deze oplossingen zijn er weer verschillende oplossingsmethodes ([*Inverse kinematics*](https://opentextbooks.clemson.edu/wangrobotics/chapter/inverse-kinematics/)).

Een analytische oplossing geeft als uitkomst een faste formule of functie, die een waarde teruggeeft afhankelijk van de input. Er is bij een analytische oplossing altijd één manier van oplossen: de formule of functie ([*Exploring Differential Equations An Interactive, Student-Centered Approach*](https://runestone.academy/ns/books/published/debookrs/glossary-main.html#gi-numerical-method)).

Bij een numerieke oplossing wordt er door middel van trial en error uiteindelijk een juiste kinematische ketting bepaald. Van start wordt de robotarm in een bepaalde stand gezet (willekeurige hoeken tussen de segmenten), vervolgens wordt de eindeffector bepaalt en door het steeds maar aan te passen van de hoeken en het uitrekenen van de eindeffector kan er worden bepaalt of de eindeffector op de doel positie zit ([*Exploring Differential Equations An Interactive, Student-Centered Approach*](https://runestone.academy/ns/books/published/debookrs/glossary-main.html#gi-numerical-method)).

Algoritme's voor Inverse Kinematica:
* [FABRIK](https://www.andreasaristidou.com/publications/papers/FABRIK.pdf)
* [Triangulation](https://scispace.com/pdf/triangualation-a-new-algorithm-for-inverse-kinematics-4gm9cpzn64.pdf)
* [cyclic coordinate descent](https://home.ttic.edu/~tewari/research/saha10finite)

## Onderbouwing van en de gemaakte keuzes

Op aandringen van de docenten is er gekozen om zelf een oplossing voor het inverse kinematische probleem te vinden en geen gebruik te maken van een al bestaand algoritme of iets dergelijks. Na grondig onderzoek is er op basis van cirkelkruising een oplossing bedacht voor het probleem ([*Robotic Systems, Section II. MODELING*](https://motion.cs.illinois.edu/RoboticSystems/InverseKinematics.html)). De kern van de methode is dat je 'alle' mogelijke posities van het base-segment en het segment gekoppelt aan de eindeffector mee neemt in het bepalen van de vorm van de kinematische ketting. Neem het voorbeeld hieronder:

![circkle](/Doorgeef_Documentatie/Onderzoek/Images/Inverse_Kinematics/circkle.png) ![arm](/Doorgeef_Documentatie/Onderzoek/Images/Inverse_Kinematics/armend.png) </br> 
*Afbeelding 2*                                                       

In de voorbeelden hierboven is de blauwe stip het coördinaat van de base, de rode stip het coördinaat van de eindeffector en zijn de groene stippen de snijpunten van de twee cirkels met elkaar. Omdat we bij dit soort problemen altijd weten wat de lengte is van het segmenten verbonden met de base en de eindeffector kan er door middel van een cirkel, om het coördinaat heen, met de radius van de segmentlengte worden bepaald welk snijpunten de afstand naar het basispunt L1 is en naar de eindeffector L2. Door vervolgens de hoek te berekenen kan er worden bepaald of de hoeken ook mogelijk zijn voor de daadwerkelijke gewrichten. Voor een kinematische ketting met twee segmenten is het vinden van de mogelijke snijpunten niet heel lastig. Als de ketting meerdere gewrichten heeft wordt het een lastiger verhaal. 

Met het uitwerken van de twee formules voor de cirkles kunnen de snijpunten worden gevonden ([*How can I find the points at which two circles intersect? [closed]*](https://math.stackexchange.com/questions/256100/how-can-i-find-the-points-at-which-two-circles-intersect)). 

$$(x−x_1)^2+(y−y_1)^2=r_1^2$$
$$(x−x_2)^2+(y−y_2)^2=r_2^2$$

Als het coördinaat van het snijpunt is gevonden kan er door middel van de functie atan2(x,y) worden bepaald welke hoek het snijpunt heeft vanaf de x-as van de base. Met deze hoek kan vervolgens worden bepaald of deze kinematische ketting mogelijk is: kan mijn gewricht ook werkelijk deze hoek bereiken? 
Om de hoek te bereken moet het punt ook in de rotatie van de origin zitten. Zo is de base voor de eindeffector het punt (x1, y1). Voor meer [informatie](https://www.youtube.com/watch?v=FvgGSgvB2I0).

![angle](/Doorgeef_Documentatie/Onderzoek/Images/Inverse_Kinematics/angle.png) </br>
*Afbeelding 3*

* θ1 = atan2(y1, x2) 
* θ2.1 = atan2((y2-y1), (x2-x1)) 
* θ2 = abs(atan2(y1 y), (x1-x))
* θ3 = θ2 + θ2.1

Voor het verplaatsen van een coördinaat naar een andere origin. Zoals (x2, y2) met als origin (x1, y1), dan trek je de waarde zo van elkaar af: 
$$ (target - origin) $$
Voor meer informatie over [atan2](https://en.wikipedia.org/wiki/Atan2).

## Implementatie van Cirkelkruising 

De oplossing voor de casus heeft veel weg van de oplossing in de vorige kop; we maken een cirkel om de eindeffector en de base joint. In dit geval nemen we de minimale en maximale draai van de base joint mee. Zie de afbeelding hieronder.

![subarm](/Doorgeef_Documentatie/Onderzoek/Images/Inverse_Kinematics/SubArm.png) ![robobase](/Doorgeef_Documentatie/Onderzoek/Images/Inverse_Kinematics/bridge.png) </br>
*Afbeelding 4*

Uit de gegevens van de Robotarm kunnen we achterhalen dat:
* θ1 > 0 en θ1 <= 102,5° 
* θ2 > 0 en θ2 >= 92° 
* θ3 <= +20° en θ3 <= -99,3°

Het idee achter de oplossing is het vinden van de juiste lengte tussen de cordinaten in de cirkel van L1 (blauw) en de cirkel van L3 (rood), waar bij de Euclidische afstand gelijk is aan L3 [*Euclidean-distance*](https://www.geeksforgeeks.org/maths/euclidean-distance/) Daarnaast gelden ook de randvoorwaarden voor de hoeken gegeven hierboven voor de juiste posities.

Om na te gaan of theta 2 (afbeelding 4) groter is dan 0 en kleiner is dan 92° kan der door middel van de cosinusregel de hoek tussen segment 1 en 2 worden bepaald. Lengte 1 en twee weten we al en door middel van de euclidische afstand kunnen we de laatse zijde van de driehoek bepalen [*The law of Cosine*](https://www.mathsisfun.com/algebra/trig-cosine-law.html).

In de specificaties van de robot arm is te zien dat de hoek van het klauwsegment moet vallen tussen +20° en -99,3°. Aan de hand van de visuele representatie is te zien dat de +20° en -99° worden 'gemeten' vanuit C met de rotatie van segment 2 in het frame van punt B. Voor het berekenen van punt P in frame C nemen we frame C met de x-as parallel aan de rotatie van het base-frame. Deze hoek wordt bepaald met de volgende berekening:
$$ atan2((P_y - C_y), (P_x - C_x)) $$

Met deze uitkomst hebben we de hoek van punt P in frame C bepaald, waarbij frame C dezelfde rotatie heeft als het base frame (punt A). Om te bepalen of de hoek die we net hebben uitgerkend nog steeds tussen +20° en -99,3° valt kunnen we met de optelling van de rotatie van frame B (theta 1 in afbeelding 5) bij de +20° en -99,3° de nieuwe min en max hoeken bepalen in het geroteerde frame C, want de hoek die we hebben berekend valt in hetzelfde geroteerde frame. Zie de afbeelding hieronder:

![roation](/Doorgeef_Documentatie/Onderzoek/Images/Inverse_Kinematics/roation.png) </br>
*Afbeelding 5* 

Links is de rotatie te zien van frame C met rotatie theta 1.  

## Implementatie in code

Voor de inverse kinematica is er in de programmeer taal Python een functie geschreven die berekend of de mogelijke eindeffector bereikbaar is. Als dit punt bereikbaar is geeft de functie de hoeken van de joints terug waarmee de eindeffector van de kinematische ketting op het gewenste eindpunt uitkomt.

Voor meer informatie van de [code](/Doorgeef_Documentatie/Code/Inverse_Kinematica/Inverse_Kinematica.py).

## Testresultaten

Om de resulaten van de inverse kinematica te testen is er een [functie](/Doorgeef_Documentatie/Code/Inverse_Kinematica/Inverse_Kinematica_Test.py) geschreven die met de coördinaten van de joints de hoeken tussen de segmenten berekend. Er zijn vijf testen gedaan om de resultaten van de Inverse kinematica met de test-functie te vergelijken. De resultaten met L1 = 2.10, L2 = 2.35 en L3 = 1.34

| Base (X,Y) | Eindeffector | Joint2 | Joint3 | Theta1 | Theta2 | Theta3 | Theta1 Test | Theta2 Test | Theta3 Test |
|------------|--------------|--------|--------|---------|---------|---------|-------------|-------------|-------------|
| (0.00, 0.00) | (2.00, -2.00) | (-1.67, -1.28) | (0.69, -1.70) | 37.40° | 48.41° | 182.54° | 37.40° | 48.41° | 182.54° |
| (0.00, 0.00) | (2.00, -0.50) | (-1.65, -1.29) | (0.69, -0.77) | 38.00° | 26.04° | 179.00° | 38.00° | 26.04° | 179.00° |
| (0.00, 0.00) | (1.00, -2.50) | (-2.07, -0.36) | (-0.07, -1.69) | 10.00° | 44.18° | 183.84° | 10.00° | 44.18° | 183.84° |
| (0.00, 0.00) | (0.50, -2.50) | (-2.08, -0.29) | (0.14, -1.21) | 8.00° | 31.12° | 231.81° | 8.00° | 31.12° | 231.81° |
| (0.00, 0.00) | (1.33, -2.22) | (-2.02, -0.57) | (0.16, -1.58) | 15.70° | 41.26° | 183.93° | 15.70° | 41.26° | 183.93° |

Aardig goede resulataten. Om de resultaten visueel te maken voor de gebruiker is er een python [script](/Doorgeef_Documentatie/Code/Inverse_Kinematica/Inverse_Kinematica_Visueel.py) geschreven dat de gegevens van de inverse kinematica plot. Voorbeelden:

![test5](/Doorgeef_Documentatie/Onderzoek/Images/Inverse_Kinematics/Test5.png) ![test4](/Doorgeef_Documentatie/Onderzoek/Images/Inverse_Kinematics/test4.png) ![test1](/Doorgeef_Documentatie/Onderzoek/Images/Inverse_Kinematics/test1.png) </br>
*Afbeelding 6* 
Groen: Base, Blauw: joint, Rood: eindeffector.

## Vervolgstappen

Voor het volgende team is het een leuke uitdaging om het probleem van inverse kinematica op te lossen door middel van een al bestaand algoritme. Veel algoritmes bewijzen dat zij sneller zijn in het uitrekenen van de kinematische oplossing en accurater. Een mooi voorbeeld van zo'n algoritme is de al eerder benoemde [FABRIK](https://www.andreasaristidou.com/publications/papers/FABRIK.pdf).

Daarnaast is het een interessante uitdaging om onderzoek te gaan doen naar een efficiënte toetsmethode om de resultaten van de inverse kinematica te controleren.

## Conclusie

Tijdens het oriëntatie onderzoek zijn er weinig specifieke eisen gesteld voor de implementatie van de inverse kinematica. Wel stond al vast dat de code zou worden geschreven in Python, maar iets over een executiesnelheid was niet behandeld bijvoorbeeld. 

Voor een zelf bedachte implementatie werkt de inverse kinematica aardig goed. Bij het testen van de resulaten kwam de implementatie aardig goed uit de test. Wat nog wel beter kan is de winskundige logica in de code. Voor een groot deel is de funtie instaat om alle restricties van de robotarm mee te nemen in berekenen van de hoeken en of de target überhaupt wel bereikbaar is met de restricties. 

## Bronnen:

* [*The Law of Cosines*](https://www.mathsisfun.com/algebra/trig-cosine-law.html)
* [*Robot Kinematics*](https://www.meegle.com/en_us/topics/robotics/robot-kinematics)
* [*Robotic SystemsSection II. MODELING*](https://motion.cs.illinois.edu/RoboticSystems/Kinematics.html#Chapter_5_Robot_Kinematics_https://irisdynamics.com/articles/forward-and-inverse-kinematics)
* [*An Introduction to Robot Kinematics*](https://www.cs.cmu.edu/~16311/current/schedule/ppp/Lec17-FK.pdf)
* [*Inverse Kinematics*](https://www.cs.cmu.edu/~16311/current/schedule/ppp/Lec17-FK.pdf)
* [*Forward Kinematics*](https://opentextbooks.clemson.edu/wangrobotics/chapter/forward-kinematics/)
* [*Exploring Differential Equations An Interactive, Student-Centered Approach*](https://runestone.academy/ns/books/published/debookrs/whats-a-numerical-soln.html)
* [*Inverse Kinematics*](https://opentextbooks.clemson.edu/wangrobotics/chapter/inverse-kinematics/)
* [*Inverse Kinematics of Open Chains*](https://modernrobotics.northwestern.edu/nu-gm-book-resource/inverse-kinematics-of-open-chains/#department)
* [*How can I find the points at which two circles intersect?*](https://math.stackexchange.com/questions/256100/how-can-i-find-the-points-at-which-two-circles-intersect?answertab=createdasc#tab-top)
* [*Circle-Circle Intersection*](https://mathworld.wolfram.com/Circle-CircleIntersection.html#eqn1)
* [*Quadratic formula*](https://en.wikipedia.org/wiki/Quadratic_formula)
* [*FABRIK*](https://www.andreasaristidou.com/publications/papers/FABRIK.pdf)
* [*Euclidean Distance*](https://www.geeksforgeeks.org/maths/euclidean-distance/)




