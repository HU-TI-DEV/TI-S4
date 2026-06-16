"""
Procedurally generates a grayscale terrain heightmap with a linear slope and
random surface noise, using user-defined start height, end height, and bumpiness.

    Author: GrijzePanda
"""

from PIL import Image
import random

SIZE = 257
START = 80.0
END = 180.0
BUMPINESS = 0.5

def user_input(prompt, default):
    v = input(f"{prompt} [{default}]: ").strip()
    return float(v) if v else float(default)

print("Press Enter to accept the default value.")
start = user_input("Slope start height:", START)
end = user_input("Slope end height:", END)
bumpiness = user_input("Terrain bumpiness:", BUMPINESS)

img = Image.new("L", (SIZE, SIZE))
px = img.load()

for y in range(SIZE):
    base = start + (end - start) * y / (SIZE - 1)

    for x in range(SIZE):
        n = random.uniform(-bumpiness, bumpiness)
        px[x, y] = max(0, min(255, int(base + n)))

img.save("environment/media/terrain.png")

print("Heightmap saved to environment/media/terrain.png")
