# RoboSub Arm Simulation

## Overzicht

Deze SDF file definieert een complete Gazebo Sim omgeving voor de RoboSub robotarm.

De simulatie bevat:

* Een gearticuleerde robotarm met 6 vrijheidsgraden
* Een tweedelige grijper (claw)
* Een camera gemonteerd op de end-effector
* Een subsea valve object als interactiedoel
* Physics-, rendering- en sensorondersteuning via Gazebo Sim plugins

De file is opgebouwd volgens de structuur:

```text
World
 ├── Physics
 ├── Lighting
 ├── Ground Plane
 ├── RoboSub Arm
 │   ├── Links
 │   ├── Joints
 │   ├── Camera
 │   └── Controllers
 └── Valve Object
```

---

# Wereldconfiguratie

## Gravity

```xml
<gravity>0 0 -9.81</gravity>
```

Standaard aardse zwaartekracht.

---

## Physics

```xml
<physics name="1ms" type="ignored">
```

| Parameter        | Waarde  |
| ---------------- | ------- |
| Max Step Size    | 0.001 s |
| Real Time Factor | 1.0     |

De simulatie draait hierdoor met een updatefrequentie van 1 ms.

---

## Gazebo Plugins

### Physics System

Verantwoordelijk voor:

* Rigid body physics
* Collision handling
* Joint simulatie

---

### User Commands System

Maakt interactie mogelijk via:

* GUI
* CLI
* Externe tools

---

### Scene Broadcaster

Synchroniseert de simulatiestatus met de Gazebo GUI.

---

### Sensors System

```xml
<plugin filename="gz-sim-sensors-system" />
```

Activeert sensorondersteuning binnen Gazebo.

Wordt momenteel gebruikt voor:

* Camera simulatie
* Image publishing
* Sensor visualisatie

---

# Omgeving

## Zonlicht

Een directional light met schaduwen simuleert zonlicht binnen de wereld.

---

## Ambient Lighting

```xml
<ambient>0.4 0.4 0.4 1</ambient>
```

Voorkomt volledig zwarte schaduwgebieden.

---

## Ground Plane

Een vlak van:

```text
100 x 100 meter
```

wordt gebruikt als vloer en collision-oppervlak.

---

# Robotmodel

## Modelnaam

```text
Robosub_arm
```

De robotarm bestaat uit meerdere gekoppelde links die samen een volledige manipulatorketen vormen.

---

# Link Structuur

```text
robosub_base
└── robosub_rotating_base
    └── upper_arm_segment
        └── lower_arm_segment
            └── palm_segment
                └── rotating_base_claw
                    ├── upper_finger_claw
                    ├── lower_finger_claw
                    └── camera_link
```

---

## robosub_base

Vaste basis van de arm.

Bevat:

* Massa- en inertiawaarden
* Collision geometry
* Visual geometry
* Joint marker voor debugging

---

## robosub_rotating_base

Draaiende basis waarop de arm gemonteerd is.

Functie:

* Rotatie rond de Z-as
* Oriëntatie van de volledige arm

Extra visual markers helpen bij het controleren van de rotatierichting.

---

## upper_arm_segment

Eerste armsegment.

Opgebouwd uit eenvoudige box geometry voor:

* Snelle rendering
* Stabiele collisions
* Gemakkelijk debuggen

---

## lower_arm_segment

Tweede armsegment.

Voorzien van inertiawaarden voor stabielere simulatie.

---

## palm_segment

Verbindingsstuk tussen arm en grijper.

Functioneert als de "pols" van de manipulator.

---

# Claw Assembly

## rotating_base_claw

Draaiende basis van de grijper.

Maakt rotatie van de volledige claw mogelijk.

---

## upper_finger_claw

Bovenste grijpersegment.

---

## lower_finger_claw

Onderste grijpersegment.

Samen vormen beide vingers een eenvoudige parallelle grijper.

---

# Camera Systeem

## camera_link

Op de end-effector is een camera gemonteerd via een fixed joint met de rotating claw base.

De camera kan gebruikt worden voor:

* Objectdetectie
* Vision testing
* Tele-operatie
* Computer vision experimenten

---

## Camera Specificaties

| Eigenschap     | Waarde    |
| -------------- | --------- |
| Resolutie      | 640 × 480 |
| Framerate      | 30 Hz     |
| Horizontal FOV | 1.5 rad   |
| Near Clip      | 0.1 m     |
| Far Clip       | 100 m     |
| Formaat        | R8G8B8    |

---

## Camera Topic

```text
/camera/image
```

Hierop worden camerabeelden gepubliceerd.

---

## Camera Visualisatie

```xml
<visualize>true</visualize>
```

Hierdoor kan de camerafeed direct binnen Gazebo bekeken worden.

---

# Joint Hiërarchie

```text
world
└── robosub_base
    └── robosub_rotating_base
        └── upper_arm_segment
            └── lower_arm_segment
                └── palm_segment
                    └── rotating_base_claw
                        ├── upper_finger_claw
                        ├── lower_finger_claw
                        └── camera_link
```

---

# Joint Configuratie

Alle beweegbare verbindingen gebruiken:

```xml
type="revolute"
```

Elke joint definieert:

* Parent link
* Child link
* Rotatie-as
* Bewegingslimieten

---

## Bewegingsassen

Binnen het model worden voornamelijk:

```text
Y-as
```

en

```text
Z-as
```

gebruikt als rotatie-assen.

---

## Bewegingslimieten

Voorbeeld:

```xml
<upper>0.785</upper>
<lower>-0.785</lower>
```

komt overeen met ongeveer:

```text
±45°
```

Deze limieten voorkomen onrealistische bewegingen.

---

# Joint Controllers

Voor iedere beweegbare joint is een afzonderlijke controller plugin aanwezig:

```xml
gz-sim-joint-controller-system
```

Hiermee kunnen joints individueel aangestuurd worden vanuit Gazebo of externe software.

---

# Valve Object

## Modelnaam

```text
Valve_mesh
```

Naast de robotarm bevat de omgeving een subsea valve model.

---

## Mesh

Het object gebruikt:

```xml
SubseaValve.stl
```

als visuele representatie.

---

## Schaal

```xml
<scale>0.005 0.005 0.005</scale>
```

De STL wordt geschaald naar een bruikbaar formaat binnen de simulatie.

---

## Positie

De valve bevindt zich ongeveer op:

```text
X = 3.0
Y = 4.0
Z = 3.0
```

ten opzichte van de wereld.

---

## Doel

De valve dient als interactiedoel voor:

* Grijpertesten
* Reachability testing
* Vision-gebaseerde detectie
* Manipulatie-experimenten
* Demonstraties

---

# Ontwerpkeuzes

## Primitive Geometry

De meeste onderdelen zijn opgebouwd uit:

* Boxes
* Cylinders
* Spheres

in plaats van complexe meshes.

Voordelen:

* Betere performance
* Simpelere collision detectie
* Snellere iteratie tijdens ontwikkeling

---

## Debug Visuals

De paarse en cyaan markers worden uitsluitend gebruikt voor debugging.

Hiermee kunnen:

* Jointposities
* Rotatieassen
* Bewegingsrichtingen

eenvoudig gecontroleerd worden.

---

## Naming Convention

Joints volgen de conventie:

```text
parent_to_child
```

Voorbeeld:

```text
upper_arm_segment_to_lower_arm_segment
```

Hierdoor blijft de volledige kinematic chain direct leesbaar.

---

# Toekomstige Uitbreidingen

Mogelijke uitbreidingen:

* ROS 2 integratie
* Uitbreiding van de Yolo dataset
* Overzet naar nieuwere Yolo versies
* Extra sensoren
* Autonomous grasping


---

# Samenvatting

Deze simulatieomgeving bevat:

* Een volledig gearticuleerde robotarm
* Een bestuurbare grijper
* Een camera op de end-effector
* Een subsea valve als interactiedoel
* Gazebo sensorondersteuning
* Individuele joint controllers
* Debugging visuals

De structuur is opgezet om eenvoudig uitbreidbaar, leesbaar en onderhoudbaar te blijven tijdens verdere ontwikkeling van het RoboSub-project.
