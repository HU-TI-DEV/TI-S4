from ultralytics import YOLO

DATA    = 'dataset.yaml'
WEIGHTS = 'yolo11n.pt'

model = YOLO(WEIGHTS)

results = model.train(
    data         = DATA,
    epochs       = 100,
    imgsz        = 640,
    batch        = 16,
    workers      = 0,
    device       = '0',
    project      = 'runs',
    name         = 'weights',
    save         = True,
    save_period  = 10,
    plots        = True,
    verbose      = True,
)

print("\nTraining complete.")
print("Best weights at: runs/weights/best.pt")