# Building ROS2 Workspace with Colcon

Navigate to workspace:
```bash
cd /workspace/models
```

## Install Colcon
```bash
apt install python3-colcon-common-extensions
```

## Build everything
```bash
colcon build
```

## Build single package
```bash
colcon build \
--packages-select <package-name>
```

## After building
```bash
source install/setup.bash
```