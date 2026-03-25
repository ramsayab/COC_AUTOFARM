import cv2
import numpy as np
import pytesseract
import mss
import pygetwindow as gw
import time
import os

# --- TESSERACT PATH (IMPORTANT) ---
base = os.path.join(os.getcwd(), "Tesseract")
pytesseract.pytesseract.tesseract_cmd = os.path.join(base, "tesseract.exe")
os.environ["TESSDATA_PREFIX"] = os.path.join(base, "tessdata")

# --- CONFIG ---
TESS_CONFIG = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789'

# --- OCR FUNCTION ---
def read_number(gray_img, position):
    x1, y1, x2, y2 = position
    crop = gray_img[y1:y2, x1:x2]
    _, binary = cv2.threshold(crop, 200, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(binary, config=TESS_CONFIG)
    digits = ''.join(filter(str.isdigit, text))
    return int(digits) if digits else 0


# --- MAIN ---
window = gw.getWindowsWithTitle("Clash of Clans")[0]

if window.isMinimized:
    window.restore()

window.activate()
time.sleep(1)

# --- CAPTURE ---
sct = mss.mss()

monitor = {
    "left": window.left,
    "top": window.top,
    "width": window.width,
    "height": window.height
}

screenshot = sct.grab(monitor)
img = np.array(screenshot)

# ✅ CORRECT: BGRA → GRAY
gray_img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)

# --- YOUR ABSOLUTE COORDINATES ---
gold = (2187, 98, 2507, 150)
elixir = (2187, 211, 2507, 260)

# ✅ CONVERT TO WINDOW-RELATIVE
abs_x1, abs_y1, abs_x2, abs_y2 = elixir

rel_x1 = abs_x1
rel_y1 = abs_y1
rel_x2 = abs_x2
rel_y2 = abs_y2

roi = (rel_x1, rel_y1, rel_x2, rel_y2)




# --- OCR ---
value = read_number(gray_img, roi)

print("Detected value:", value)