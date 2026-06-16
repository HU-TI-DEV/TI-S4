import subprocess

process = subprocess.Popen(
    ["gz", "topic", "-e", "-t", "/air_pressure"],
    stdout=subprocess.PIPE,
    text=True
)

print("Listening to air pressure sensor...\n")

for line in process.stdout:

    print(line.strip())

    if "pressure" in line:

        try:
            value = float(line.split(":")[1])

            print(f"Current pressure: {value}")

            if value > 102000:
                print("WARNING: Possible explosion detected!")

        except:
            pass