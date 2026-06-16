# 3e meeting Collin

Collin laat wat van het proces zien van de robotarm.
Sommige subs gaan onder het platform varen. Aan de onderkant zitten ook markers die gescand moeten worden. Dit is moeilijk, want hij moet niet vast komen te zitten. Eén van de opties om dit te doen is door een camera op de kop van de robotarm te zetten die de punten kan scannen. Het kan interessant zijn om hiernaar te kijken in Gazebo.

## Team Narwal
### Waar staan we?

We zijn nu bijna klaar met sprint 2. Per sprint hebben we een milestone. We zitten nu in milestone 1. 

### Over requirements:
We hebben de feedback van de requirements verwerkt. Functionele en niet-functionele requirements zijn nu bij elkaar gegroepeerd. Vindt Collin duidelijk.


__Collin:__<br>
Jullie hebben nu dingen staan als "snel genoeg zijn" en "niet te snel". Weten jullie al hoe jullie dat gaan specificeren?

__A:__ Nee, dat is een probleem voor later.

__Collin:__<br>
Wat ik gewend ben, is dat je bij de requirement zet welke eenheid je gebruikt
hoe jullie het gaan onderzoeken.

Je hebt verschillende manieren om te simuleren. je kan met fixed timestap doen, dan is je fout unknown. in dit soort programmas zitten solvers, die kijken hoe groot de fouten zijn en zet als de fouten te groot zijn de timestap kleiner. Het is interessant om te onderzoeken hoe gazebo dit doet. De simulatie tijd kan sneller gaan dan werkelijke tijd. Dit is handig om meer simulaties te kunnen doen.

__Collin:__<br>
De titels van sommige requirements kunnen duidelijker.

### Over key drivers:

We hebben key drivers opgesteld.

__Collin:__<br>
Ik zou de functionele eis tweezijdig maken:

1. Autonome systemen
2. Operations trainen

De hoeksensoren meten geen afstand. Die moet nog berekend worden.

Voor nu zien de key drivers er goed uit.

### Over Gazebo model:
We hebben ook binnen Gazebo een model gemaakt.

__Collin:__<br> 
Probeer de kleuren overal hetzelfde te houden. Het kan ook nuttig zijn on de draaipunten duidelijk weer te geven door het bijvoorbeeld een cylinder te maken. De draaipunten moeten op de goede plekken zitten, het is makkelijk om dit te testen als het visueel weergegeven wordt. 

### Sprint resultaat:

We hebben uiteindelijk 7 van de 8 doelen van de sprint bereikt.
We hebben nog geen use cases gemaakt.

Gazebo was moeilijker dan gedacht. We hebben ook al gekeken naar dingen aan elkaar vast maken. Hier zijn veel opties voor. Er komt nog een .README over het maken van vormen.

### Volgende sprint:
Volgende sprint staan er de volgende dingen op de planning:
- Verbinden van joints
- Template voor het oriëntatieonderzoek
- Branches gebruiken
- Use cases maken
- Gazebo README voor onderdelen

Ons doel is om aan het eind van iedere sprint alle vernieuwde onderdelen bij elkaar te voegen.

__Collin:__<br> 
Gaat het echt 2 weken duren om dingen aan elkaar te verbinden?

__A:__ Ja, op huidig tempo wel. Dit moeten we zelf uitzoeken en hebben we weinig les over gehad.

__Collin:__<br> 
Wordt het niet makkelijker om 2D-lijnen te gebruiken? Hoe werkt dat in Gazebo?

opties:
![Types of hinges](Images/Hinges.jpeg)

Ik zou het goed vinden als jullie volgende keer weten welke optie jullie gekozen hebben en waarom.


__Collin:__<br> 
Is het slim om taken zo op te splitsen dat iemand aan de joints werkt en iemand aan de beweging?

__A:__ We werken in groepjes aan verschillende delen. Binnen die tweetallen komt er onderscheid (beweging en joints). We kunnen niet één persoon alles laten doen want iedereen moet het begrijpen.

__Collin:__ begrijpelijk.




## Andere groep:

### Waar staan zij?
Ze hebben in gazebo een simulatie gemaakt met daarbij water physics. Die van hun hangt ondersteboven en bungeld nu. 

__Collin:__<br> hoe zijn jullie van plan om de draaiwaardes van de joints er in te zetten?

__A:__ In gazebo te hardcoden.

__Collin:__<br> Jullie gebruiken nu libraries. Die hoeven jullie niet helemaal door te rekenen maar bedenk wel een paar testjes om te testen of de library doet wat je verwacht. Daar mag een marge in zitten. 

### Over requirements: 
Ze hebben met de documentatie non functional requirements opgesteld met specificities.

__Collin:__<br> Zelfde advies als de andere groep, verdeel het onder in groepen en bedenk de hoofdfunctie.


### Over volgende sprint:

Ze zijn van plan om volgende sprint al beweging te krijgen. Eerst met een controller en daarna autonoom maken.

__Collin:__<br> Dat is het handigst om te doen met een controller met joysticks. Ik heb documentatie meegestuurd met wat alle knoppen nu doen. Dit is niet heilig maar als je het veranderd moet je dit kunnen uitleggen. 


### Over de devcontainer:

De devcontainer van school had geen GPU forwarding en is dus langzaam.

__Collin:__<br>
Dit moet je eigenlijk bij een docent aankaarten zodat het volgende keer goed geregeld is.


### Over Vision:
__Collin:__<br> In theorie zou het handig zijn om te bespreken met de mensen die nu vision doen op de camera van de robosub. Dat duurt waarschijnlijk nog wel even. Ik heb een verslag gedeeld over vision. 

### Feedback presentatie:
__Collin:__<br> Ik zie nu twee teams: een team doet het rustig en snappen het allemaal, een team heeft een iemand veel gedaan en nuttige dingen gevonden en is de rest van het team nog niet bij. Zorg dat je dit verbeterd. Dit kan je een keer als team veroorloven maar niet vaker. Iedereen moet dingen kunnen uitleggen. 

Neem volgende keer expliciet mee wat iedereen heeft gedaan.
Nu leek het alsof één persoon alles deed, terwijl er meer werk was.


