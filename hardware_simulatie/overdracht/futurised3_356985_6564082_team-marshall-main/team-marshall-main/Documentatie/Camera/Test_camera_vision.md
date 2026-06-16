# Test en Validatierapport: DoorDetectorNode

Dit document beschrijft het test en validatieproces van de deuropeningsdetectie. Tijdens de ontwikkelingsfase is de node blootgesteld aan verschillende scenario's binnen de 3D-simulatieomgeving om de nauwkeurigheid en randvoorwaarden te valideren.

## 1. Testmatrix & Historisch Overzicht

| Test ID | Geteste Methode | Probleem / Observatie | Resultaat | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC-01** | Canny Edge + Horizontale ROI Scan (`y_scans`) | Scankader bleef hardnekkig rood uitslaan ("OBSTAKEL IN MIDDEN") wanneer de robot recht voor de deuropening stond. | **FAIL** | Vervangen |
| **TC-02** | HoughLinesP + Versoepelde Y-Match | Lijnen van de egale, rode muren dichtbij werden amper gedetecteerd of in minuscule stukjes opgeknipt. | **FAIL** | Vervangen |
| **TC-03** | HSV Kleursegmentatie (Rood-Masker) | Perfecte en directe detectie van deurstijlen dichtbij; negeerde de achtergrond volledig. | **PASS** | Afgekeurd op criteria |
| **TC-04** | Sobel-X Gradiënt + Verticale Projectie (Marge 45%) | Succesvolle geometrische detectie, maar de groene balk sprong pas extreem laat (vlak voor de deur) op groen. | **PASS** | Doorontwikkeld |
| **TC-05** | Gecorrigeerde Sobel-X + Variabele Marge (25%) | Directe, stabiele detectie op veilige naderings- en remafstand. Geometrisch accuraat. | **PASS** | **GEACCEPTEERD** |

## 2. Gedetailleerde Analyse van Testfases & Failures

### Fase 1: Het "Achtergrond-Muur" Canny Probleem (TC-01)
* **Symptoom:** Het scankader in de ROI-code bleef continu rood uitslaan en gaf de status "OBSTAKEL / MUUR IN MIDDEN", waardoor de robot weigerde door te rijden.
* **Oorzaak:** Canny Edge Detection trekt randen op basis van contrastovergangen. De muren in de ruimte *achter* de deuropening waren eveneens donkerrood gekleurd. Wanneer de robot loodrecht voor de opening stond, keek de camera door het gat heen en detecteerde Canny de achterste muren en grijze obstakels. De horizontale controlelijnen raakten deze 'witte edge pixels' in het midden van het scherm, waardoor de code onterecht dacht dat de doorgang geblokkeerd was.

### Fase 2: Het "Geen Textuur" Hough-Probleem (TC-02)
* **Symptoom:** Na het verwijderen van de centrale scanlijnen slaagde de robot er alsnog niet in de deurstijlen stabiel te detecteren; er werden nauwelijks bruikbare lijnen getekend op de voorgrond.
* **Oorzaak:** Omdat de simulatieomgeving (Gazebo) gebruikmaakt van rode vlakken voor de muren, is er op korte afstand geen sprake van schaduw of textuur tussen de voor- en zijkant van de muur. Canny Edge vond hierdoor geen interne randen. Eventuele minimale segmenten die wel werden gevonden, vielen buiten de strikte parameters (`minLineLength` en `maxLineGap`) van de `HoughLinesP`-functie.

### Fase 3: De Kleur-Paradox (TC-03)
* **Symptoom:** Een overstap naar een HSV-kleurfilter (filteren op de specifieke rode RGB/HSV-waarde van de muren) loste het probleem direct op. De muren werden perfect geïsoleerd en de achtergrond werd onzichtbaar.
* **Resultaat:** Hoewel de test technisch slaagde, werd deze methode **afgekeurd op basis van de ontwerpcriteria**. Een harde eis van het project is dat het systeem kleuronafhankelijk moet opereren om "hardcoding" op één specifieke simulatoromgeving te voorkomen.

## 3. De Validatieoplossing: Geometrische Sobel-X Projectie (TC-04 & TC-05)

Om te voldoen aan alle ontwerpeisen (kleuronafhankelijkheid, robuustheid tegen egale vlakken en achtergrond-filtering) is de definitieve code overgestapt op een **Sobel-X gradiëntfilter** in combinatie met **verticale kolomprojectie** (`np.sum`).

### Validatiestappen:
1. **Kleuronafhankelijkheid:** De invoer wordt direct omgezet naar een grijswaardenmatrix. Veranderingen in muurkleuren hebben hierdoor geen invloed op het algoritme.
2. **Gradiënt-kracht:** Sobel-X berekent de horizontale verandering. De abrupte overgang waar de rode muur stopt en de deuropening (lucht/vloer) begint, levert een gigantische wiskundige piek op.
3. **Massa-filtering (Veraf vs. Dichtbij):** Kleine grijze blokken of muren op de achtergrond zijn verticaal gezien erg kort in het camerabeeld en leveren lage pieken op in de projectie. De deurstijlen op de voorgrond beslaan bijna de volledige hoogte van het scherm en genereren enorme pieken. Hierdoor filtert het algoritme de verre achtergrond mathematisch uit.
4. **Optimalisatie van de Remafstand (TC-05):** In eerste instantie stond de breedte-evaluatie te streng afgesteld (minimaal 45% van de schermbreedte). Hierdoor reageerde de robot pas extreem laat. Door de acceptatiegrens te verlagen naar **25% van de schermbreedte**, mits de gecombineerde piekintensiteit (massa/hoogtecheck) hoog genoeg is, springt de validatiebalk nu op een veilige en realistische naderingsafstand stabiel op groen.

## 4. Conclusie

De DoorDetectorNode werkt nu als behoort en detecteer nu door middel van een Sobel-x filter en Verticale Kolomprojectie binnenranden van de deuropening. De camera wordt alleen gebruikt als ondersteunende factor bij momenten waar de robot denkt voor de deur opening te staan. Hierdoor is de implementatie die nu is ontwikkeld genoeg voor de criteria van de opdrachtgever en de product owner.