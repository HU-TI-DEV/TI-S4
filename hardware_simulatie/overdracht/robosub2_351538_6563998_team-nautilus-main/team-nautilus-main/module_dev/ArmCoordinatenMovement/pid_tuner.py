"""
PID Tuner voor RoboSub arm
--------------------------
Gebruik:
    python3 pid_tuner.py
"""

import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation

import threading
import time
import math
import subprocess
import json
import os
import sys
from collections import deque
from datetime import datetime

# ── Configuratie ─────────────────────────────────────────────────────────────

JOINT_STATE_TOPIC = "/world/robosubSimulationV4/model/robosub/joint_state"
LOG_WINDOW_SEC    = 60000.0
UPDATE_RATE_HZ    = 20
MAX_POINTS        = int(LOG_WINDOW_SEC * 50)
POSITION_TOL_DEG = 0.05 #tolerance staat op 0.05 graden

JOINTS = [
    ("subToBase",          "subToBase",          -45.0,    45.0,   3.0,   0.015,  0.038),
    ("baseToUpperarm",     "baseToUpperarm",    -104.89,    0.0,   3.2,   0.018,  0.24),
    ("upperarmToForearm",  "upperarmToForearm",  -94.50,    0.0,   1.0,   0.015, 0.08),
    ("forearmToWrist",     "forearmToWrist",    -20.0,   100.40,   0.9,   0.01,  0.06),
    ("wristToHand",        "wristToHand",         0.0,   270.0,    4.0,   0.02,  0.05),
    ("handToFirstfinger",  "handToFirstfinger",   0.0,    45.0,    0.4,   0.002, 0.02),
    ("handToSecondfinger", "handToSecondfinger", -45.0,    0.0,    2.5,  0.0125,  0.038),
]

# ── Joint state ───────────────────────────────────────────────────────────────

class JointState:
    def __init__(self, name, gz_name, lower, upper, kP, kI, kD):
        self.name        = name
        self.gz_name     = gz_name
        self.lower_deg   = lower
        self.upper_deg   = upper
        self.kP          = kP
        self.kI          = kI
        self.kD          = kD
        self.current_deg = 0.0
        self.target_deg  = 0.0
        self.lock        = threading.Lock()

        self.times     = deque(maxlen=MAX_POINTS)
        self.positions = deque(maxlen=MAX_POINTS)
        self.targets   = deque(maxlen=MAX_POINTS)
        self.errors    = deque(maxlen=MAX_POINTS)

        self.move_start_time = None
        self.move_start_pos  = None
        self.settle_time     = None
        self.overshoot_deg   = 0.0
        self.moving          = False

    def update_position(self, pos_rad, t):
        pos_deg = math.degrees(pos_rad)
        with self.lock:
            prev_deg         = self.current_deg
            self.current_deg = pos_deg
            self.times.append(t)
            self.positions.append(pos_deg)
            self.targets.append(self.target_deg)
            self.errors.append(self.target_deg - pos_deg)

            # Detecteer wanneer joint begint te bewegen
            if self.moving and self.move_start_time is None:
                if abs(pos_deg - prev_deg) > 0.005:  # beweegt meer dan 0.005 graden
                    self.move_start_time = t
                    print(f"[{self.name}] beweging gedetecteerd op t={t:.2f}s")

            # Overshoot bijhouden
            if self.moving and self.move_start_pos is not None:
                direction = 1.0 if self.target_deg > self.move_start_pos else -1.0
                overshoot = (pos_deg - self.target_deg) * direction
                if overshoot > self.overshoot_deg:
                    self.overshoot_deg = overshoot

            # Settle detectie — alleen nadat beweging gedetecteerd is
            if self.moving and self.move_start_time is not None and self.settle_time is None:
                if abs(self.target_deg - pos_deg) < POSITION_TOL_DEG:
                    self.settle_time = t - self.move_start_time
                    self.moving      = False
                    print(f"[{self.name}] gesettled na {self.settle_time:.2f}s")

    def set_target(self, target_deg):
        with self.lock:
            self.target_deg      = target_deg
            self.move_start_time = None   # ← None, wordt gezet zodra beweging start
            self.move_start_pos  = self.current_deg
            self.settle_time     = None
            self.overshoot_deg   = 0.0
            self.moving          = True

joint_states = [JointState(*j) for j in JOINTS]
start_time   = time.time()

# ── Gazebo listener ───────────────────────────────────────────────────────────

def parse_gz_output(lines):
    import re
    text = "\n".join(lines)

    results = {}

    joint_blocks = re.split(r'(?=joint \{)', text)
    for block in joint_blocks:
        if "joint {" not in block:
            continue

        name_match = re.search(r'name:\s*"([^"]+)"', block)
        if not name_match:
            continue
        name = name_match.group(1)

        # Vind axis1 { ... } inclusief geneste accolades
        axis1_start = block.find("axis1 {")
        if axis1_start == -1:
            continue

        depth       = 0
        axis1_block = ""
        for ch in block[axis1_start:]:
            axis1_block += ch
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    break

        pos_match = re.search(r'position:\s*([-\d.eE+]+)', axis1_block)
        if not pos_match:
            continue

        try:
            position = float(pos_match.group(1))
            results[name] = position
        except ValueError:
            pass

    return results

def gazebo_listener():
    cmd = ["gz", "topic", "-e", "-t", JOINT_STATE_TOPIC]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    except FileNotFoundError:
        print("[ERROR] 'gz' niet gevonden in PATH")
        os._exit(1)

    buffer = []
    depth  = 0

    while True:
        line = proc.stdout.readline()
        if not line:
            break

        stripped = line.strip()

        # Nieuw top-level bericht begint met "header {" of een lege regel gevolgd door content
        # Detecteer start van nieuw bericht: depth is 0 en we zien een openingsregel
        if depth == 0 and stripped.endswith("{") and not stripped.startswith("#"):
            buffer = [stripped]
            depth  = 1
            continue

        if depth > 0:
            buffer.append(stripped)
            depth += stripped.count("{")
            depth -= stripped.count("}")

            if depth == 0:
                # Volledig bericht ontvangen
                parsed = parse_gz_output(buffer)
                if parsed:
                    t = time.time() - start_time
                    for js in joint_states:
                        if js.gz_name in parsed:
                            js.update_position(parsed[js.gz_name], t)
                buffer = []

# ── Terminal input (aparte thread) ────────────────────────────────────────────

def print_help(js):
    print(f"\n{'─'*52}")
    print(f"  Joint    : {js.name}")
    print(f"  Gains    : kP={js.kP}  kI={js.kI}  kD={js.kD}")
    print(f"  Limieten : {js.lower_deg}° → {js.upper_deg}°")
    print(f"{'─'*52}")
    print("  p <waarde>   → kP instellen       (bijv: p 6.0)")
    print("  i <waarde>   → kI instellen       (bijv: i 0.01)")
    print("  d <waarde>   → kD instellen       (bijv: d 0.3)")
    print("  t <graden>   → target voor grafiek (bijv: t -50)")
    print("  save         → gains opslaan in JSON")
    print("  reset        → terug naar originele waarden")
    print("  help         → dit menu")
    print("  q            → stoppen")
    print(f"{'─'*52}\n")

def save_gains():
    gains = {js.name: {"kP": js.kP, "kI": js.kI, "kD": js.kD} for js in joint_states}
    fname = f"gains_{datetime.now().strftime('%H%M%S')}.json"
    with open(fname, "w") as f:
        json.dump(gains, f, indent=2)
    print(f"  [✓] Opgeslagen in {fname}")

def terminal_input(js, original_gains):
    print_help(js)
    while True:
        try:
            raw = input(">> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nStoppen...")
            os._exit(0)

        if not raw:
            continue
        parts = raw.split()
        cmd   = parts[0].lower()

        if cmd == "q":
            print("Stoppen...")
            os._exit(0)

        elif cmd in ("p", "i", "d") and len(parts) == 2:
            try:
                val = float(parts[1])
                if cmd == "p":
                    js.kP = val
                elif cmd == "i":
                    js.kI = val
                else:
                    js.kD = val
                print(f"  k{cmd.upper()} = {val}")
            except ValueError:
                print("  Ongeldige waarde")

        elif cmd == "t" and len(parts) == 2:
            try:
                deg = float(parts[1])
                if deg < js.lower_deg or deg > js.upper_deg:
                    print(f"  [!] Buiten limiet [{js.lower_deg}° → {js.upper_deg}°]")
                else:
                    js.set_target(deg)
                    print(f"  Target ingesteld op {deg}° — stuur ook via C++ menu")
            except ValueError:
                print("  Ongeldige waarde")

        elif cmd == "save":
            save_gains()

        elif cmd == "reset":
            js.kP, js.kI, js.kD = original_gains
            print(f"  Reset → kP={js.kP}  kI={js.kI}  kD={js.kD}")

        elif cmd == "help":
            print_help(js)

        else:
            print("  Onbekend commando. Typ 'help'.")

# ── Matplotlib in hoofdthread ─────────────────────────────────────────────────

def run_plot(js):
    fig = plt.figure(figsize=(13, 8))
    fig.canvas.manager.set_window_title(f"PID Tuner — {js.name}")
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.35)

    ax_pos   = fig.add_subplot(gs[0, :])
    ax_error = fig.add_subplot(gs[1, 0])
    ax_gains = fig.add_subplot(gs[1, 1])
    ax_info  = fig.add_subplot(gs[2, :])
    ax_gains.axis("off")
    ax_info.axis("off")

    def draw(frame):
        with js.lock:
            times     = list(js.times)
            positions = list(js.positions)
            targets   = list(js.targets)
            errors    = list(js.errors)
            kP        = js.kP
            kI        = js.kI
            kD        = js.kD
            settle    = js.settle_time
            overshoot = js.overshoot_deg
            current   = js.current_deg
            target    = js.target_deg

        ax_pos.cla()
        if times:
            ax_pos.plot(times, positions, color="#2196F3", lw=1.8, label="Echte positie (Gazebo)")
            ax_pos.plot(times, targets,   color="#F44336", lw=1.2, ls="--", label="Target")
            ax_pos.axhline(target + POSITION_TOL_DEG, color="#4CAF50", lw=0.8, ls=":", alpha=0.7)
            ax_pos.axhline(target - POSITION_TOL_DEG, color="#4CAF50", lw=0.8, ls=":", alpha=0.7,
                           label=f"±{POSITION_TOL_DEG:.3f}° tolerantie")

        ax_pos.set_ylim(js.lower_deg -5, js.upper_deg + 5)
        ax_pos.set_title(f"{js.name}  —  huidig: {current:.2f}°  |  target: {target:.2f}°", fontsize=11)
        ax_pos.set_xlabel("Tijd (s)")
        ax_pos.set_ylabel("Hoek (graden)")
        handles, labels = ax_pos.get_legend_handles_labels()
        if handles:
            ax_pos.legend(fontsize=8, loc="upper left")
        ax_pos.grid(True, alpha=0.3)

        ax_error.cla()
        if errors:
            ax_error.plot(times, errors, color="#FF9800", lw=1.5)
            ax_error.axhline(0, color="gray", lw=0.8, ls="--")
            ax_error.fill_between(times, errors, 0, alpha=0.15, color="#FF9800")
        ax_error.set_title("Error over tijd", fontsize=10)
        ax_error.set_xlabel("Tijd (s)")
        ax_error.set_ylabel("Error (graden)")
        ax_error.grid(True, alpha=0.3)

        ax_gains.cla()
        ax_gains.axis("off")
        tabel = ax_gains.table(
            cellText=[["kP", f"{kP:.4f}"], ["kI", f"{kI:.5f}"], ["kD", f"{kD:.4f}"]],
            colLabels=["Gain", "Waarde"],
            loc="center", cellLoc="center"
        )
        tabel.auto_set_font_size(False)
        tabel.set_fontsize(11)
        tabel.scale(1.2, 1.8)
        ax_gains.set_title("Huidige gains", fontsize=10, pad=12)

        ax_info.cla()
        ax_info.axis("off")
        settle_str = f"{settle:.2f} s" if settle is not None else "nog niet gesettled"
        ax_info.text(0.5, 0.70,
                     f"Settle tijd: {settle_str}     Overshoot: {overshoot:.3f}°     "
                     f"Limieten: [{js.lower_deg}° → {js.upper_deg}°]",
                     ha="center", va="center", fontsize=10,
                     transform=ax_info.transAxes,
                     bbox=dict(boxstyle="round,pad=0.4", facecolor="#E3F2FD", alpha=0.8))
        ax_info.text(0.5, 0.25,
                     "Terminal:  p <waarde>   i <waarde>   d <waarde>   t <graden>   save   reset   q",
                     ha="center", va="center", fontsize=9, color="#555555",
                     transform=ax_info.transAxes, fontfamily="monospace")

    # ani moet bewaard blijven anders wordt hij garbage collected
    ani = FuncAnimation(fig, draw, interval=1000 // UPDATE_RATE_HZ, cache_frame_data=False)
    plt.show()

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n=== RoboSub PID Tuner ===\n")
    for i, js in enumerate(joint_states):
        print(f"  {i}: {js.name}  (kP={js.kP}, kI={js.kI}, kD={js.kD})")

    while True:
        try:
            choice = int(input("\nWelke joint wil je tunen? [0-6]: "))
            if 0 <= choice < len(joint_states):
                break
            print("  Ongeldige keuze.")
        except ValueError:
            print("  Voer een getal in.")

    js             = joint_states[choice]
    original_gains = (js.kP, js.kI, js.kD)

    print(f"\n[✓] Joint: {js.name}")
    print(f"[✓] Topic: {JOINT_STATE_TOPIC}\n")

    # Gazebo listener als daemon thread
    threading.Thread(target=gazebo_listener, daemon=True).start()

    # Terminal input als daemon thread
    threading.Thread(target=terminal_input, args=(js, original_gains), daemon=True).start()

    # Grafiek in hoofdthread — vereist door Qt5
    run_plot(js)

if __name__ == "__main__":
    main()