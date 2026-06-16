"""
Real-time terrain deformation system driven by bucket contact events.

Converts world coordinates to terrain pixels, modifies a grayscale heightmap
when digging occurs, and periodically reloads the terrain in the simulation.

    Author: GrijzePanda
"""

import time
import sys
import threading

from PIL import Image

INTERFACE_DIRECTORY = "interface"
if INTERFACE_DIRECTORY not in sys.path:
    sys.path.insert(0, INTERFACE_DIRECTORY)

import interface 

PNG = "environment/media/terrain.png"
MAP_SIZE_METERS = 129
PIXELS = 257
DIG_AMOUNT = 10 # grayscale drop per dig
MIN_VAL = 20 # bedrock
RESPAWN_INTERVAL = 2.0

img = Image.open(PNG).convert("L")
pixels = img.load()

last_pixel = None
terrain_needs_update = False
last_update_time = 0.0


def world_to_pixel(x, y):
    meters_per_pixel = MAP_SIZE_METERS / (PIXELS - 1)

    px = int(round((x / meters_per_pixel) + (PIXELS - 1) / 2))
    py = int(round((-y / meters_per_pixel) + (PIXELS - 1) / 2))

    if not (0 <= px < PIXELS and 0 <= py < PIXELS):
        return None

    return px, py


def dig(px, py):
    global last_pixel, terrain_needs_update

    if last_pixel == (px, py):
        print(f"skip ({px},{py}) just dug there")
        return False

    current = pixels[px, py]
    pixels[px, py] = max(MIN_VAL, current - DIG_AMOUNT)

    last_pixel = (px, py)
    print(f"Dug tile ({px},{py})")
    terrain_needs_update = True
    
    return True


def worker():
    global terrain_needs_update, last_update_time
    
    while True:
        time.sleep(0.2)

        if not terrain_needs_update:
            continue

        now = time.time()

        if now - last_update_time < RESPAWN_INTERVAL:
            continue

        img.save(PNG)

        interface.despawn("terrain")
        interface.spawn("terrain")

        interface.despawn("support_plane")
        interface.spawn("support_plane")

        terrain_needs_update = False
        last_update_time = now


def main():
    threading.Thread(target=worker, daemon=True).start()

    # Contacts subscriber
    interface.start_subscribers()
    print("Listening for contacts...")

    while True:
        state = interface.get_state()
        bucket_touching = state["bucket_contact"]["touching"]
        bucket_x = state["bucket_contact"]["x"]
        bucket_y = state["bucket_contact"]["y"]

        if bucket_touching:
            px_py = world_to_pixel(
                bucket_x,
                bucket_y,
            )

            if px_py is not None:

                px, py = px_py

                print(f"Contact at ({bucket_x:.2f}, {bucket_y:.2f})")

                dig(px, py)
        time.sleep(0.2)


if __name__ == "__main__":
    main()
