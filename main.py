import os
import time
import pygetwindow as gw
import mss
import cv2
import numpy as np
from ultralytics import YOLO
import cv2
import pandas as pd
from pynput import keyboard
import pydirectinput as pyin
import pytesseract
from random import choice, sample, randint


shortcut_path = "C:/Users/User/Desktop/Clash of Clans.lnk"
deploy_type = 2    # 1. random place one side 2. random place everyside
troops = [2, [10, 4] ]    # [how many unique troops, [each quantity] ] --> eg; 10 e-drag & 4 baloon [2, [10, 4]] - this mean your e-drag shortcut is 1 and ballon is 2
spell_shortcut = "a"     # Just work on Lightning spell
wall_upgrade = 20000000   # How much resource until upgrade wall

### Read Resource
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

# Absolute Coor for Resource Detection
gold = (2187, 98, 2507, 150)
elixir = (2187, 211, 2507, 260)

# find wall upgrade text in bulding list
def find_wall_text_coor(gray_img):
    _, binary = cv2.threshold(gray_img, 200, 255, cv2.THRESH_BINARY)
    template = cv2.imread("model/wall_text.png", 0)
    _, template_bin = cv2.threshold(template, 200, 255, cv2.THRESH_BINARY)
    # --- MATCH ---
    res = cv2.matchTemplate(binary, template_bin, cv2.TM_CCOEFF_NORMED)
    y, x = np.where(res >= 0.7)
    return x, y

### Deploy troops
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

x = np.linspace( 311, 159, 10 ).astype(int)
y = np.linspace( 1261, 1387, 10 ).astype(int)
attack_btn_1 = list(zip(x, y))
x = np.linspace( 242, 642, 10 ).astype(int)
y = np.linspace( 996, 1060, 10 ).astype(int)
attack_btn_2 = list(zip(x, y))
x = np.linspace( 2040, 2380, 10 ).astype(int)
y = np.linspace( 1247, 1283, 10 ).astype(int)
attack_btn_3 = list(zip(x, y))


print("Membuka Clash of Clans via Google Play Games PC...")
os.startfile(shortcut_path)
time.sleep(20)


# Cari jendela game CoC
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

    classes = pd.read_csv("data/classes.txt", header=None)[0].to_list()
    model = YOLO("model/best.pt")


run = True
def stop(key):
    global run
    if key == keyboard.Key.enter:
        print("stoping..")
        run = False
        return False
listener = keyboard.Listener(on_press=stop)
listener.start()

attack_mode = False
lobby = True
while run:
    if lobby:
        screenshot = sct.grab(monitor)
        gray_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)

        gold_value = read_number(gray_img, gold)
        elixir_value = read_number(gray_img, elixir)
        if (gold_value > wall_upgrade) and (elixir_value > wall_upgrade):
            while (gold_value > 10000000) and (elixir_value > 10000000):
                time.sleep(0.5)
                pyin.click(1303 + monitor["left"], 119 + monitor['top']) # builder click
                for _ in range(5):
                    time.sleep(1.5)
                    screenshot = sct.grab(monitor)
                    gray_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)
                    x, y = find_wall_text_coor(gray_img) # wall text coordinat
                    if len(x) != 0:
                        #wall click
                        time.sleep(0.5)
                        pyin.click(x[0] + monitor["left"] + 40 , y[0] + monitor["top"] + 30)
                        time.sleep(0.5)
                        wall_gold_coor = (1561, 1190)
                        wall_elixir_coor = (1774, 1190)
                        confirm_coor = (1860, 1280)
                        if gold_value > elixir_value:
                            pyin.click(wall_gold_coor[0] + monitor["left"] + randint(6, 13), wall_gold_coor[1] + monitor["top"] + randint(3, 7))
                            time.sleep(0.8)
                        else:
                            pyin.click(wall_elixir_coor[0] + monitor["left"] + randint(6, 13), wall_elixir_coor[1] + monitor["top"] + randint(3, 7))
                            time.sleep(0.8)

                        pyin.click(confirm_coor[0] + monitor["left"], confirm_coor[1] + monitor["top"])
                        break
                    else:
                        pyin.moveTo(1400 + monitor["left"], 900 + monitor["top"])
                        pyin.mouseDown()
                        for y in range(880, 600, -30):
                            pyin.moveTo(1380, y + randint(5, 15))
                            time.sleep(0.01)
                        pyin.mouseUp()
                time.sleep(0.7)
                screenshot = np.array(screenshot)
                gray_img = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)
                gold_value = read_number(gray_img, gold)
                elixir_value = read_number(gray_img, elixir)

        time.sleep(1)
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)
        template = cv2.imread(f"model/star_bonus.png")
        h, w = template.shape[:-1]
        match = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(match >= 0.8)
        if len(loc[0]) > 0:
            # Ambil koordinat pertama yang cocok
            y = loc[0][0]
            x = loc[1][0]
            # Hitung titik tengah tombol
            center_x = monitor["left"] + x + w // 2
            center_y = monitor["top"] + y + h // 2
            time.sleep(1)
            # Eksekusi klik
            pyin.click(center_x, center_y)


        
        time.sleep(5)
        t = choice(attack_btn_1)
        pyin.click(t[0] + monitor["left"], t[1] + monitor["top"])
        
        time.sleep(1)
        t = choice(attack_btn_2)
        pyin.click(t[0] + monitor["left"], t[1] + monitor["top"])

        time.sleep(1)
        t = choice(attack_btn_3)
        pyin.click(t[0] + monitor["left"], t[1] + monitor["top"])

        lobby = False
        attack_mode = True
        time.sleep(2)

    if not lobby and attack_mode:

        time.sleep(1)
        base_attack = np.array(sct.grab(monitor))
        img = cv2.cvtColor(base_attack, cv2.COLOR_BGRA2BGR)
        result = model(img, conf=0.6)
        if len(result[0].boxes) == 0:
            print("no building detected, waiting 1 sec..")
        else: 
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
            attack_mode = False

    if not lobby:
        screenshot = sct.grab(monitor)
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)

        template = cv2.imread(f"model/return_home.png")
        h, w = template.shape[:-1]

        match = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(match >= 0.8)

        if len(loc[0]) > 0:
            # Ambil koordinat pertama yang cocok
            y = loc[0][0]
            x = loc[1][0]
            # Hitung titik tengah tombol
            center_x = monitor["left"] + x + w // 2
            center_y = monitor["top"] + y + h // 2
            time.sleep(1)
            # Eksekusi klik
            pyin.click(center_x, center_y)
            
            lobby = True
            time.sleep(5)
        else:
            time.sleep(3)
