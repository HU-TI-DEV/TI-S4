# The Everything Devcontainer

This devcontainer configuration has everything necessary to complete Semester 4 of Computer Engineering at HU — and then some.

The aim is to create a smoother development experience for the (oft-considered painfully slow) Gazebo simulation environment.

**Key features:**

- **Hardware Acceleration:** Full GPU passthrough for Gazebo rendering.
- **Gazebo Jetty:** The latest version of Gazebo with pre-configured transport libraries.
- **Build Tools:** C++ (CMake, Ninja, GDB) and Python 3.12+ environments included out of the box.
- **WSLg Optimized:** Specific fixes for Qt/X11 rendering to ensure a smooth Gazebo GUI experience on Windows.

## Table of Contents

- [Requirements](#requirements)
- [Windows Defender Exclusions](#windows-defender-exclusions)
- [Installations](#installations)
   - [Ubuntu in WSL2](#ubuntu-in-wsl2)
   - [WSL Integration with Docker](#wsl-integration-with-docker)
   - [Installing Gateway in WSL](#installing-gateway-in-wsl)
   - [Step 1: Download the Linux Archive](#step-1-download-the-linux-archive)
   - [Step 2: Extract the Archive](#step-2-extract-the-archive)
   - [Step 3: Launch Gateway](#step-3-launch-gateway)
   - [Optional: create a shortcut](#optional-create-a-shortcut)
- [Git & SSH Setup](#git--ssh-setup)
- [IMPORTANT: Project Location](#important-project-location)
- [Opening the Project](#opening-the-project)
- [Setting up Python Development](#setting-up-python-development)
- [Building and Running C++ Projects](#building-and-running-c-projects)
- [Gazebo Rendering](#gazebo-rendering)
- [Troubleshooting](#troubleshooting)
- [Test if it works](#test-if-it-works)
- [More Resources](#more-resources)

---

## Requirements

| Requirement       | Specification                                                                                                                                                             |
|-------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| GPU               | GPU with DX12 support                                                                                                                                                     |
| Drivers           | GPU Drivers with DX12 support                                                                                                                                             |
| OS                | Windows 10/11 with an Ubuntu WSL2 instance                                                                                                                                |
| Software          | Docker Desktop with WSL2 integration + JetBrains Gateway for Ubuntu (a workaround is possible on Windows by first connection to an IDE, but running inside WSL is better) |

## Windows Defender Exclusions

To prevent Windows Defender from tanking performance because of scanning (which will massively increase IO reads), we choose to exclude WSL and Docker from scanning.

To exclude WSL from this type of nonsense, Open Windows Security → Virus & threat protection → Manage settings → Add or remove exclusions, then add the following:

| Type   | Path                                                               |
|--------|--------------------------------------------------------------------|
| Folder | %USERPROFILE%\AppData\Local\Docker                                 |
| Folder | %USERPROFILE%\AppData\Local\Packages\CanonicalGroupLimited.Ubuntu* |
| Folder | \\wsl.localhost\Ubuntu                                             |
| Process | wsl.exe                                                            |
| Process | wslhost.exe                                                        |
| Process | docker.exe                                                         | 
| Process | dockerd.exe                                                        |
| Process | com.docker.backend.exe                                             |

Or if you want to use a one-shot PowerShell command, use this:
```powershell
$paths = @(
"$env:USERPROFILE\AppData\Local\Docker",
"$env:LOCALAPPDATA\Packages\CanonicalGroupLimited.Ubuntu*"
)
$processes = @("wsl", "wslhost", "docker", "dockerd", "com.docker.backend")

foreach ($p in $paths)    { Add-MpPreference -ExclusionPath $p }
foreach ($p in $processes) { Add-MpPreference -ExclusionProcess "$p.exe" }

Write-Host "Exclusions added."
```

This way, you can keep real-time protection on without having Windows sometimes destroy the connection to WSL.

## Installations

### Ubuntu in WSL2
https://documentation.ubuntu.com/wsl/latest/howto/install-ubuntu-wsl2/

### WSL Integration with Docker

https://docs.docker.com/desktop/features/wsl/

### Installing Gateway in WSL

Installing Gateway in Docker avoids you having to open the devcontainer inside of a JetBrains IDE for the first time, this is because Gateway opens devcontainer from Windows, which, as mentioned earlier, will cause the build to fail.

### **Step 1: Download the Linux Archive**
Open your WSL terminal (Ubuntu) and download the latest standalone Linux version of Gateway. JetBrains provides a handy permanent link for the latest release.

Run this command to download it to your home directory:
```bash
cd ~
wget -O gateway.tar.gz "https://data.services.jetbrains.com/products/download?code=GW&platform=linux"
```

### Step 2: Extract the Archive
Create a directory for JetBrains apps (if you don't have one) and extract the downloaded tarball into it.

```bash
mkdir -p ~/.local/share/JetBrains
tar -xzf gateway.tar.gz -C ~/.local/share/JetBrains
```

### **Step 3: Launch Gateway**
The extracted folder will have a version-specific name (like `JetBrainsGateway-2024.1`). To run it, you just need to execute the `gateway.sh` script located inside its `bin` folder.

You can find the exact folder name and launch it with this chained command:
```bash
cd ~/.local/share/JetBrains/JetBrainsGateway-*/bin
./gateway.sh
```

At this point, the JetBrains Gateway UI should open on your Windows desktop as a native Linux window (via WSLg).

### Optional: create a shortcut
So you don't have to type that path every time, you can quickly create an alias in your `.bashrc` or `.zshrc`:

1. Open your profile script:
   ```bash
   nano ~/.bashrc
   ```
2. Add this line to the bottom of the file:
   ```bash
   alias gateway="~/.local/share/JetBrains/JetBrainsGateway-*/bin/gateway.sh > /dev/null 2>&1 &"
   ```
3. Save (`Ctrl+O`, `Enter`) and exit (`Ctrl+X`).
4. Reload your configuration:
   ```bash
   source ~/.bashrc
   ```

Now, whenever you want to open Gateway, you can just type `gateway` in your WSL terminal, and it will launch.

---

## Git & SSH Setup

Since the container runs inside WSL, it needs your SSH keys to interact with GitHub.

**1. Generate keys** (if you don't have them yet). Run the following inside your WSL terminal:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```
Replace the email with your own.

**2. Add your key to the SSH agent:**

```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

**3. Copy your public key:**

```bash
cat ~/.ssh/id_ed25519.pub
```

**4. Add the key to GitHub:**
Go to **GitHub → Settings → SSH and GPG key → New SSH Key**, then paste the output from the previous command.

You should now be able to pull and push to GitHub from within WSL.

> For more information, see the [official GitHub documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account?tool=webui).


---
## IMPORTANT: Project Location

Your project **must** reside within the WSL file system (e.g., `\\wsl.localhost\Ubuntu\home\user\project`).

> **Running from a Windows mount (`/mnt/c/` or `C:\`) will cause the WSLg UI mounts to fail, and the devcontainer will not start.**

---

## Opening the Project

Now that you have git and your SSH keys are configured, you can open the project:

**Steps:**
1. Clone the project from within your WSL2 filesystem. This must be done via SSH, NOT the regular way. In our case, this will be `git clone git@github.com:your-repository`
2. Open **JetBrains Gateway** inside of WSL.
3. Go to Dev Containers, click on "New Dev Container" and navigate to the devcontainer.json inside the directory
4. Then, it will prompt you to choose an IDE Backend, for our purposes, CLion works best!

The container will:
- Install all C++ build tools (CMake, Ninja, GDB)
- Install Gazebo Jetty and transport libraries
- Set up Python 3.12 with all ML/vision dependencies from `requirements.txt`
- Mount GPU device access, install drivers (Mesa) and WSLg display passthrough

---

## Setting up Python Development

**Important:** Do NOT use the default venv that CLion suggests — your packages are already installed in the container's Python environment.

**To configure Python in CLion:**

1. Go to **Settings -> Build, execution & development and choose Python Interpreter**
2. Choose **"Add Local Interpreter → Existing Environment"**
3. Navigate to `/opt/venv/bin/python` in the container filesystem 
4. Click **OK** to confirm
5. 
This points CLion to the pre-configured virtual environment inside the container, ensuring all ML libraries (PyTorch, OpenCV, scikit-learn, etc.) are available.

**Running Python Scripts:**

You will need to manually add run configurations for Python files unfortunately. However, this is not that big of a deal.

---

## Building and Running C++ Projects

The devcontainer includes:
- **CMake** — for project configuration
- **Ninja** — for fast parallel builds
- **GDB** — for debugging

Simply open your `CMakeLists.txt` file in CLion, and it will automatically detect the build system. Click **"Load CMake Project"** when prompted.


## Gazebo Rendering

The devcontainer is optimized for Gazebo GUI rendering on WSLg:
- GPU passthrough is enabled (`--gpus=all`)
- X11/Qt rendering is properly configured
- Shared memory is increased to 4GB for smooth simulation

When you run Gazebo, the GUI will appear directly on your Windows desktop via WSLg.

Simply use the `gz sim filetorun` command to use it. 

## Troubleshooting

| Issue                                    | Solution                                                                                                                                                                  |
|------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Devcontainer won't start**             | Ensure your project is in WSL (`\\wsl.localhost\Ubuntu\...`), not in `/mnt/c/`                                                                                            |
| **Permission errors on files**           | The container user (CLion) should own all project files, if this isn't the case for whatever reason, use the linux command `sudo chown $(whoami) project/filetoown`       |
| **Git Doesn't work in the devcontainer** | Make new SSH keys, same as the regular git/github setup |


## Test if it works

To test if it works, head to the TestGazebo folder of this directory and follow the instructions there. If everything works right, it should drive a basic car in Gazebo.

## More Resources

- [Gazebo Jetty Documentation](https://gazebosim.org/docs/latest/install_ubuntu)
- [WSLg Documentation](https://learn.microsoft.com/en-us/windows/wsl/tutorials/gui-apps)
- [JetBrains Remote Development](https://www.jetbrains.com/help/clion/remote-development-overview.html)