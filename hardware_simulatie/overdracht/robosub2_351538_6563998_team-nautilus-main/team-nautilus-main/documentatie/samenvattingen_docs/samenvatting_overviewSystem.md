# Samenvatting van overview systeem

**Dit document behandelt de volgende onderwerpen:**

[Het doel van RoboSub](#het-doel-van-RoboSub)  
[Robotarm diagram](#robotarm-diagram)  
[Besturing van de robot](#besturing-van-de-robot)  
[Servo gestuurde robotarm](#servo-gestuurde-robotarm)  
[Hydraulische robotarm](#hydraulische-robotarm)  
[Kinematica en inverse kinematica](#kinematica-en-inverse-kinematica)

## Het doel van RoboSub

Het hoofddoel van dit project is deelname aan de RAMI-wedstrijd en het uitvoeren van toegepast onderzoek.

Tijdens deze wedstrijd moet een onderwaterrobot taken uitvoeren, zoals:

het bedienen van kleppen
het verzamelen van ringen

Binnen dit project ligt de focus op:

het besturen van een hydraulische robotarm om knoppen in een bepaalde volgorde en oriëntatie in te drukken

## Robotarm diagram

Er zijn diagramen met hydraulica of met servo.
In het robotarmdiagram staan de afmetingen en parameters van de arm, die eerder zijn bepaald en berekend.

## Besturing van de robot

De informatie over de Logitech-controller.

## Servo-gestuurde robotarm

De nadruk ligt op de hoekgestuurde servo-robotarm.

De besturing verloopt volgens het volgende proces:  
Eindpositie en oriëntatie, gewrichtshoeken, servo-aansturing, Inverse kinematica.

De omzetting van eindpositie naar gewrichtshoeken kan worden gedaan met:  
analytische inverse kinematica,
brute force methoden,
AI-methoden.

## Hydraulische robotarm

Dit stuk is niet relevant voor ons project. We kunnen het weglaten.

## Kinematica en inverse kinematica

In dit onderdeel worden de formules van kinematica en inverse kinematica uitgelegd
en hoe deze formules in code kunnen worden geïmplementeerd.

Daarnaast worden er bronnen gegeven over brute force en AI.

Deze kennis is later nuttig voor het uitbreiden van de kinematica
en het laten grijpen van objecten door de robotarm.
