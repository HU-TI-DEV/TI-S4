"""
Evaluate and visualize your trained model.
Run this after training completes.
"""

from ultralytics import YOLO
import os

WEIGHTS = 'runs\\detect\\runs\\detect\\gazebo_scratch-2\\weights\\best.pt'
DATA    = 'dataset.yaml'

model = YOLO(WEIGHTS)

# ── VALIDATION METRICS ────────────────────────────────────────────────────
print("Running validation...")
metrics = model.val(data=DATA, conf=0.001, iou=0.6)

print(f"\n── Results ──────────────────────────────────────")
print(f"mAP50:      {metrics.box.map50:.4f}   (target: > 0.80)")
print(f"mAP50-95:   {metrics.box.map:.4f}   (target: > 0.55)")
print(f"Precision:  {metrics.box.mp:.4f}   (of all predictions, how many correct)")
print(f"Recall:     {metrics.box.mr:.4f}   (of all real objects, how many found)")

print(f"\n── Per-class AP50 ───────────────────────────────")
for i, ap in enumerate(metrics.box.ap50):
    print(f"  class {i}: {ap:.4f}")

# ── INFERENCE ON TEST IMAGES ──────────────────────────────────────────────
print("\nRunning inference on sample images...")

# Test on a few val images
val_images = [
    f"dataset_yolo/images/val/{f}"
    for f in os.listdir("dataset_yolo/images/val")[:5]
]

results = model(val_images, conf=0.25, iou=0.4)

for i, r in enumerate(results):
    print(f"\nImage {i+1}: {r.path}")
    if r.boxes is not None:
        for box in r.boxes:
            cls_id = int(box.cls)
            conf   = float(box.conf)
            xyxy   = box.xyxy[0].tolist()
            print(f"  class {cls_id} | conf: {conf:.2f} | box: {[round(x,1) for x in xyxy]}")
    else:
        print("  No detections")

# Save annotated images
save_dir = "inference_results"
os.makedirs(save_dir, exist_ok=True)
results2 = model(val_images, conf=0.25, save=True, project=save_dir, name="test")
print(f"\nAnnotated images saved to: {save_dir}/test/")

# ── EXPORT ────────────────────────────────────────────────────────────────
print("\nExporting to ONNX for deployment...")
model.export(format='onnx', imgsz=640, simplify=True)
print("ONNX model saved alongside best.pt")