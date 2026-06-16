FROM ubuntu:24.04
LABEL authors="luucw"

ENV DEBIAN_FRONTEND=noninteractive

# Install the basic necessary tools and libraries for C++, Python and Gazebo. Especially rendering is important here
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-client \
    build-essential \
    cmake \
    ninja-build \
    gdb \
    python3 \
    python3-dev \
    python3-venv \
    python3-pip \
    curl \
    gnupg2 \
    lsb-release \
    sudo \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Install required graphics tools to get Gazebo to work using GL and Vulkan
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglvnd0 \
    libgl1 \
    libglx0 \
    libegl1  \
    libgles2 \
    mesa-utils \
    vulkan-tools \
    libvulkan1 \
    mesa-vulkan-drivers \
    && rm -rf /var/lib/apt/lists/*

# I'm using Gazebo Jetty, the latest version of Gazebo.
# I followed these instructions to install Gazebo Jetty: https://gazebosim.org/docs/latest/install_ubuntu

RUN curl -sSL https://packages.osrfoundation.org/gazebo.gpg -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" > /etc/apt/sources.list.d/gazebo-stable.list \
    && apt-get update \
    && apt-get install -y gz-jetty \
    && apt-get install -y python3-gz-transport15 \
    && rm -rf /var/lib/apt/lists/*

ARG USERNAME=CLion
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create a non-root user to avoid permission issues when running the container. This user will have sudo privileges without a password, which is useful for development purposes.
# Important to mention! The user Ubuntu is removed, this is because the nvidia/cuda base image has a default user named Ubuntu with UID 1000, which can cause conflicts with the ownership of files and directories (found this out the hard way... we love CMake!).
RUN userdel -f -r ubuntu || true \
    && groupadd --force --gid $USER_GID $USERNAME \
    && useradd -o --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME


# Set up Python venv
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv --system-site-packages /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV VIRTUAL_ENV=/opt/venv
RUN pip install --no-cache-dir -r /tmp/requirements.txt
RUN chown -R $USERNAME:$USERNAME /opt/venv

# Set up WSL runtime dir

RUN mkdir -p /mnt/wslg/runtime-dir \
    && chown -R ${USERNAME}:${USERNAME} /mnt/wslg/runtime-dir \
    && chmod 0700 /mnt/wslg/runtime-dir

ENV GZ_PARTITION=test
USER $USERNAME