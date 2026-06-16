# Installatie- & Configuratiedocumentatie: ROS 2 Jazzy & Gazebo Harmonic

Dit document beschrijft de stappen die nodig zijn om de simulatie-omgeving voor de robot **Flip** te draaien binnen de Ubuntu 24.04 (Noble) Docker-container.

> **Snelle start:** In de standaard Docker-image zijn alle benodigde pakketten uit Sectie 1 al vooraf geïnstalleerd. Is het `gz sim` commando niet direct beschikbaar? Sla Sectie 1 over en voer direct de stappen uit **Sectie 2 (Omgevingsvariabelen)** uit.

## 1. Systeempakketten (Alleen bij schone installatie)
Mocht je vanaf een volledig lege container beginnen of container die niet helemaal voldoet aan de eisen? Check/installeer dan eerst de simulator en de bijbehorende ROS 2- en navigatiepakketten:

```bash
apt-get update && apt-get install -y \
  gz-harmonic \
  ros-jazzy-ros-gz \
  ros-jazzy-ros-gz-sim \
  ros-jazzy-slam-toolbox \
  ros-jazzy-rviz2
```

## 2. Essentiële Omgevingsvariabelen & Sourcing
Voordat de commando's en plugins correct werken, moeten de juiste paden actief zijn. Voer de volgende regels uit in je terminal (of voeg ze toe aan je `.bashrc` / opstartscript):

```bash
# 1. Activeer de ROS 2-omgeving en de gekoppelde Gazebo-bridges
source /opt/ros/jazzy/setup.bash

# 2. Geef aan waar Gazebo de robotmodellen van Flip kan vinden
export GZ_SIM_RESOURCE_PATH=/workspace/Futurised/models
```