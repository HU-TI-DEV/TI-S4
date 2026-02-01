# Programma PID control
PID control is de standaard om dingen "te regelen". De cruise control van een auto werkt bijvoorbeeld met een PID controller. Maar ook in drones zitten (geneste) PID controllers.  

## Voorbereiding
Bekijk de video's:
- [What is a PID controller?](https://www.youtube.com/shorts/AqWYZFeyAwY).  
- [Wat is PID?](https://www.youtube.com/watch?v=PJKI_-K5iGk)
- [PID - stap 2](https://www.youtube.com/watch?v=7C77m7qwhs4)
- [PID - stap 3](https://www.youtube.com/watch?v=8hbh8vUTaEk)

Run de volgende code:
```python
import matplotlib.pyplot as plt
import math
import matplotlib.patches as patches
import numpy as np
from matplotlib.animation import FuncAnimation



# Road
t=np.linspace(-2*math.pi, 2*math.pi, 500)
x = 5*np.sin(2*t)
y = -5*np.cos(t)

# Car initial state
xa, ya = -5, -5
angle = 30
step = 0.05
kp = 0.5
kp2 = 10
dt =1

fig, ax = plt.subplots(figsize=(8, 8))
ax.plot(x, y, 'k-', linewidth=2)
ax.set_xlim(-10, 10)
ax.set_ylim(-10, 10)
ax.set_aspect('equal')

car = patches.Rectangle((xa-0.5, ya-0.25), 1, 0.5,
                        angle=angle, color='blue',
                        rotation_point="center")
ax.add_patch(car)

# To store car state in animation
state = {'xa': xa, 'ya': ya, 'angle': angle}


def update(frame):
    # Update car heading based on closest road point
    #=============
    angle_speed=0 # THIS IS NOT CORRECT

    #=================

    if angle_speed>3:
        angle_speed=3
    if angle_speed<-3:
        angle_speed=-3
        
    
    state['angle'] += angle_speed*dt
    
    # Move car forward
    rad = np.deg2rad(state['angle'])
    state['xa'] += step * np.cos(rad)
    state['ya'] += step * np.sin(rad)

    # Update rectangle position and angle
    car.set_xy((state['xa']-0.5, state['ya']-0.25))
    car.angle = state['angle']

    return car,

anim = FuncAnimation(fig, update, frames=300, interval=20, blit=True)
plt.show()
```
  
## Tijdens en na de les

Het probleem... We willen het karretje gaan regelen....

## Inleveren op Canvas

4 Opdracht: [Assignment knowing your robot and sensors](./4_Assignment_knowing_your_robot_and_sensors.md)

Veel succes!
