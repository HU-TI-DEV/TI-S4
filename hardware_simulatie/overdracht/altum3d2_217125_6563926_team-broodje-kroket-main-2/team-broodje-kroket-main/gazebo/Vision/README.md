# Vision

Het doel van vision in dit project is om de verschillende stations te herkennen. Deze herkenning wordt uiteindelijk gebruikt als backup voor de arm, zodat gecontroleerd kan worden of de beweging goed gaat en of de arm echt voor het juiste station staat. Dit gebeurt door verschillende filters toe te passen op het camerabeeld.

## Doel van deze map

In deze map staat alles wat nodig is om het vision-gedeelte van het project te testen en verder uit te werken. De focus ligt op:

- het ophalen van camerabeelden in Gazebo.
- het herkennen van stations of objecten in beeld.


## Structuur van de map

De map bestaat op dit moment uit de volgende onderdelen:

- `Camera/` bevat de code voor het uitlezen en tonen van de camera;
- `Model_Vision/` bevat het model en de wereldbestanden die in Gazebo gebruikt worden;
- `README.md` is de huidige projectbeschrijving;

## How to use

Open een terminal in de container en ga naar de map `Vision/Model_Vision`.  

Voer daarna het volgende commando uit:

```
gz sim model.sdf
```
Dit opent de wereld voor de camera in Gazebo.


Open vervolgens een nieuwe terminal in de container en ga naar de map `Vision/Camera`.

Voer daarna het volgende commando uit:

```
python3 camera.py
```
Dit opent de camera en laat het camerabeeld zien.

## Research (keuzeonderbouwing)
In dit project is er gekozen voor de volgende filters:
CvtColor, GaussianBlur, Canny Edge Detection, morphologyEx en HoughLinesP.

### CvtColor (grayscale)
Dit filter wordt gebruikt om het camerabeeld om te zetten naar grayscale. Dit wordt gedaan zodat het beeld eenvoudiger te verwerken is. Kleurinformatie is voor deze stap niet nodig, omdat de detectie vooral kijkt naar vormen, randen en contrasten. Door eerst naar grijswaarden om te zetten, wordt de volgende beeldverwerking overzichtelijker en stabieler.

### GaussianBlur
GaussianBlur wordt gebruikt om kleine ruis in het beeld te verminderen. Dit filter maakt het beeld iets zachter, waardoor kleine storingen en losse pixels minder invloed hebben op de detectie. Daardoor worden de randen van grote objecten beter herkend en ontstaan er minder foutieve detecties in de volgende stappen.

### Canny Edge Detection
Canny Edge Detection wordt gebruikt om duidelijke randen in het beeld te vinden. Dit is belangrijk omdat de contouren van stations en openingen vooral zichtbaar worden via hun buitenlijnen. Door deze randen te detecteren, kan het systeem beter bepalen waar vormen beginnen en eindigen.

### morphologyEx
De functie morphologyEx wordt in deze code gebruikt met een closing-operatie. Deze stap helpt om kleine gaten en onderbrekingen in de gevonden randen op te vullen. Hierdoor worden contouren vollediger, wat belangrijk is om objecten later beter als een geheel te kunnen herkennen.

### HoughLinesP
HoughLinesP wordt gebruikt om rechte lijnen in het beeld te detecteren. In dit project helpt dat vooral bij het vinden van de opening van een station. Door te kijken naar lijnen met bepaalde hoeken en naar plekken waar veel van deze lijnen samenkomen, kan het systeem een waarschijnlijke opening herkennen.

### Keuzes

In dit project is de beslissing gemaakt om over te stappen van het herkennen van specifieke stations per box naar het detecteren van de opening en buitenkant van de stations zelf. Voorheen werd er een box per station getekend met een eigen naam. Dit bleek niet erg betrouwbaar te zijn door verschillende omstandigheden, zoals schaduwen die veranderen, vormen die sterk op elkaar lijken en detecties terwijl het object niet volledig in beeld is. Hierdoor is gekozen om over te stappen naar het detecteren van de buitenkant en opening van de stations. Dit bleek een betere implementatie te zijn, omdat deze aanpak veel minder wordt beïnvloed door de bovengenoemde problemen.

## Implementatie

De implementatie in `camera.py` volgt deze volgorde:

1. Het camerabeeld wordt eerst omgezet naar grayscale met `CvtColor`.
2. Daarna wordt `GaussianBlur` toegepast om ruis te verminderen.
3. Met `Canny Edge Detection` worden de randen in beeld bepaald.
4. Vervolgens wordt met `morphologyEx` de randinformatie verbeterd.
5. Ten slotte worden met contourdetectie en `HoughLinesP` stations en stationopeningen herkend.

## Aanbevelingen

- Onderzoek of een andere combinatie van filters de herkenning van objecten kan verbeteren.
- Bekijk de mogelijkheid om een AI-model te trainen voor objectherkenning, voor een betrouwbaardere detectie.
- Maak een koppeling met het InverseKinematics-model door de camera op de robotarm te plaatsen.