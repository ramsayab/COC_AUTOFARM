import os
import time
import pygetwindow as gw
import mss
import cv2
import numpy as np
from ultralytics import YOLO
import cv2
import pandas as pd
import ctypes
import pydirectinput as pyin

classes = pd.read_csv("data/classes.txt", header=None)[0].to_list()
model = YOLO("runs/detect/train/weights/best.pt")
shortcut_path = "C:/Users/User/Desktop/Clash of Clans.lnk"

print("Membuka Clash of Clans via Google Play Games PC...")
try:
    os.startfile(shortcut_path)
    time.sleep(20)
except FileNotFoundError:
    print(f"Error: Shortcut tidak ditemukan di {shortcut_path}")
    exit()

# 2. Cari jendela game CoC
window_name = "Clash of Clans"
windows = gw.getWindowsWithTitle(window_name)

if not windows:
    print(f"Jendela '{window_name}' tidak ditemukan! Pastikan game sudah terbuka sepenuhnya.")
else:
    coc_window = windows[0]
    
    # Bawa jendela game ke paling depan
    coc_window.activate() 
    time.sleep(1)
    
    # 3. Ambil koordinat spesifik jendela CoC
    sct = mss.mss()
    monitor = {
        "left": coc_window.left,
        "top": coc_window.top,
        "width": coc_window.width,
        "height": coc_window.height
    }

    # 4. Mulai Merekam (Di sini kamu bisa sisipkan model YOLO-mu)
    print("Tekan 'q' pada jendela deteksi untuk berhenti.")
    while True:
        screenshot = sct.grab(monitor)
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)

        result = model(img, conf=0.5, save=True)

        for r in result:
            for box in r.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                if classes[cls] != "air_defense": continue
                if conf < 0.7: continue

                x1, y1, x2, y2 = box.xyxy[0].tolist()
                cx = monitor["left"] + ((x1 + x2) / 2)
                cy = monitor["top"] + ((y1 + y2) / 2)

                pyin.press("a")
                time.sleep(1)
                for each in range(3):
                    pyin.click(x=int(cx), y=int(cy))
                    time.sleep(0.2)

                print(f"\n\nclass: {classes[cls]}, conf: {conf:.2f}")
                print(f"center: ({cx}, {cy})")


        if ctypes.windll.user32.GetAsyncKeyState(0x20) !=0:
            print("quit games...")
            break

        time.sleep(1)


