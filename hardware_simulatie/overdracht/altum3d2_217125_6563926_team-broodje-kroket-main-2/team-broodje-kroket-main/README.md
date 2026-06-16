# Project Atum3D


## Over dit project:
In deze repo Staat ons project voor Atum3D. De opdracht was om een robot arm te maken die prints uit een printer kan halen, in een curing station kan doen, daarna in een alchohol bad stopt en uiteindelijk naar één plek toe brengt. Dit is gedaan door een combinatie van een vision model dat alle objecten herkent en de movement is gedaan door middel van Inverse kinematics en PID voor stability control.
 
## benodigdheren
### windows:
- Docker Desktop
- MobaXterm

### Linux:
heeft geen extra benodigdheden

## Hoe instaleer je het:
Open een terminal in deze map (`team-broodje-kroket/DockerContainer`) en run:
 
```bash
docker compose up -d
```

Ga daarna de container in:

```bash
docker compose exec team-project bash
```
Stoppen:

```bash
docker compose down
```


## Hoe gebruik je het:
Open een terminal 
```
docker ps -a
```
Vindt het ID voor de dockercontainer en plaats die in het volgende commando:

```
docker exec -it -e DISPLAY=host.docker.internal:0 <container ID> bash
```
Hieronder kun je een uitleg vinden over hoe je de volgende items draait.  

[Movement](gazebo/movement/readme.md)  
[vision](gazebo/Vision/README.md)


## Contributers:

Anton Steeghs(Movement(Inverse Kinematics)/Model/movement)

Laurens Richter(Vision)

Twan Roodenburg(Movement(PID)/Models/(export))  

Vigo de Koning(Vision)  


## Contact:
| Anton | anton.steeghs@student.hu.nl   
| Laurens | laurens.richter@student.hu.nl  
| Twan | twan.roodenburg@student.hu.nl  
| Vigo | vigo.dekoning@student.hu.nl  

