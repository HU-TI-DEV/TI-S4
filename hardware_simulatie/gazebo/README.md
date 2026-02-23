# Programma Gazebo deel I
Gazebo is een modelling/simulation framework. Dit gebruiken wij in dit Semester om de robots te modelleren/simuleren in een virtuele omgeving. 

## Voorbereiding
Bekijk de video [Waarom we aan de slag gaan met Gazebo](https://www.youtube.com/watch?v=cgZElRSVHXY).  

## Tijdens en na de les


1 [Installing Gazebo](./1_Installing_gazebo.md)

2 [Building our first robot](./2_Building_our_first_robot.md)

3 [Connect with C++](./3_Connect_with_c.md)

## Inleveren op Canvas

4 Opdracht: [Assignment knowing your robot and sensors](./4_Assignment_knowing_your_robot_and_sensors.md)

Veel succes!

# Programma Gazebo deel II

## Voorbereiding
Zorg dat je Gazebo deel I af hebt. 

## Tijdens en na de les

5 [Using_thrusters_and_camera](./5_Using_thrusters_and_camera.md)

6 [Driving the robot](./6_Driving_the_robot.md)

## Inleveren op Canvas

7 Opdracht: [Assignment let's start building the robot for our project!](./7_Assignment_start_with_the_real_one.md)

# Programma Gazebo deel III
PID control is de standaard om dingen "te regelen". De cruise control van een auto werkt bijvoorbeeld met een PID controller. Maar ook in drones zitten (geneste) PID controllers.  

## Voorbereiding
Bekijk de video's:
- [What is a PID controller?](https://www.youtube.com/shorts/AqWYZFeyAwY).  
- [Wat is PID?](https://www.youtube.com/watch?v=PJKI_-K5iGk)
- [PID - stap 2](https://www.youtube.com/watch?v=7C77m7qwhs4)
- [PID - stap 3](https://www.youtube.com/watch?v=8hbh8vUTaEk)

Run de volgende code in je favoriete python editor, niet in je container:
```python
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ==========================================================
# ----------------- SYSTEM PARAMETERS ----------------------
# ==========================================================

m = 5.0          # inertia
d = 2.0          # damping
u_max = 10.0     # actuator saturation (max steering power)

dt = 0.02        # simulation timestep

# ==========================================================
# ------------------- INITIAL STATE ------------------------
# ==========================================================

h = 0.0          # level (0–10)
v = 0.0          # velocity
setpoint = 5.0   # desired level

# ==========================================================
# ------------------- CONTROLLER AREA ----------------------
# ==========================================================

Kp = 8.0         # proportional gain

def p_controller(setpoint, h):
    """
    Simple P-controller.
    Rreplace this
    with your own PID controller.
    """
    error = setpoint - h
    u = Kp * error 
    preverror=error
    return u


# ==========================================================
# ---------------------- SIMULATION ------------------------
# ==========================================================

fig, (ax_level, ax_plot) = plt.subplots(1, 2, figsize=(10, 6))

# ----- Tank Visualization -----
ax_level.set_xlim(0, 1)
ax_level.set_ylim(0, 10)
ax_level.set_title("Level System (Click to change setpoint)")
ax_level.set_xticks([])

water_rect = plt.Rectangle((0.2, 0), 0.6, h, color="blue")
ax_level.add_patch(water_rect)

sp_line = ax_level.axhline(setpoint, color='red', linestyle='--')

# ----- Response Plot -----
ax_plot.set_xlim(0, 10)
ax_plot.set_ylim(0, 10)
ax_plot.set_title("Level Response")
ax_plot.set_xlabel("Time [s]")
ax_plot.set_ylabel("Level")

time_data = []
level_data = []
sp_data = []

line_level, = ax_plot.plot([], [], label="Level")
line_sp, = ax_plot.plot([], [], '--', label="Setpoint")
ax_plot.legend()

t = 0.0


# ==========================================================
# ------------------ MOUSE INTERACTION ---------------------
# ==========================================================

def onclick(event):
    global setpoint
    if event.inaxes == ax_level and event.ydata is not None:
        # Limit setpoint between 0 and 10
        setpoint = np.clip(event.ydata, 0, 10)

fig.canvas.mpl_connect('button_press_event', onclick)


# ==========================================================
# ------------------- ANIMATION LOOP -----------------------
# ==========================================================

def update(frame):
    global h, v, t

    # ----- Controller -----
    u = p_controller(setpoint, h)

    # ----- Actuator saturation -----
    u = np.clip(u, -u_max, u_max)

    # ----- System dynamics (Euler integration) -----
    a = (u - d*v) / m
    v += a * dt
    h += v * dt

    # Limit level between 0 and 10
    if h < 0:
        h = 0
        v = 0
    elif h > 10:
        h = 10
        v = 0

    t += dt

    # ----- Update tank -----
    water_rect.set_height(h)
    sp_line.set_ydata([setpoint, setpoint])  # must be sequence!

    # ----- Update plot data -----
    time_data.append(t)
    level_data.append(h)
    sp_data.append(setpoint)

    # Scroll plot after 10 seconds
    if t > 10:
        ax_plot.set_xlim(t - 10, t)

    line_level.set_data(time_data, level_data)
    line_sp.set_data(time_data, sp_data)

    return water_rect, sp_line, line_level, line_sp


ani = FuncAnimation(fig, update, interval=dt*1000)

plt.tight_layout()
plt.show()
```
mmmhhh... dit werkt best slecht toch????

Run de volgende code in je favoriete python editor, niet in je container:
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

Opdracht: [8_Assignment_PID_control](./8_Assignment_PID_control.md)

Veel succes!
