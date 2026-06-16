# Gazebo Docker Commands (Integrated Graphics Systems)
# **Note:** All commands are ran in the directory root of the repo!

The following commands are verified to work on laptops or systems **without a dedicated GPU** (using integrated graphics). 



---

## 1️⃣ Allow Docker to Access Your X Server

Run this command from the **repository root** to allow GUI applications inside the container to display on your screen:

```bash id="ks92hd"
xhost +local:docker
```

---

## 2️⃣ Run Container and Mount the Entire Repository

Use this option if you want the whole repository available inside the container workspace.

```bash id="d92ksl"
docker run -it \
  --name gazebo_container \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -e QT_QPA_PLATFORM=xcb \
  -e QT_X11_NO_MITSHM=1 \
  --device /dev/dri \
  --group-add video \
  -v /tmp/.x11-unix:/tmp/.x11-unix:rw \
  -v "$(pwd)":/workspace:cached \
  s4_2026 bash
```

---

## 3️⃣ Run Container and Mount Only the `codes` Directory

Use this option if you only need the contents of the `codes` folder inside the container.

```bash id="l29s8d"
docker run -it \
  --name gazebo_container \
  --net=host \
  -e DISPLAY=$DISPLAY \
  -e QT_QPA_PLATFORM=xcb \
  -e QT_X11_NO_MITSHM=1 \
  --device /dev/dri \
  --group-add video \
  -v /tmp/.x11-unix:/tmp/.x11-unix:rw \
  -v "$(pwd)/codes":/workspace:cached \
  s4_2026 bash
```
