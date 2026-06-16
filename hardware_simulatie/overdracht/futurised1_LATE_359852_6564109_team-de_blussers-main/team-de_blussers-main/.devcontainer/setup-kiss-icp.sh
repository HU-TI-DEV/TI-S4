#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
#  KISS-ICP installeren in de devcontainer.
#
#  LET OP: er bestaat GEEN `ros-jazzy-kiss-icp` apt-pakket (KISS-ICP zit niet in
#  de Jazzy rosdistro). Daarom bouwen we het from source in een container-lokale
#  workspace (~/kiss_icp_ws) — bewust BUITEN de /workspace bind-mount, zodat de
#  build snel is op Windows/macOS en de repo schoon blijft.
#
#  Wordt aangeroepen door .devcontainer/devcontainer.json (postCreateCommand),
#  dus draait automatisch na een "Dev Containers: Rebuild Container".
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

KISS_WS="$HOME/kiss_icp_ws"

if [ -d "$KISS_WS/install/kiss_icp" ]; then
    echo "[kiss-icp] al gebouwd in $KISS_WS — overslaan."
else
    echo "[kiss-icp] geen apt-pakket beschikbaar; from source bouwen in $KISS_WS ..."
    command -v git >/dev/null || sudo apt-get update && sudo apt-get install -y git
    mkdir -p "$KISS_WS/src"
    if [ ! -d "$KISS_WS/src/kiss-icp" ]; then
        git clone --depth 1 https://github.com/PRBonn/kiss-icp.git "$KISS_WS/src/kiss-icp"
    fi
    # shellcheck disable=SC1091
    source /opt/ros/jazzy/setup.bash
    ( cd "$KISS_WS" && colcon build --packages-select kiss_icp --cmake-args -DCMAKE_BUILD_TYPE=Release )
    # Op Ubuntu-jazzy is de tf2_ros *.hpp-patch NIET nodig (zie Documentatie/SLAM_KISS_ICP.md).
fi

# Zorg dat elke terminal de kiss_icp-overlay sourcet (vóór de workspace-overlay).
LINE="source $KISS_WS/install/setup.bash"
if ! grep -qxF "$LINE" "$HOME/.bashrc" 2>/dev/null; then
    echo "$LINE" >> "$HOME/.bashrc"
    echo "[kiss-icp] overlay toegevoegd aan ~/.bashrc"
fi

echo "[kiss-icp] klaar — open een nieuwe terminal of run: $LINE"
