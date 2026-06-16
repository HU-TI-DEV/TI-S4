# Gazebo naar YOLOv5 Live Weergave

Deze repository vangt een live camerabeeld direct vanuit een draaiende Gazebo-simulatie op en voert real-time objectdetectie uit met behulp van een legacy YOLOv5-model.

**Belangrijk: deze setup omzeilt ROS volledig** door direct gebruik te maken van Gazebo's native `gz-transport` (ZeroMQ) netwerklaag. **Hier hebben we voor gekozen omdat wij in tijdsnood zaten. Voor verdere ontwikkeling van het project is het aangeraden om een ROS implementatie te maken.**

## NumPy 2.0
Moderne Python-omgevingen hebben momenteel last van een enorm compatibiliteitsprobleem door de release van NumPy 2.x. Dit breekt oudere C-extensies.

Om te voorkomen dat OpenCV en PyTorch crashen, **moet** deze omgeving worden vastgezet op het NumPy 1.x ecosysteem. De onderstaande installatie-instructies regelen dit automatisch.

---

## Installatiegids

### 1. Vereisten
* **Python 3.12** (Aanbevolen)
* **Gazebo** (Moet `gz.msgs10` en `gz.transport13` ondersteunen — bijv. Gazebo Harmonic)
* Een getraind YOLOv5 PyTorch-gewichtenbestand (bijv. `best.pt`)

### 2. De Virtuele Omgeving Opzetten
Isoleer deze pakketten altijd in een virtuele omgeving om te voorkomen dat je de standaard Python-installatie van je systeem verstoort.
```bash
python3 -m venv venv
source venv/bin/activate  # Op Windows gebruik je: venv\Scripts\activate
```

### 3. Kern AI-Pakketten Installeren
Installeer eerst PyTorch. (Let op: Pas dit commando aan als je specifieke CUDA GPU-acceleratie nodig hebt via de officiële PyTorch website).

```Bash
pip install torch torchvision
```

### 4. Het Stabiele Ecosysteem Vastzetten (De Fix)
Voer dit exacte commando uit om de resterende pakketten te installeren. Dit zet NumPy en OpenCV vast op stabiele, onderling compatibele versies (numpy<2 en opencv-python<4.11), en installeert yolov5 om aan de eisen van PyTorch te voldoen.

```Bash
pip install "numpy<2" "opencv-python<4.11" yolov5
```

(Optioneel) Als je een rode pip waarschuwing ziet over het pakket sahi (Slicing Aided Hyper Inference), kun je deze negeren óf oplossen door sahi te downgraden naar een versie die compatibel is met onze OpenCV-versie:

```Bash
pip install "sahi<0.12"
```

### 5. De Simulatie Draaien
#### Stap 1: Start Gazebo<br>
Lanceer je Gazebo-wereld met daarin je robot en camera. <br>
Cruciaal: Zorg ervoor dat je op de Play (▶) knop drukt linksonder in de Gazebo UI. De camera zendt geen bytes uit als de fysica-engine op pauze staat!

#### Stap 2: Controleer je Camera Topic
Open een nieuwe terminal (met de virtuele omgeving actief) en controleer op welk topic je camera exact uitzendt:

```Bash
gz topic -l
```

Als jouw topic anders is dan het standaard /camera/image, pas dan de variabele topic_name aan in de main() functie van het Python-script.

#### Stap 3: Voer het Script uit
Het script zoekt standaard naar de modelgewichten op ../../runs/train/exp3/weights/best.pt. Als jouw gewichten ergens anders staan, kun je het pad eenvoudig doorgeven via een omgevingsvariabele (YOLO_WEIGHTS_PATH):

Bash
#### Optie A: Gebruik het standaard pad binnen de mappenstructuur:
python3 image_test_2.py

#### Optie B: Geef handmatig een specifiek pad mee:
YOLO_WEIGHTS_PATH=/pad/naar/jouw/best.pt python3 image_test_2.py
UI Besturing
Het script opent twee vensters via OpenCV:

Gazebo Camera Live Feed (De schone, rauwe beelden uit de simulatie).

Direct Gazebo -> Legacy YOLOv5 (De beelden inclusief getekende bounding boxes en labels).

Klik op een van de OpenCV-vensters en druk op q of ESC om de videostreams en het script veilig af te sluiten.

### DEBUG: Probleemoplossing
"Successfully subscribed! Waiting for images..." maar er verschijnen geen vensters? Staat de simulatie op pauze? Druk op de play knop.

De topic-naam in het Python-script komt niet exact overeen met wat Gazebo uitzendt. Controleer de naam via gz topic -l en pas deze aan in het script.