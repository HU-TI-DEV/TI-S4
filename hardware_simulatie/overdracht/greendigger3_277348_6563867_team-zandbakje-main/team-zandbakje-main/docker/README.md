### Setting up docker in VScode.
Date : 24-03-2026</br>

---

To ensure everyone is using the same docker image, follow these steps to set it up correctly in the VScode env.

#### Setup
- First check to make sure the file tree is the following:
```
docker/
  |->image/
  |   |->s4_2026.tar
  |->compose.yaml
  |->devcontainer.json
  |->Dockerfile
```

- Then open the terminal above the docker file.  
`C:\Users\..\..\team-zandbakje>`  
It should look something like this.

- run : `docker compose -f docker/compose.yaml up -d`  
  This starts the container. If you're unsure run : `docker compose -f docker/compose.yaml ps`.  

! Always run it with the yaml file, since it automatically starts the mobaxterm display.

- run : `docker compose -f docker/compose.yaml exec -w /workspace gazebo-dev bash`  
  to enter the container via the terminal.

- Get to work. :)