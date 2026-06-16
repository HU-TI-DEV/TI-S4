# Person detection met computer vision en YOLO + beeld in rviz via ros2

Er wordt gebruik gemaakt van deep learning (yolobot) om specifiek liggende personen te detecteren via een thermal camera in Gazebo. Het voorgetrainde faster R-CNN model wordt aangepast door middel van finetuning (transfer learning).

Deze workflow bestaat uit:
- Gazebo (simulatie)
- ROS2 (data transport)
- PyTorch (AI model)
- OpenCV (visualisati)

**Pretrained model:**
YOLOv8 (ultralytics)


## Onderzoek: Computer Vision, CNN's en YOLO, eigen model from scratch

### Computer Vision
Voor dit project is intelligentie belangrijk en daarvoor heb ik onderzoek gedaan naar verschillende computer vision modellen voor het detecten van mensen.

Binnen computer vision bestaan er verschillende taken:
- **Classificatie:** bepalen *wat* er op een afbeelding staat (bijv. "er staat een persoon op deze foto").
- **Object detectie:** bepalen *wat* er op de afbeelding staat én *waar* het zich bevindt, meestal aangegeven met een bounding box.
- **Segmentatie:** per pixel bepalen tot welk object het behoort.

Voor dit project is **object detectie** de meest relevante taak, omdat we niet alleen willen weten *of* er een persoon aanwezig is, maar ook *waar* die persoon zich precies bevindt in het beeld.

### Convolutional Neural Networks (CNN's)
De meeste moderne computer vision modellen zijn gebaseerd op een **Convolutional Neural Network (CNN)**. Een CNN is een speciaal type neuraal netwerk dat ontworpen is om patronen in beelden te herkennen. Het werkt met zogenoemde *convolutielagen* die kleine filters over de afbeelding schuiven om kenmerken (features) te detecteren. In de eerste lagen herkent het netwerk eenvoudige kenmerken zoals randen, lijnen en kleuren, terwijl diepere lagen steeds complexere kenmerken leren herkennen, zoals vormen, lichaamsdelen en uiteindelijk hele objecten zoals een persoon.

De kracht van een CNN zit in het feit dat het netwerk deze filters zelf leert tijdens het trainen, in plaats van dat een mens ze handmatig moet ontwerpen. Hierdoor kunnen CNN's zeer goed generaliseren en presteren ze veel beter dan klassieke beeldverwerkingstechnieken.

### Object detectie modellen
Voor object detectie bestaan er grofweg twee families van CNN-gebaseerde modellen:
- **Two-stage detectors** (zoals Faster R-CNN): deze modellen genereren eerst regio's die mogelijk een object bevatten en classificeren die regio's vervolgens. Ze zijn vaak zeer nauwkeurig, maar relatief traag.
- **One-stage detectors** (zoals YOLO en SSD): deze modellen voorspellen in één keer zowel de bounding boxes als de klassen. Ze zijn doorgaans veel sneller en daardoor geschikt voor realtime toepassingen.

### YOLO (You Only Look Once)
In dit project gebruiken wij YOLOv8 van Ultralytics. Dit is een moderne, goed onderhouden en gebruiksvriendelijke implementatie die zowel goede nauwkeurigheid als hoge snelheid biedt. Bovendien is er uitgebreide documentatie beschikbaar en is het model eenvoudig te trainen en te integreren met Python en PyTorch.

### Mijn keuze: waarom YOLO en finetunen in plaats van een model from scratch?
Voor de personen-detectie heb ik bewust gekozen voor YOLOv8 en voor finetuning in plaats van een model volledig vanaf nul te trainen op een zelf opgebouwde dataset. De belangrijkste redenen hiervoor zijn:

1. **Voorgetraind op grote datasets:** YOLOv8 is al voorgetraind op een zeer grote dataset (COCO) met miljoenen afbeeldingen en vele objectklassen, waaronder personen. Het model heeft daardoor al geleerd om algemene visuele kenmerken (randen, vormen, lichaamsdelen) te herkennen. Door te finetunen kan ik deze bestaande kennis hergebruiken en het model specifiek leren om personen in de Gazebo-omgeving te herkennen.

2. **Minder data nodig:** Een model volledig from scratch trainen vereist een enorm grote en gevarieerde dataset. Met finetuning heb ik veel minder eigen trainingsdata nodig. Dit is veel efficiënter en haalbaarder binnen de scope van dit project.

3. **Tijd en haalbaarheid:** Het zelf opbouwen en labelen van een grote dataset en het ontwerpen van een eigen CNN-architectuur is zeer arbeidsintensief. Door een bestaand, model te finetunen kan ik me richten op het oplossen van het werkelijke probleem (het detecteren van liggende personen) in plaats van op het uitvinden van het wiel.

4. **Realtime prestaties:** Omdat de detectie op een (gesimuleerde) camerastream in Gazebo moet draaien, is snelheid belangrijk. YOLO is als one-stage detector ontworpen voor realtime toepassingen en is daarom een logische keuze.

**Conclusie:** Het finetunen van een voorgetraind YOLOv8 model is de meest efficiënte, betrouwbare en haalbare aanpak voor dit project. Ik combineer de algemene kennis van een groot voorgetraind model met een kleine, specifieke dataset van personen in Gazebo, waardoor ik met relatief weinig data en rekentijd toch nauwkeurige detecties kan realiseren.


# Extra custom dataset
Na het testen van het Yolo model heb ik opgemerkt dat het herkenningszekerheid percentage erg laag meet en na testen ben ik er achter gekomen dat de models in Gazebo te blokkerig zijn. Om dit op te lossen heb ik zelf data verzameld via screenshots en daarnaast heb ik ook een bestaande dataset gebruikt van Roboflow. Om de data bruikbaar te maken voor herkenning, heb ik per afbeelding labels gemaakt.

Het opbouwen van de custom dataset bestond uit de volgende stappen:

1. **Data verzamelen:** Met screenshots van de Gazebo-simulatie heb ik afbeeldingen verzameld van personen in de parkeergarage-omgeving. Hierdoor lijkt de trainingsdata zo veel mogelijk op de beelden die het model tijdens het echte gebruik te zien krijgt. Daarnaast heb ik een bestaande dataset van Roboflow toegevoegd om meer variatie en meer afbeeldingen te krijgen.

2. **Labelen:** Elke afbeelding heb ik gelabeld door per persoon een bounding box te tekenen met de juiste klasse (`person`). Hiervoor heb ik LabelImg gebruikt, dat de labels in het YOLO-formaat opslaat (een `.txt`-bestand per afbeelding met de klasse en de genormaliseerde coördinaten van de bounding box).

3. **Dataset structuur:** De dataset is opgesplitst in een train- en validatieset. De configuratie staat in `data.yaml`, waarin de paden naar de afbeeldingen en de klassenamen zijn gedefinieerd.

4. **Trainen (finetunen):** Met deze gecombineerde dataset heb ik het voorgetrainde YOLOv8-model gefinetuned. Doordat de dataset nu specifiek de blokkerige Gazebo-personen bevat, herkent het model deze veel beter en is de herkenningszekerheid (confidence) omhoog gegaan.


# Vision in Ros2 via cv_bridge en ros_gz_bridge
Om de beelden uit Gazebo daadwerkelijk in ROS2 te kunnen verwerken met het YOLO-model, zijn er twee bruggen (bridges) nodig: de `ros_gz_bridge` en `cv_bridge`.

**ros_gz_bridge:** Gazebo en ROS2 zijn twee aparte systemen die elk hun eigen berichtformaat (message types) gebruiken. De `ros_gz_bridge` vertaalt berichten tussen Gazebo en ROS2. In dit project gebruik ik de bridge om de camera topic van Gazebo (`gz.msgs.Image`) om te zetten naar een ROS2 bericht (`sensor_msgs/msg/Image`), zodat de camerabeelden als ROS2 topic beschikbaar komen:

```bash
ros2 run ros_gz_bridge parameter_bridge \
/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image
```

**cv_bridge:** Een ROS2-`Image` bericht heeft een ander formaat dan een afbeelding die OpenCV of YOLO kan verwerken. `cv_bridge` is de schakel tussen ROS2 en OpenCV: het zet een ROS2-`Image`-bericht om naar een OpenCV-afbeelding (een NumPy-array) en weer terug. In de detectie-node werkt dat als volgt:

1. De node abonneert (subscribe) op de camera-topic `/camera/image_raw`.
2. Bij elk binnenkomend `Image`-bericht zet `cv_bridge` het bericht om naar een OpenCV-afbeelding met `imgmsg_to_cv2()`.
3. Deze afbeelding wordt aan het YOLO-model gevoerd, dat de personen detecteert en bounding boxes teruggeeft.
4. De bounding boxes worden op de afbeelding getekend, waarna de afbeelding met `cv2_to_imgmsg()` weer wordt omgezet naar een ROS2-`Image`-bericht.
5. Dit resultaat wordt op een nieuwe ROS2-topic gepubliceerd, zodat het verder gebruikt of gevisualiseerd kan worden.

Op deze manier vormt de keten **Gazebo → ros_gz_bridge → ROS2 → cv_bridge → YOLO/OpenCV → ROS2** een complete pijplijn van de gesimuleerde camera naar de uiteindelijke detectie.

# Vision in Rviz
Om de resultaten van de persoonsdetectie visueel te kunnen controleren, gebruik ik **RViz**. RViz is de standaard visualisatietool van ROS2 waarmee je onder andere camerabeelden, sensordata en topics live kunt bekijken.

De detectie-node publiceert het verwerkte beeld (met de getekende bounding boxes) op een ROS2-`Image`-topic. In RViz kan ik dit bekijken door:

1. RViz te starten.
2. Een **Image** display toe te voegen.
3. Bij de display de juiste topic te selecteren waarop de detectie-node de juiste beelden publiceert.

Op deze manier zie ik in realtime de camerabeelden uit Gazebo met daarover de detecties van het YOLO-model. Dit is erg handig om te controleren of het model de personen correct herkent en hoe hoog de confidence is, zonder dat ik een apart OpenCV-venster hoef te openen. Bovendien is RViz al onderdeel van de ROS2-omgeving, waardoor het goed samenwerkt met de andere beelden.

---

## Te installeren packages
**PyTorch AI**
- torch (CUDA versie)
- torchvision
- torchsummary
- scikit-learn

**Image processing**
- opencv-python
- pillow

**ROS2 koppeling**
- ros_gz_bridge
- rclpy
- cv_bridge


#### PyTorch installatie met CUDA
```bash
# Check de goede cuda installatie

pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

```bash
pip3 install torchsummary scikit-learn opencv-python pillow
```

**ROS2 python dependencies**
```bash
pip3 install rclpy
```

**Test of Pytorch en openCV goed zijn geïnstalleerd**
```bash
python3 -c "import torch; import cv2; print('PyTorch en OpenCV zijn klaar voor gebruik')"
```

**Test of cuda besschikbaar is en of hij op de CPU of GPU draait.**
```bash
python3 -c "import torch; print('CUDA beschikbaar:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
```

# ROS2 omgeving
om een ROS2 op te zetten heb ik in de dockerfile gemaakt die alles voor ROS2 installeerd. Om dit goed in de docker omgeving op te zetten moet je de container rebuilden en reopenen. `CTRL + shift + p` -> `>Dev Containers: Rebuild without cach and Reopen in Container`. 
>! Doe dit alleen als je geen aparte installaties hebt gedaan. Als je dat wel hebt gedaan, voer de commando's los uit in de terminal.

```dockerfile
FROM s4_2026

RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    lsb-release

# ROS2 repository
RUN apt-get update && apt-get install -y curl gnupg lsb-release

RUN curl -sSl https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
    | gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg

RUN echo "deb [signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu noble main" > /etc/apt/sources.list.d/ros2.list

# ROS2 Jazzy
RUN apt-get update && apt-get install -y \
    ros-jazzy-ros-base \
    ros-jazzy-ros-gz \
    ros-jazzy-ros-gz-bridge \
    ros-jazzy-ros-gz-sim \
    python3-colcon-common-extensions \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*


# ROS setup automatisch sourcen
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc

WORKDIR /workspace
```

Deze dockerfile installeerd de benodigde ros jazzy packages voor Ubuntu (noble).


ros2 builden:
```bash
cd ~/ros2
colcon build
```
---

## Gazebo en RViz opstarten

**TERMINAl 1**
```bash
docker start [naam_container]
docker exec -it [naam_container] bash
gz sim Gazebo/worlds/parking_garage.world &

# RUN de simulatie
```

**TERMINAL 2 | in docker container:**

```bash
cd ros2

# Zet ros2 bridge open voor ontvangen gazebo topic
ros2 run ros_gz_bridge parameter_bridge \
/camera/image_raw@sensor_msgs/msg/Image@gz.msgs.Image
```

**TERMINAL 3 |  in docker container:**
```bash
source install/setup.bash
ros2 launch person_detection detection.launch.py
```

Opnieuw builden:
```bash
colcon build --packages-select person_detection
```


## Ultralytics YOLO model
Ik heb met een eigen dataset een model getraind om personen in gazebo te herkennen.
![Yolo model](/vision/img/Detection_screenshot_retrained_model.png)



# Bronnen

PyTorch - TorchVision  Object Detection Finetuning Tutorial -->  [https://docs.pytorch.org/tutorials/intermediate/torchvision_tutorial.html](https://docs.pytorch.org/tutorials/intermediate/torchvision_tutorial.html)

Ultralytics YOLO Docs | [https://docs.ultralytics.com/tasks/detect/](https://docs.ultralytics.com/tasks/detect/)

LabelImg | [https://labelimg.org](https://labelimg.org)

Roboflow | [https://roboflow.com](https://roboflow.com)

ROS2 cv_bridge | [https://index.ros.org/p/cv_bridge/](https://index.ros.org/p/cv_bridge/)

