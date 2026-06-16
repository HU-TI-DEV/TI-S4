# Starting with .ps1 file
To enter the docker container easily and install the right versions of Numpy, ultralytics and torch, create a `.ps1` file with the following commands:
```bash
docker start <container-name>
docker exec <container-name> /workspace/venv/bin/pip install --quiet numpy==1.26.4 "numpy<2.0" "opencv-python<4.11"
docker exec -it -e DISPLAY=host.docker.internal:0 <container-name> bash
```
In this project all of the participants named their `.ps1` file: `rungazebo.ps1`

Run the file inside the repository:
```bash
./<file-name>.ps1
```

If you want to run the .ps1 file with a container using GPU instead if CPU, [see here](../using-cuda/ReadME.md). There are some examples in this folder saved as `.txt` file, because `.ps1` files are in the `.gitignore`.