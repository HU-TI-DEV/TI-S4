# Docker setup

**IMPORTANT:** The below setup for creating a Docker container compatible with the project in this repository is based on the Docker container provided by the HU (Hogeschool-Utrecht) in semester 4, named `s4_2026`. This Docker image can be found on Canvas it sadly isn't available in this repository, because the file is too big. For installation of this image see the official semester 4 README.md, where the installation steps are provided and are necessary to run stuff like Gazebo.

--- 

#### If you ever need the name of the created container it is **gazebo_container**.

**Note:** It's handy to create your container according to the md that suits your situation best. If you have not done so you will only be able to use the shortcut after:
- either renaming your container to gazebo_container with:
    ```cmd
    docker rename yourContainerName gazebo_container 
    ```
    **or**

- replacing **gazebo_container** with the name of your container in the **commands below**. You might also not be able to use the volumes on the repo unless you mount them yourself.

---

## Ubuntu shortcut for running created container according to either [the guide for laptops with integrated grapphics](./setup/container-creation/Ubuntu/forIntegratedGraphics.md) or [the guide for laptops with dedicated graphics](./setup/container-creation/Ubuntu/forDedicatedGraphics.md)

If you want to easily start and execute the container on Ubuntu then:

1. Make a .sh file in the root of the repo with the contents:
    ```bash
    # Start container
    docker start gazebo_container

    # Set display
    xhost +local:docker

    # Execute container
    docker exec -it gazebo_container bash
    ```


2. Make your created .sh file exectuteable by navigating to the root folder and running:

    ```bash
    chmod +x yourFileName.sh
    ```

You should now be able to start and execute the gazebo container in the root folder with
```bash
./yourFileName.sh
```

---

## Windows shortcut for running created container according to either [the guide for CMD](./setup/container-creation/Windows/usingCMD.md) or [the guide for Powershell](./setup/container-creation/Windows/usingPowershell.md)

If you want to easily start and execute the container on Windows then:

1. Navigate to the root directory of the repo and make a .ps1 file with the contents:
    ```ps1
    docker start gazebo_container | Out-Null
    docker exec -it -e DISPLAY=host.docker.internal:0 gazebo_container bash
    ```

2. Navigate to the repo root and simply run 
    ```ps1
    .\nameOfYourPowershellFile.ps1
    ```

    in the terminal. 


If this fails it is because Windows blocks PowerShell scripts by default for security. To allow this right click on the Windows icon, open PowerShell as Administrator and run:
```ps1
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```


After this you should be able to run
```powershell
.\nameOfYourPowershellFile.ps1
```
