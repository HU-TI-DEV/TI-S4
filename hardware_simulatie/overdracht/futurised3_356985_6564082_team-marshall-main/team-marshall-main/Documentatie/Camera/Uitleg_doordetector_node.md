# Technische Documentatie: DoorDetectorNode

## 1. Systeemoverzicht
De DoorDetectorNode is een ROS 2-node ontworpen voor robot Flip om deuropeningen en vrije doorgangen te detecteren via een camera. In het project van Team Marshall wordt de camera **alleen pas gebruikt wanneer Flip voor de ingang staat** waarmee hij doormiddel van de camera een extra check voert of hij daadwerkelijk voor een deur staat.

In plaats van kleursegmentatie maakt deze node gebruik van **geometrische computer vision-technieken**. Door computer vision-algoritmen te combineren met wiskundige **verticale projectie**, is de node in staat om deurstijlen op basis van pure vorm en contrast te lokaliseren. De node filtert storende objecten op de achtergrond (zoals obstakels in de volgende ruimte) zo goed mogelijk weg.

## 2. Architectuur & ROS 2 Interface

### Dataflow Diagram
/camera (Image) -> image_callback -> OpenCV Pipeline -> /door_detected (Bool)

### ROS 2 Interfaces
* **Subscriptions:**
    * `/camera` (`sensor_msgs/msg/Image`): Ontvangt de ruwe RGB-camerabeelden uit de (Gazebo) simulatieomgeving.
* **Publishers:**
    * `/door_detected` (`std_msgs/msg/Bool`): Publiceert True zodra er een geldige deuropening op een veilige remafstand is gedetecteerd, anders False.

## 3. Systeemvereisten & Opstartprocedure

Om de cameradata correct vanuit de Gazebo-simulatie naar de ROS 2-omgeving te sturen, is een actieve parameter bridge nodig. Deze wordt al automatisch geactiveerd door het bestand launch.py, maar voor in een test-omgeving-scenario kan dit ook handmatig in een terminal worden ingevoerd:

ros2 run ros_gz_bridge parameter_bridge /camera@sensor_msgs/msg/Image[gz.msgs.Image]

## 4. Het Algoritme

Raw Image -> Gray & Blur -> Sobel-X Filter -> Vertical Projection -> Width/Height Check

### Stap 1: Pre-processing (Kleuronafhankelijkheid)
Het binnenkomende beeld wordt direct omgezet naar grijswaarden (cv2.COLOR_BGR2GRAY). Hierdoor is het algoritme **volledig kleuronafhankelijk** en reageert het puur op vorm contrast. Vervolgens vlakt een Gaussische blur (cv2.GaussianBlur) hoogfrequente ruis en scherpe pixelovergangen uit voor een smoother beeld.

### Stap 2: Sobel-X Randdetectie
Er is bewust gekozen voor een **Sobel-X filter** (cv2.Sobel) in plaats van een Canny-edge filter. Sobel-X berekent de eerste afgeleide van de afbeeldingsintensiteit in de horizontale richting. 
* **Horizontale lijnen** (zoals vloerranden of plafonds) genereren geen verandering in de X-richting en worden direct geëlimineerd.
* **Verticale lijnen** (deurstijlen, muren) genereren een gigantische piek in de gradiënt en lichten fel wit op.

### Stap 3: Verticale Projectie (np.sum)
Nadat de verticale randen zijn geïsoleerd via een binaire drempelwaarde (cv2.threshold op 40), focust de code zich op het midden-horizontale gedeelte van het scherm (tussen 20% en 80% van de totale hoogte) om storende vloeren of plafonds te vermijden. Binnen deze geselecteerde Region of Interest (ROI) voert de code een verticale projectie uit, waarbij alle witte pixels per verticale kolom bij elkaar worden opgeteld:

column_counts[x] = som_van_alle_witte_pixels_in_kolom_x_binnen_ROI

* Kleine objecten of verre muren beslaan maar weinig verticale pixels en leveren lage pieken op.
* De deurstijlen op de voorgrond lopen van boven tot onder door de ROI en genereren twee **enorme, onmiskenbare pieken** in de grafiek.

### Stap 4: Geometrische Validatie & Bereik
Omdat we ervan uitgaan dat Flip recht voor de deur staat, wordt het scherm exact opgesplitst in een linker- en rechterzoekzone (beide op exact 50% van de schermbreedte). Met np.argmax worden de exacte X-coördinaten van de twee deurstijlen bepaald. Een piek wordt hierbij pas geaccepteerd als deze een minimale hoogte van 20 pixels heeft. De deuropening wordt vervolgens pas als 'veilig en geldig' beschouwd als er aan twee geometrische voorwaarden wordt voldaan:

1. **Afstandscheck:** De opening tussen de twee pieken (Delta X) moet groter zijn dan 25% van de schermbreedte, maar kleiner dan 98%. Dit zorgt ervoor dat de robot de deur al van een realistische naderingsafstand herkent en voorkomt dat muren buiten beeld verdwijnen als hij er te dicht op staat.
2. **Massa/Hoogtecheck:** De som van de twee pieken (de totale hoogte-indicator) moet groter zijn dan 50 pixels. Dit voorkomt dat de robot reageert op kleine obstakels of deuren in de verre verte.

## 5. Visualisatie & Feedback
Voor demonstratiedoeleinden genereert de node een live OpenCV-venster met real-time feedback:
* **Blauwe verticale lijnen:** De exacte X-coördinaten waar het algoritme de binnenrand van de muren heeft gelokaliseerd.
* **Groene horizontale balk:** Wordt getrokken zodra de deuropening is gevalideerd voor een helder beeld van een deurpost.

## 6. Conclusie & Ontwerpverantwoording

De geometrische aanpak van de DoorDetectorNode biedt een stabiele en betrouwbare extra check wanneer Flip voor een ingang staat. Door te kiezen voor vorm- en contrastanalyse in plaats van traditionele computer vision-methoden, lost deze implementatie twee grote praktijkproblemen op:

* **Volledige kleuronafhankelijkheid:** Omdat het algoritme direct naar grijswaarden converteert, werkt de node in elke virtuele of echte wereld. Het maakt niet uit of de muren rood, wit of blauw zijn; de node reageert puur op de geometrie van de deurstijlen.
* **Natuurlijke achtergrondfiltering:** Objecten, meubels of muren die dieper in de volgende ruimte staan, genereren door hun afstand een veel lagere verticale pixelmassa binnen de ROI. Hierdoor worden ze door de verticale projectie (`np.sum`) mathematisch weggefilterd, wat valse positieven voorkomt.

Hiermee is de node een robuust hulpmiddel dat onafhankelijk van de omgeving accuraat kan verifiëren of de robot daadwerkelijk voor een open doorgang staat.