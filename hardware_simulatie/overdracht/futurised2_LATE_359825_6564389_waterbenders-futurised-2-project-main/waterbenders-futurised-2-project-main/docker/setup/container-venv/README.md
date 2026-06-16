# Installing venv
Both [One-liners](#1-one-liners) and [Using vpip](#2-using-vpip) do the same thing. The only difference is that [Using vpip](#2-using-vpip) has a bit more details what you are doing with what command. You can choose to use `vpip` or regular `python` for running files. So choose which set of instructions you wish to run.

# Contents
- [Installing venv](#installing-venv)
- [Contents](#contents)
- [1. One-liners](#1-one-liners)
- [2. Using vpip](#2-using-vpip)
- [3. Using regular](#3-using-regular)
- [4. Extras:](#4-extras)


# 1. One-liners
- setup venv, add aliases and source 
```bash
apt update && apt install python3.12-venv -y

python3 -m venv --system-site-packages /root/venv

echo 'alias vpy="/root/venv/bin/python"' >> /root/.bashrc
echo 'alias vpip="/root/venv/bin/python -m pip"' >> /root/.bashrc

source /root/.bashrc
```

- install necessary pip packages
Since the numpy version we need is `numpy-1.26.4` we will be using `vpip install "numpy<2"`
```bash
vpip install "numpy<2"
vpip install ultralytics
vpip install matplotlib
```


# 2. Using vpip 
1. Install python3 for installing venv
```bash
apt update && apt install python3.12-venv -y
```


2. Create venv in `/root` for persistent usage
```bash
python3 -m venv --system-site-packages /root/venv
```

3. Add an alias for easy access
- open `.bashrc` for adding alias
```bash
nano /root/.bashrc
```

- add `vpy` alias to `.bashrc` for running files with virtual python
```bash
alias vpy="/root/venv/bin/python"
```

- add `vpip` alias to `.bashrc` for installing pip files with virtual pip
```bash
alias vpip="/root/venv/bin/python -m pip"
```

4. Source bash for alias usage:
```bash
source /root/.bashrc
```

5. Install packages using `vpip`
- numpy example:
```bash
vpip install "numpy<2"
```

- ultralytics example:
```bash
vpip install ultralytics
```

- matplotlib example:
```bash
vpip install matplotlib
```

5. Run files using `vpy`
```bash
vpy path/to/your/file.py
```

# 3. Using regular
1. **Enter the container**
```bash
./rungazebo.ps1
```
1. **Install venv support (once)**
```bash
apt update
apt install -y python3-venv python3-full
```
1. **Create a virtual environment**
```bash
python3 -m venv /workspace/venv --system-site-packages
```
*Why `--system-site-packages`? So your venv can still access:*
- *ROS packages like rclpy*
- *System-installed dependencies*
4. Activate the venv
```bash
source /workspace/venv/bin/activate
```

**Check if it's installed:**
```bash
which python
which pip
```
Expected:
```bash
/workspace/venv/bin/python
/workspace/venv/bin/pip
```

5. **Install Python dependencies**
```bash
pip install --upgrade pip
pip install "numpy<2"
pip install ultralytics opencv-python torch torchvision
```
1. **Source ROS**
```bash
source /opt/ros/jazzy/setup.bash
```
1. **Run your script**
```bash
python <file-name>.py
```



# 4. Extras:
1. Sourcing venv from `/root`if you did not setup alias
```bash
source /root/venv/bin/activate
```

2. Deactivating venv
```bash
deactivate
```

3. Deleting venv if you need to. Please note that you be removing it from `/root` so if you did not create it there then replace `/root` with the path where `venv` or `.venv` is.
```bash
rm -rf /root/venv
```
