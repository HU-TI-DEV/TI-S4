import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Slider, Button
from matplotlib.lines import Line2D

#  Joint Definitions 
JOINT_DEFS = [
    # {Name, UpperLimit(Deg), LowerLimit(Deg), InitialPos(Deg)}
    {"name": "subToBase",          "lo": -45.00,  "hi":  45.00,  "init": 0.0},  
    {"name": "baseToUpperarm",     "lo": -104.89, "hi":   0.00,  "init": 0.0},  
    {"name": "upperarmToForearm",  "lo":  -94.50, "hi":   0.00,  "init": 0.0},  
    {"name": "forearmToWrist",     "lo":  -20.00, "hi": 100.40,  "init": 0.0},  
    {"name": "wristToHand",        "lo":    0.00, "hi": 270.00,  "init": 0.0}, 
]

# Converts upper and lower limits to radians
def jlo(i): return np.radians(JOINT_DEFS[i]["lo"])
def jhi(i): return np.radians(JOINT_DEFS[i]["hi"])
 
#  Arm Geometry
UPPER_ARM = np.array([-0.208, 0.0, -0.0292])
FOREARM   = np.array([ 0.235, 0.0,  0.0   ])
WRIST     = np.array([ 0.1601,0.0,  0.0   ])

BASE_Z_OFFSET = 0.1
 
L1 = np.linalg.norm(UPPER_ARM)
L2 = np.linalg.norm(FOREARM)
L3 = np.linalg.norm(WRIST)
TOTAL_LENGTH = L1 + L2 + L3
 
# Helper to normalize angles between [-PI, PI]
def normalize_angle(a: float) -> float:
    while a >  np.pi: a -= 2 * np.pi
    while a < -np.pi: a += 2 * np.pi
    return a
 
 
def clamp_angle(a: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, a))
 
 
#  FABRIK IK Solver  (returns diagnostics too)
def solve_ik(target_r: float, target_z: float):
    """
    Returns:
        pts        – 4 × [r, z] chain positions
        angles     – 7 joint angles (rad), clamped to joint limits
        iters      – FABRIK iterations used
        elapsed_us – wall-clock solve time in microseconds
        clamped    – list of joint indices where clamping occurred
    """
    t_start = time.perf_counter()
 
    base_r, base_z = 0.0, BASE_Z_OFFSET
    lengths = [L1, L2, L3]
 
    pts = [
        [base_r, base_z],
        [base_r + UPPER_ARM[0], base_z + UPPER_ARM[2]],
        [base_r + UPPER_ARM[0] + FOREARM[0],  base_z + UPPER_ARM[2] + FOREARM[2]],
        [base_r + UPPER_ARM[0] + FOREARM[0] + WRIST[0],
         base_z + UPPER_ARM[2] + FOREARM[2]  + WRIST[2]],
    ]
 
    root = list(pts[0])
    target_dist = np.hypot(target_r - base_r, target_z - base_z)
 
    EPSILON  = 0.001
    MAX_ITER = 100
    iters    = 0
 
    if target_dist > TOTAL_LENGTH:
        for i in range(3):
            dr = target_r - pts[i][0]
            dz = target_z - pts[i][1]
            d  = np.hypot(dr, dz)
            pts[i+1][0] = pts[i][0] + (dr / d) * lengths[i]
            pts[i+1][1] = pts[i][1] + (dz / d) * lengths[i]
        iters = 1
    else:
        error = np.hypot(pts[3][0] - target_r, pts[3][1] - target_z)
        while error > EPSILON and iters < MAX_ITER:
            pts[3] = [target_r, target_z]
            for i in range(2, -1, -1):
                dr = pts[i][0] - pts[i+1][0]
                dz = pts[i][1] - pts[i+1][1]
                d  = np.hypot(dr, dz)
                pts[i][0] = pts[i+1][0] + (dr / d) * lengths[i]
                pts[i][1] = pts[i+1][1] + (dz / d) * lengths[i]
 
            pts[0] = list(root)
            for i in range(3):
                dr = pts[i+1][0] - pts[i][0]
                dz = pts[i+1][1] - pts[i][1]
                d  = np.hypot(dr, dz)
                pts[i+1][0] = pts[i][0] + (dr / d) * lengths[i]
                pts[i+1][1] = pts[i][1] + (dz / d) * lengths[i]
 
            error = np.hypot(pts[3][0] - target_r, pts[3][1] - target_z)
            iters += 1
 
    elapsed_us = (time.perf_counter() - t_start) * 1e6
 
    # Raw angles 
    angles  = [0.0] * 7
    clamped = []
 
    # j0 yaw: not solved in 2-D, stays 0
    raw0 = 0.0
    cl0  = clamp_angle(raw0, jlo(0), jhi(0))
    if abs(cl0 - raw0) > 1e-9: clamped.append(0)
    angles[0] = cl0
 
    # j1 baseToUpperarm
    seg1r = pts[1][0] - pts[0][0]
    seg1z = pts[1][1] - pts[0][1]
    theta0_1 = np.arctan2(-UPPER_ARM[2], UPPER_ARM[0])
    raw1 = normalize_angle(np.arctan2(-seg1z, seg1r) - theta0_1)
    cl1  = clamp_angle(raw1, jlo(1), jhi(1))
    if abs(cl1 - raw1) > 1e-9: clamped.append(1)
    angles[1] = cl1
 
    # j2 upperarmToForearm
    seg2r        = pts[2][0] - pts[1][0]
    seg2z        = pts[2][1] - pts[1][1]
    world_angle2 = np.arctan2(-seg2z, seg2r)
    raw2 = normalize_angle(angles[1] - world_angle2)
    cl2  = clamp_angle(raw2, jlo(2), jhi(2))
    if abs(cl2 - raw2) > 1e-9: clamped.append(2)
    angles[2] = cl2
 
    # j3 forearmToWrist
    seg3r        = pts[3][0] - pts[2][0]
    seg3z        = pts[3][1] - pts[2][1]
    world_angle3 = np.arctan2(-seg3z, seg3r)
    raw3 = normalize_angle(world_angle3 - world_angle2)
    cl3  = clamp_angle(raw3, jlo(3), jhi(3))
    if abs(cl3 - raw3) > 1e-9: clamped.append(3)
    angles[3] = cl3
 
    # j4 wristToHand (fixed at 0, clamped to [0, 270°])
    raw4 = 0.0
    cl4  = clamp_angle(raw4, jlo(4), jhi(4))
    angles[4] = cl4

    return pts, angles, iters, elapsed_us, clamped
 
 
# ─────────────────────────────────────────────
#  Figure Layout
# ─────────────────────────────────────────────
REACH = TOTAL_LENGTH * 1.15
COLORS = {
    "bg":        "#0f1117",
    "panel":     "#1a1d27",
    "panel2":    "#12151f",
    "upper":     "#4fc3f7",
    "forearm":   "#81d4fa",
    "wrist":     "#b3e5fc",
    "joint":     "#ffffff",
    "target":    "#ff6b6b",
    "reach":     "#2a2f40",
    "grid":      "#1e2235",
    "text":      "#cdd6f4",
    "accent":    "#f38ba8",
    "ok":        "#a6e3a1",
    "warn":      "#f9e2af",
    "slider_bg": "#313244",
    "clamp":     "#fab387",
}
 
fig = plt.figure(figsize=(13, 8.5), facecolor=COLORS["bg"])
fig.canvas.manager.set_window_title("5-DOF Arm IK Simulator")
 
# ── Axes ─────────────────────────────────────────────────────────────────
ax      = fig.add_axes([0.06, 0.20, 0.52, 0.74], facecolor=COLORS["bg"])
ax_info = fig.add_axes([0.61, 0.44, 0.37, 0.50], facecolor=COLORS["panel"])
ax_diag = fig.add_axes([0.61, 0.20, 0.37, 0.21], facecolor=COLORS["panel2"])
 
ax_sr   = fig.add_axes([0.06, 0.11, 0.52, 0.035], facecolor=COLORS["slider_bg"])
ax_sz   = fig.add_axes([0.06, 0.05, 0.52, 0.035], facecolor=COLORS["slider_bg"])
ax_btn  = fig.add_axes([0.61, 0.05, 0.10, 0.07],  facecolor=COLORS["panel"])
 
slider_r = Slider(ax_sr, 'r  (reach)',  -REACH, REACH, valinit=0.35, color=COLORS["upper"])
slider_z = Slider(ax_sz, 'z  (height)', -REACH, REACH, valinit=0.20, color=COLORS["forearm"])
btn_reset = Button(ax_btn, 'Reset', color=COLORS["panel"], hovercolor=COLORS["slider_bg"])
 
for sl in (slider_r, slider_z):
    sl.label.set_color(COLORS["text"])
    sl.valtext.set_color(COLORS["text"])
 
# ── Arm Graphics ──────────────────────────────────────────────────────────
reach_fill = plt.Circle((0, BASE_Z_OFFSET), TOTAL_LENGTH,
                         color=COLORS["reach"], fill=True, zorder=0, alpha=0.45)
reach_ring = plt.Circle((0, BASE_Z_OFFSET), TOTAL_LENGTH,
                         color=COLORS["upper"], fill=False, lw=1,
                         linestyle='--', zorder=1, alpha=0.3)
ax.add_patch(reach_fill)
ax.add_patch(reach_ring)
 
seg_upper,   = ax.plot([], [], lw=7, color=COLORS["upper"],   solid_capstyle='round', zorder=3)
seg_forearm, = ax.plot([], [], lw=5, color=COLORS["forearm"], solid_capstyle='round', zorder=3)
seg_wrist,   = ax.plot([], [], lw=3, color=COLORS["wrist"],   solid_capstyle='round', zorder=3)
joint_dots,  = ax.plot([], [], 'o', ms=8,  color=COLORS["joint"],  zorder=5)
end_dot,     = ax.plot([], [], 'o', ms=11, color=COLORS["wrist"],  zorder=6,
                        markeredgecolor='white', markeredgewidth=1.5)
target_dot,  = ax.plot([], [], '*', ms=16, color=COLORS["target"],
                        zorder=7, markeredgecolor='white', markeredgewidth=0.8)
cross_h,     = ax.plot([], [], '-', color=COLORS["target"], lw=1, alpha=0.5, zorder=2)
cross_v,     = ax.plot([], [], '-', color=COLORS["target"], lw=1, alpha=0.5, zorder=2)
 
# ── Axes Styling ──────────────────────────────────────────────────────────
ax.set_xlim(-REACH, REACH)
ax.set_ylim(-REACH * 0.55, REACH * 1.1)
ax.set_aspect('equal')
ax.set_xlabel("r  (horizontal reach, m)", color=COLORS["text"], fontsize=9)
ax.set_ylabel("z  (height, m)",           color=COLORS["text"], fontsize=9)
ax.set_title("5-DOF Arm — 2D IK Plane", color=COLORS["text"], fontsize=11,
             fontweight='bold', pad=10)
ax.tick_params(colors=COLORS["text"], labelsize=8)
for sp in ax.spines.values(): sp.set_edgecolor(COLORS["grid"])
ax.grid(True, color=COLORS["grid"], lw=0.6, linestyle='--', alpha=0.7)
ax.axhline(0, color=COLORS["grid"], lw=0.8)
ax.axvline(0, color=COLORS["grid"], lw=0.8)
 
ground = mpatches.FancyBboxPatch((-0.04, BASE_Z_OFFSET - 0.05), 0.08, 0.04,
                                   boxstyle="round,pad=0.005",
                                   facecolor=COLORS["slider_bg"],
                                   edgecolor=COLORS["upper"], lw=1.5, zorder=4)
ax.add_patch(ground)
ax.text(0, BASE_Z_OFFSET - 0.065, "base", ha='center', color=COLORS["text"],
        fontsize=7, fontfamily='monospace', zorder=5)
 
# ── Info Panel (joint angles) ─────────────────────────────────────────────
ax_info.set_xlim(0, 1); ax_info.set_ylim(0, 1); ax_info.axis('off')
ax_info.text(0.5, 0.97, "Joint Angles", ha='center', va='top',
             color=COLORS["text"], fontsize=10, fontweight='bold', fontfamily='monospace')
 
SHORT = ["subToBase    ", "baseToUpperarm", "uparm→forearm ", "forearm→wrist ",
         "wrist→hand   "]
angle_texts = []
limit_bars  = []  # colored horizontal fill bars for each joint
for i in range(5):
    y = 0.88 - i * 0.116
    # limit range label (grey, small)
    ax_info.text(0.02, y,
                 f"{JOINT_DEFS[i]['lo']:+.0f}° … {JOINT_DEFS[i]['hi']:+.0f}°",
                 va='top', color="#555577", fontsize=6.5, fontfamily='monospace')
    t = ax_info.text(0.02, y - 0.038, f"  {SHORT[i]}: ---",
                     va='top', color=COLORS["text"], fontsize=8, fontfamily='monospace')
    angle_texts.append(t)
 
# ── Diagnostics Panel ─────────────────────────────────────────────────────
ax_diag.set_xlim(0, 1); ax_diag.set_ylim(0, 1); ax_diag.axis('off')
ax_diag.text(0.5, 0.97, "Solver Diagnostics", ha='center', va='top',
             color=COLORS["text"], fontsize=10, fontweight='bold', fontfamily='monospace')
 
iter_text   = ax_diag.text(0.05, 0.72, "Iterations : ---", va='top',
                            color=COLORS["ok"], fontsize=9, fontfamily='monospace')
time_text   = ax_diag.text(0.05, 0.50, "Solve time : ---", va='top',
                            color=COLORS["ok"], fontsize=9, fontfamily='monospace')
err_text    = ax_diag.text(0.05, 0.28, "EE error   : ---", va='top',
                            color=COLORS["accent"], fontsize=9, fontfamily='monospace')
clamp_text  = ax_diag.text(0.05, 0.08, "", va='top',
                            color=COLORS["clamp"], fontsize=8, fontfamily='monospace')
 
# ── Legend ────────────────────────────────────────────────────────────────
legend_elems = [
    Line2D([0],[0], color=COLORS["upper"],   lw=4, label=f"Upper arm  {L1:.4f} m"),
    Line2D([0],[0], color=COLORS["forearm"], lw=4, label=f"Forearm    {L2:.4f} m"),
    Line2D([0],[0], color=COLORS["wrist"],   lw=3, label=f"Wrist      {L3:.4f} m"),
    Line2D([0],[0], marker='*', color=COLORS["target"], ms=10, lw=0, label="Target"),
]
ax_info.legend(handles=legend_elems, loc='lower center', bbox_to_anchor=(0.5, 0.0),
               fontsize=7.5, facecolor=COLORS["panel"], edgecolor=COLORS["slider_bg"],
               labelcolor=COLORS["text"], framealpha=1)
 
 
# ─────────────────────────────────────────────
#  Redraw
# ─────────────────────────────────────────────
def redraw(tr: float, tz: float):
    pts, angles, iters, elapsed_us, clamped = solve_ik(tr, tz)
    rs = [p[0] for p in pts]
    zs = [p[1] for p in pts]
 
    # Arm segments
    seg_upper.set_data(  rs[0:2], zs[0:2])
    seg_forearm.set_data(rs[1:3], zs[1:3])
    seg_wrist.set_data(  rs[2:4], zs[2:4])
 
    # Dots
    joint_dots.set_data(rs[:3], zs[:3])
    end_dot.set_data([rs[3]], [zs[3]])
    target_dot.set_data([tr], [tz])
 
    # Crosshair
    hf = REACH * 0.022
    cross_h.set_data([tr - hf, tr + hf], [tz, tz])
    cross_v.set_data([tr, tr], [tz - hf, tz + hf])
 
    # Joint angle labels
    for i, t in enumerate(angle_texts):
        deg = np.degrees(angles[i])
        lo_d = JOINT_DEFS[i]["lo"]
        hi_d = JOINT_DEFS[i]["hi"]
        # colour: orange if clamped, green if near limit, normal otherwise
        if i in clamped:
            col = COLORS["clamp"]
        else:
            col = COLORS["text"]
        t.set_text(f"  {SHORT[i]}: {deg:+7.2f}°")
        t.set_color(col)
 
    # Diagnostics
    iter_color = COLORS["ok"] if iters < 50 else COLORS["warn"]
    iter_text.set_text(f"Iterations : {iters:3d} / 100")
    iter_text.set_color(iter_color)
 
    time_color = COLORS["ok"] if elapsed_us < 500 else COLORS["warn"]
    time_text.set_text(f"Solve time : {elapsed_us:.1f} µs")
    time_text.set_color(time_color)
 
    err = np.hypot(rs[3] - tr, zs[3] - tz)
    err_mm = err * 1000
    err_color = COLORS["ok"] if err_mm < 1.0 else COLORS["accent"]
    err_text.set_text(f"EE error   : {err_mm:.3f} mm")
    err_text.set_color(err_color)
 
    if np.hypot(tr, tz - BASE_Z_OFFSET) > TOTAL_LENGTH:
        clamp_text.set_text("⚠  Out of reach — arm fully extended")
        clamp_text.set_color(COLORS["accent"])
    elif clamped:
        names = ", ".join(JOINT_DEFS[j]["name"] for j in clamped)
        clamp_text.set_text(f"⚠  Clamped: {names}")
        clamp_text.set_color(COLORS["clamp"])
    else:
        clamp_text.set_text("✓  All joints within limits")
        clamp_text.set_color(COLORS["ok"])
 
    fig.canvas.draw_idle()
 
 
def on_slider(_val):
    redraw(slider_r.val, slider_z.val)
 
def on_click(event):
    if event.inaxes is ax and event.button == 1:
        slider_r.set_val(event.xdata)
        slider_z.set_val(event.ydata)
 
def on_reset(_event):
    slider_r.reset()
    slider_z.reset()
 
slider_r.on_changed(on_slider)
slider_z.on_changed(on_slider)
fig.canvas.mpl_connect('button_press_event', on_click)
btn_reset.on_clicked(on_reset)
 
redraw(slider_r.valinit, slider_z.valinit)
plt.show()
