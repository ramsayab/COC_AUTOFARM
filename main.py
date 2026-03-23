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
from random import choice, sample


shortcut_path = "C:/Users/User/Desktop/Clash of Clans.lnk"
deploy_type = 2    # 1. random place one side 2. random place everyside
troops = [2, [10, 4] ]    # [how many unique troops, [each quantity] ] --> eg; 10 e-drag & 4 baloon [2, [10, 4]] - this mean your e-drag shortcut is 1 and ballon is 2
spell_shortcut = "a"     # Just work on Lightning spell



print("Membuka Clash of Clans via Google Play Games PC...")
os.startfile(shortcut_path)
time.sleep(30)


# Cari jendela game CoC
windows = gw.getWindowsWithTitle("Clash of Clans")[0]
if not windows:
    print(f"COC tidak Ada! Pastikan game sudah terbuka.")

else:
    # Bawa jendela game ke paling depan
    windows.activate() 
    time.sleep(1)
    
    # Ambil koordinat spesifik jendela CoC
    sct = mss.mss()
    monitor = {
        "left": windows.left,
        "top": windows.top,
        "width": windows.width,
        "height": windows.height
    }

    classes = pd.read_csv("data/classes.txt", header=None)[0].to_list()
    model = YOLO("model/best.pt")

    screenshot = sct.grab(monitor)
    img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)

    result = model(img, conf=0.7)
    for r in result:
        for box in r.boxes:
            cls = int(box.cls[0])
            conf = float(box.conf[0])

            if classes[cls] != "air_defense": continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            cx = int( monitor["left"] + ((x1 + x2) / 2) )
            cy = int( monitor["top"] + ((y1 + y2) / 2) )

            pyin.press(spell_shortcut)
            time.sleep(choice( np.arange(0, 0.5, 0.1) ))
            for each in range(3):
                pyin.click(x= cx+choice(np.arange(2, 14, 1)), y= cy+choice(np.arange(1, 9, 1)))
                time.sleep(choice( np.arange(0.1, 0.4, 0.1) ))
        time.sleep( choice(np.linspace(0.5, 1, 5)) )


    green_zone = {
    "top_left": [(1039, 164), (339, 654)],
    "top_right": [(1548, 67), (2410, 711)],
    "bot_left": [(296, 728), (904, 1214)],
    "bot_right": [(2424, 722), (1779, 1210)]
    }
    if deploy_type == 1:
        deploy_pos = green_zone[choice(list(green_zone))]
        x = np.linspace( deploy_pos[0][0], deploy_pos[-1][0], 100 ).astype(int)
        y = np.linspace( deploy_pos[0][1], deploy_pos[-1][1], 100 ).astype(int)
        coor = list(zip(x, y))

    else:
        coor = []
        for key in list(green_zone):
            avg = int(sum(troops[1])/4) + 1
            x = np.linspace( green_zone[key][0][0], green_zone[key][-1][0], 30 ).astype(int)
            y = np.linspace( green_zone[key][0][1], green_zone[key][-1][1], 30 ).astype(int)
            coor.append( sample(list(zip(x, y)), avg) )
        coor = [row for rows in coor for row in rows]
    
for type in range(troops[0]):
    pyin.press(f"{type+1}")
    time.sleep(1)
    for num in range(troops[1][type]):
        t = choice(coor)
        pyin.click(t[0] + monitor["left"], t[1] + monitor["top"])
        time.sleep( choice(np.linspace(0, 1, 5)) )

for hero in ['q', 'w', 'e', 'r', 'z']:
    pyin.press(hero)
    time.sleep(0.4)
    t = choice(coor)
    pyin.click(t[0] + monitor["left"], t[1] + monitor["top"])

