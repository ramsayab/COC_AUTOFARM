from ultralytics import YOLO
import cv2
import pandas as pd

classes = pd.read_csv("data/classes.txt", header=None)[0].to_list()

model = YOLO("runs/detect/train/weights/best.pt")

img = cv2.imread("data/images/val/62c69789-Screenshot_2026-03-20_152553.png")

yHat = model(img)

for r in yHat:
    boxes = r.boxes
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        cls = int(box.cls[0])
        conf = float(box.conf[0])

        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        print(f"\n\nclass: {classes[cls]}, conf: {conf:.2f}")
        print(f"center: ({cx}, {cy})")