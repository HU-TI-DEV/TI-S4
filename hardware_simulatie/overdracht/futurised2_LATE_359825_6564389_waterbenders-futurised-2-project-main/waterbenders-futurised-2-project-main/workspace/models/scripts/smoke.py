#!/usr/bin/env python3

import time
import random
import subprocess
import threading

WORLD = "room"

particle_id = 0

# SMOKE SOURCE
SMOKE_X = -16
SMOKE_Y = 16
SMOKE_Z = 0.5

LIFETIME = 3.0

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

    subprocess.run(cmd, capture_output=True, text=True)


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

    name = f"smoke_{particle_id}"

    x = SMOKE_X + random.uniform(-0.12, 0.12)
    y = SMOKE_Y + random.uniform(-0.12, 0.12)
    z = SMOKE_Z + random.uniform(0.0, 1.2)

    radius = random.uniform(0.04, 0.10)
    shade = random.uniform(0.25, 0.55)
    alpha = random.uniform(0.25, 0.5)

    sdf = f"""
<?xml version="1.0" ?>
<sdf version="1.10">

<model name="{name}">

  <static>true</static>

  <pose>{x} {y} {z} 0 0 0</pose>

  <link name="link">

    <visual name="visual">

      <geometry>
        <sphere>
          <radius>{radius}</radius>
        </sphere>
      </geometry>

      <material>
        <ambient>{shade} {shade} {shade} {alpha}</ambient>
        <diffuse>{shade} {shade} {shade} {alpha}</diffuse>
        <emissive>0 0 0 0</emissive>
      </material>

      <transparency>{1-alpha}</transparency>

    </visual>

  </link>

</model>

</sdf>
"""

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

    if "data: true" in result.stdout:
        particles[name] = time.time()


threading.Thread(
    target=cleanup_loop,
    daemon=True
).start()

while True:

    spawn_particle()

    time.sleep(0.1)