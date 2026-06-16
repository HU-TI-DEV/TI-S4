# Cuda Activation
If you want Gazebo and the script to run smoother, we can make sure to use your GPU instead of CPU for more power and speed. This is a setup guide and tips to set this up correctly. This guide is using Windows Powershell.

# Contents
- [Cuda Activation](#cuda-activation)
- [Contents](#contents)
- [Veryfiying hardware](#veryfiying-hardware)
    - [*Check Docker Settings:*](#check-docker-settings)
- [Installing NVIDIA Drivers](#installing-nvidia-drivers)
- [Creating a new container](#creating-a-new-container)
- [Re-install venv](#re-install-venv)
- [Updating rungazebo.ps1](#updating-rungazebops1)
- [Final perfomance check](#final-perfomance-check)

# Veryfiying hardware
Run this in Powershell:
```bash
Get-CimInstance Win32_VideoController | Select-Object Name
```
- If you see **"NVIDIA GeForce...":** Your hardware is ready.
- If you only see **"Intel"** or **"Microsoft"**: You need to install the NVIDIA Drivers on your Windows host first.
Docker containers are isolated. To give your ROS2/Gazebo container "permission" to use your GPU, you need the NVIDIA Container Toolkit.

Install NVIDIA Container Toolkit: Since you are on Windows, this is usually handled by Docker Desktop.

### *Check Docker Settings:*<br>
Open Docker Desktop -> Settings -> Resources -> WSL Integration. Ensure your WSL2 distro is **enabled**.

If you really want to use lspci inside your Linux container to see hardware, you just need to install the pciutils package:
```bash
apt-get update && apt-get install -y pciutils
lspci | grep -i nvidia
```

# Installing NVIDIA Drivers
First it's important to make sure you have the latest NVIDIA drivers, follow the link to install NVIDIA desktop app where you can update drivers:<br>
- [NVIDIA Site](https://www.nvidia.com/en-us/drivers/)

Once you have the app go to Drivers tab on the left, and in the top right select `Game Ready Driver`

![alt text](/docs/images/docker_setup_cuda.png)

**Click download/install.**

# Creating a new container
In order for your GPU's to be activated for the Docker Container, we need to create a new container, unfortunately it's not possible to change from CPU to GPU in a existing container. But we can check if the container is already using GPU:
```bash
nvidia-smi
```
- If it works: You are good to go! Your script will now use the GPU.
- If it says **"NVIDIA-SMI has failed"**: You must delete and re-create the container one time with the correct flag.


Create the container with correct prompts:
```bash
# Delete the old one (save your code first!)
docker stop gazebo_container            # the name of your container
docker rm gazebo_container

docker run -it `
    --name <new-container-name> `
    --gpus all `
    --network host `
    -e DISPLAY=host.docker.internal:0 `
    -v "C:\path\to\your\code:/workspace:/workspace" `
    -w /workspace `
    [YOUR_IMAGE_NAME] bash
```

# Re-install venv
To re-install your venv correctly to run python scripts: [venv setup guide](../container-venv/README.md)

# Updating rungazebo.ps1
To restart and enter your container and make **sure** the right versions of packages installed, this is the new version of the .ps1 file:
```bash
# 1. Start the gzc container
docker start gzc

# 2. Quick environment check (Optional but recommended)
Write-Host "Entering container and installing packages..." -ForegroundColor Cyan
docker exec gzc /workspace/venv/bin/pip install --quiet numpy==1.26.4 "numpy<2.0" "opencv-python<4.11"

# 3. Enter the container
# This uses the GPU and Display settings we need
docker exec -it `
    -e DISPLAY=host.docker.internal:0 `
    -e NVIDIA_VISIBLE_DEVICES=all `
    -e NVIDIA_DRIVER_CAPABILITIES=all `
    gzc bash
```

# Final perfomance check
```bash
python -c "import torch; print('GPU Available:', torch.cuda.is_available()); print('Device Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```
- If it says `True`: You are officially ready to run your YOLO script with near-zero lag.
- If it says `False`: You just need to run `pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121` one time inside that activated venv.