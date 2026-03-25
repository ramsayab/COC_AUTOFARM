import cv2
import numpy as np
import pygetwindow as gw
import time
import mss
import pydirectinput as pyin
import random


windows = gw.getWindowsWithTitle("Clash of Clans")[0]
if not windows:
    print(f"COC tidak Ada! Pastikan game sudah terbuka.")

else:
    # Bawa jendela game ke paling depan
    if windows.isMinimized:
        windows.restore()
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
# builder click
pyin.click(1303 + monitor["left"], 119 + monitor['top'])
time.sleep(1)


def find_wall_coor():
    screenshot = sct.grab(monitor)

    gray = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

    template = cv2.imread("model/wall_text.png", 0)
    _, template_bin = cv2.threshold(template, 200, 255, cv2.THRESH_BINARY)
    # --- MATCH ---
    res = cv2.matchTemplate(binary, template_bin, cv2.TM_CCOEFF_NORMED)
    y, x = np.where(res >= 0.7)
    return x, y


# Scroll Builder
for _ in range(10):
    time.sleep(1)
    x, y = find_wall_coor()
    if len(x) != 0:
        #wall click
        print("FOUND:", x[0],", ", y[0])
        time.sleep(0.5)
        pyin.click(x[0] + monitor["left"] + 40 , y[0] + monitor["top"] + 30)
        time.sleep(0.5)
        wall_gold_coor = (1561, 1190)
        wall_elixir_coor = (1774, 1190)
        confirm_coor = (1860, 1280)
        pyin.click(wall_gold_coor[0] + monitor["left"] + random.randint(6, 13), wall_gold_coor[1] + monitor["top"] + random.randint(3, 7))
        time.sleep(0.8)
        pyin.click(confirm_coor[0] + monitor["left"], confirm_coor[1] + monitor["top"])

        break
    else: 
        pyin.moveTo(1400 + monitor["left"], 900 + monitor["top"])
        pyin.mouseDown()
        for y in range(880, 600, -30):
            pyin.moveTo(1380, y + random.randint(5, 15))
            time.sleep(0.001)
        pyin.mouseUp()