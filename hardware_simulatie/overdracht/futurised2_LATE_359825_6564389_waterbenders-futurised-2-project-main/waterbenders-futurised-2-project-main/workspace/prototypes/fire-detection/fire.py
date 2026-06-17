#!/usr/bin/env python3

import time
import random
import subprocess
import threading

WORLD = "room"

particle_id = 0

# FIRE POSITION
FIRE_X = -16
FIRE_Y = 16
FIRE_Z = 0.5

LIFETIME = 1

particles = {}


def remove_particle(name):

    cmd = [
        "gz",
        "service",
        "-s",
        f"/world/{WORLD}/remove",
        "--reqtype",
        "gz.msgs.Entity",
        "--reptype",
        "gz.msgs.Boolean",
        "--timeout",
        "1000",
        "--req",
        f"name: '{name}'"
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if "data: true" in result.stdout:
        print("removed", name)
    else:
        print("remove failed", name)


def cleanup_loop():
    while True:
        now = time.time()
        expired = []
        for name, spawn_time in list(particles.items()):
            if now - spawn_time > LIFETIME:
                expired.append(name)
        for name in expired:
            remove_particle(name)
            if name in particles:
                del particles[name]
        time.sleep(0.1)

def spawn_particle():
    global particle_id
    particle_id += 1
    name = f"thermal_fire_{particle_id}"
    x = FIRE_X + random.uniform(-0.03, 0.03)
    y = FIRE_Y + random.uniform(-0.03, 0.03)
    z = FIRE_Z + random.uniform(0.0, 0.12)
    radius = random.uniform(0.015, 0.025)
    
    sdf = f"""
<?xml version="1.0" ?>
<sdf version="1.10">
<model name="{name}">
  <static>false</static>
  <pose>{x} {y} {z} 0 0 0</pose>
  <link name="link">
    <inertial>
      <mass>0.001</mass>
      <inertia>
        <ixx>0.0001</ixx>
        <iyy>0.0001</iyy>
        <izz>0.0001</izz>
      </inertia>
    </inertial>
    <visual name="visual">
      <geometry>
        <sphere>
          <radius>{radius}</radius>
        </sphere>
      </geometry>
      <material>
        <ambient>1 0.5 0 1</ambient>
        <diffuse>1 0.3 0 1</diffuse>
        <emissive>1 0.6 0.1 1</emissive>
      </material>
    </visual>
  </link>
</model>
</sdf>
"""

    # TEMP FILE
    filename = f"/tmp/{name}.sdf"
    with open(filename, "w") as f:
        f.write(sdf)
    cmd = [
        "gz",
        "service",
        "-s",
        f"/world/{WORLD}/create",
        "--reqtype",
        "gz.msgs.EntityFactory",
        "--reptype",
        "gz.msgs.Boolean",
        "--timeout",
        "1000",
        "--req",
        f'sdf_filename: "{filename}"'
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    print(result.stdout)
    print(result.stderr)

    if "data: true" in result.stdout:
        particles[name] = time.time()
        print("spawned", name)
    else:
        print("FAILED TO SPAWN", name)

threading.Thread(
    target=cleanup_loop,
    daemon=True
).start()

while True:
    spawn_particle()
    time.sleep(0.5)