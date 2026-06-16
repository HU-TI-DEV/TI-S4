import os
import shutil
import random
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────────────────
SRC_DIR   = "dataset"           # your current flat folder with images + txts
DEST_DIR  = "dataset_yolo"      # output folder with train/val split
VAL_SPLIT = 0.15                # 15% for validation
SEED      = 42                  # for reproducibility
# ────────────────────────────────────────────────────────────────────────────

random.seed(SEED)

# Find all images
images = [f for f in os.listdir(SRC_DIR)
          if f.lower().endswith(('.jpg', '.jpeg', '.png'))]

print(f"Found {len(images)} images")

# Check every image has a label
missing = []
for img in images:
    stem = Path(img).stem
    if not os.path.exists(f"{SRC_DIR}/{stem}.txt"):
        missing.append(img)

if missing:
    print(f"WARNING: {len(missing)} images have no label file:")
    for m in missing[:5]:
        print(f"  {m}")

# Shuffle and split
random.shuffle(images)
split_idx = int(len(images) * (1 - VAL_SPLIT))
splits = {
    "train": images[:split_idx],
    "val":   images[split_idx:]
}

print(f"Train: {len(splits['train'])} | Val: {len(splits['val'])}")

# Create folders and copy files
for subset, files in splits.items():
    Path(f"{DEST_DIR}/images/{subset}").mkdir(parents=True, exist_ok=True)
    Path(f"{DEST_DIR}/labels/{subset}").mkdir(parents=True, exist_ok=True)

    for img_file in files:
        stem = Path(img_file).stem

        # Copy image
        shutil.copy(
            f"{SRC_DIR}/{img_file}",
            f"{DEST_DIR}/images/{subset}/{img_file}"
        )

        # Copy label
        label_src = f"{SRC_DIR}/{stem}.txt"
        if os.path.exists(label_src):
            shutil.copy(
                label_src,
                f"{DEST_DIR}/labels/{subset}/{stem}.txt"
            )

print(f"Done. Dataset written to: {DEST_DIR}/")

# Count class distribution
from collections import Counter
counts = Counter()
for subset in ["train", "val"]:
    for label_file in Path(f"{DEST_DIR}/labels/{subset}").glob("*.txt"):
        for line in open(label_file):
            line = line.strip()
            if line:
                counts[int(line.split()[0])] += 1

print("\nClass distribution across full dataset:")
for cls_id, count in sorted(counts.items()):
    print(f"  class {cls_id}: {count} annotations")