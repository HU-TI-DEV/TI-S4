# **Note:** All commands are ran in the directory root of the repo and they are specific for **Powershell**! 

This guide explains how to create and run a Gazebo Docker container using the **s4_2026** image, with local project files mounted as volumes so they are accessible inside the container.

## 1️⃣ Start your X server

Before launching the container, start an X server (for example **VcXsrv**) so GUI applications can display properly.

## 2️⃣ Run the container

Open PowerShell in the root directory of the repository and run:

```ps1
docker run -it `
  --name gazebo_container `
  -e DISPLAY=host.docker.internal:0 `
  -v ${PWD}\codes:/workspace `
  s4_2026 bash
```
