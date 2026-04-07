import cv2
import numpy as np
import mss
import pygetwindow as gw
import time
import os

# --- KOORDINAT ---

first_troops = (234, 692, 293, 722)
second_troops = (326, 692, 376, 722)
third_troops = (413, 692, 462, 722)
fourth_troops = (495, 692, 544, 722)
fifth_troops = (571, 692, 630, 722)


mygold = (1115, 80, 1234, 100)
myelixir = (1115, 136, 1234, 161)
enemygold = (150, 137, 274, 164)
enemyelixir = (148, 172, 272, 195)

# --- FOKUS WINDOW ---
try:
    window = gw.getWindowsWithTitle("Clash of Clans")[0]
    if window.isMinimized:
        window.restore()
    window.activate()
    time.sleep(1)
except IndexError:
    print("Game Clash of Clans tidak ditemukan!")
    exit()

# --- CAPTURE ---
sct = mss.mss()
monitor = {
    "left": window.left,
    "top": window.top,
    "width": window.width,
    "height": window.height
}

screenshot = sct.grab(monitor)
gray_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)

# --- CROP ---
x1, y1, x2, y2 = fifth_troops
crop = gray_img[y1:y2, x1:x2]
h_crop, w_crop = crop.shape

# --- PREPROCESS ---
_, crop_thresh = cv2.threshold(crop, 230, 255, cv2.THRESH_BINARY)
cv2.imwrite("debug_crop_thresh.png", crop_thresh)


def read_number(gray_cropped_img):
    detected_digits = []
    for tem in os.listdir("template/number/"):
        digit_value = tem.split(".")[0]
        template = cv2.imread(f"template/number/{tem}", 0)

        for scale in np.linspace(0.4, 2, 16): # Scaling from 20 - 100 %
            w_temp = int(template.shape[1] * scale)
            h_temp = int(template.shape[0] * scale)
            if h_temp > h_crop or w_temp > w_crop or h_temp == 0 or w_temp == 0: # skip if template_size > img
                continue

            resized_template = cv2.resize(template, (w_temp, h_temp))
            match = cv2.matchTemplate(gray_cropped_img, resized_template, cv2.TM_CCOEFF_NORMED)

            loc = np.where(match >= 0.75)
            for x, y in zip(loc[1], loc[0]):
                score = match[y, x]
                detected_digits.append({
                    "x": int(x),
                    "width": int(w_temp),
                    "number": digit_value, 
                    "confidence": float(score) })
    detected_digits.sort(key=lambda d: d["confidence"], reverse=True) # Sort based on Score

    final_digits = []
    for d in detected_digits:
        overlap = False
        for f in final_digits:
            if abs(d["x"] - f["x"]) < max(d["width"], f["width"]) * 0.5:
                overlap = True
                break
        if not overlap:
            final_digits.append(d)

    final_digits.sort(key=lambda d: d["x"])
    return int("".join([d["number"] for d in final_digits]))

print("Detected value:", read_number(crop_thresh))