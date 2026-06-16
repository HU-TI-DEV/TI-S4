# **Note:** All commands are ran in the directory root of the repo and they are specific for **cmd**! 

## Mount the Entire Repository into the Container Workspace

Use this option if you want all repository files to be accessible inside the container.

```cmd
docker run -it ^
  --name gazebo_container ^
  -e DISPLAY=host.docker.internal:0 ^
  -v %cd%:/workspace ^
  s4_2026 bash
```

---

## Mount Only the `codes` Directory into the Container Workspace

Use this option if you only need the contents of the `codes` folder inside the container.

```cmd
docker run -it ^
  --name gazebo_container ^
  -e DISPLAY=host.docker.internal:0 ^
  -v %cd%\workspace:/workspace ^
  s4_2026 bash
```
