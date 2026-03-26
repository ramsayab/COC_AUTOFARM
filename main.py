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

enemy_resource_minimum = 1500000   # Minimum Enemy resource (gold and Elxir)
wall_upgrade = 20000000   # How much resource until upgrade wall


### Read Resource
# --- TESSERACT PATH (IMPORTANT) ---
base = os.path.join(os.getcwd(), "Tesseract")
pytesseract.pytesseract.tesseract_cmd = os.path.join(base, "tesseract.exe")
os.environ["TESSDATA_PREFIX"] = os.path.join(base, "tessdata")

### Deploy troops Zone
green_zone = {
"top_left": [(1039, 164), (339, 654)],
"top_right": [(1548, 67), (2410, 711)],
"bot_left": [(296, 728), (904, 1214)],
"bot_right": [(2424, 722), (1779, 1210)]
}
# Absolute Coor for Resource Detection
gold = (2280, 100, 2507, 149)
elixir = (2280, 211, 2507, 260)
# enemy resource
gold_enemy = (198, 215, 421, 259)
elixir_enemy = (198, 275, 421, 321)



print("Membuka Clash of Clans via Google Play Games PC...")
os.startfile(shortcut_path)
time.sleep(7)

# Cari jendela game CoC
windows = gw.getWindowsWithTitle("Clash of Clans")[0]
if not windows:
    print(f"Coc tidak ada.")
else:
    if windows.isMinimized:
        windows.restore()
    windows.activate()

    time.sleep(1)
    sct = mss.mss()
    monitor = {
        "left": windows.left,
        "top": windows.top,
        "width": windows.width,
        "height": windows.height
    }


# --- CONFIG ---
TESS_CONFIG = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789'
# --- OCR FUNCTION ---
def read_resource_number(gray_img, position):
    x1, y1, x2, y2 = position
    crop = gray_img[y1:y2, x1:x2]
    _, binary = cv2.threshold(crop, 220, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(binary, config=TESS_CONFIG)
    digits = ''.join(filter(str.isdigit, text))
    return int(digits) if digits else 0

# find wall upgrade text in bulding list
def find_wall_text_coor(gray_img):
    _, binary = cv2.threshold(gray_img, 200, 255, cv2.THRESH_BINARY)
    template = cv2.imread("model/wall_text.png", 0)
    _, template_bin = cv2.threshold(template, 200, 255, cv2.THRESH_BINARY)
    # --- MATCH ---
    res = cv2.matchTemplate(binary, template_bin, cv2.TM_CCOEFF_NORMED)
    y, x = np.where(res >= 0.7)
    return x, y

def get_random_between_coor(x, y, variation):
    x = np.linspace(x[0], x[1], variation).astype(int)
    y = np.linspace(y[0], y[1], variation).astype(int)
    return list( zip(x, y) )

def deploy_troops_type(green_zone, type):
    if type == 1:
        side = green_zone[choice(list(green_zone))]
        return get_random_between_coor( x=(side[0][0], side[-1][0]), y=(side[0][1], side[-1][1]), variation=100)
    else:
        coor = []
        for key in list(green_zone):
            avg = int(sum(troops[1])/4) + 1
            coor.append( sample( get_random_between_coor(x=(green_zone[key][0][0], green_zone[key][-1][0]), y=(green_zone[key][0][1], green_zone[key][-1][1]), variation=10), avg ) )
        return [row for rows in coor for row in rows]

def get_gray_ss(monitor):
    screenshot = sct.grab(monitor)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)
def get_bgr_ss(monitor):
    screenshot = sct.grab(monitor)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)


classes = pd.read_csv("data/classes.txt", header=None)[0].to_list()
model = YOLO("model/best.pt")
total_resource_get = 0
run = True
def stop(key):
    global run
    if key == keyboard.Key.enter:
        print(f"stoping..\nget resource: {total_resource_get}")
        run = False
        return False
listener = keyboard.Listener(on_press=stop)
listener.start()

attack_mode = False
lobby = True
while run:
    if lobby:
        gray_img = get_gray_ss(monitor)
        gold_value = read_resource_number(gray_img, gold)
        elixir_value = read_resource_number(gray_img, elixir)
        time.sleep(0.5)
        if (gold_value > wall_upgrade) and (elixir_value > wall_upgrade):   # fix note
            while (gold_value > 10000000) and (elixir_value > 10000000):
                time.sleep(0.5)
                pyin.click(1303 + monitor["left"], 119 + monitor['top']) # builder click
                for _ in range(5):
                    time.sleep(1.5)
                    gray_img = get_gray_ss(monitor)
                    x, y = find_wall_text_coor(gray_img) # wall text coordinat
                    if len(x) != 0:
                        #wall clicka
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
                gray_img = get_gray_ss(monitor)
                gold_value = read_resource_number(gray_img, gold)
                elixir_value = read_resource_number(gray_img, elixir)

        time.sleep(1)
        img = get_bgr_ss(monitor)
        template = cv2.imread("model/star_bonus.png")
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

        print("atk btn not found waiting 1 sec..")
        time.sleep(1)
        img = get_bgr_ss(monitor)
        template_atk = cv2.imread("model/attack_btn_lobby.png")
        h, w = template.shape[:-1]
        match = cv2.matchTemplate(img, template_atk, cv2.TM_CCOEFF_NORMED)
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

            time.sleep(1)
            t = choice(get_random_between_coor( x=(242, 642), y=(996, 1060), variation=10 ))
            pyin.click(t[0] + monitor["left"], t[1] + monitor["top"])

            time.sleep(1)
            t = choice(get_random_between_coor( x=(2040, 2380), y=(1247, 1283), variation=10 ))
            pyin.click(t[0] + monitor["left"], t[1] + monitor["top"])

            lobby = False
            attack_mode = True
            time.sleep(2)
        else: continue
        
    if not lobby and attack_mode:
        time.sleep(1)
        img = get_bgr_ss(monitor)
        result = model(img, conf=0.6)
        if len(result[0].boxes) == 0:
            print("no building detected, waiting 1 sec..")
        else:
            grey_img = get_gray_ss(monitor)
            current_enemy_resource_sum = read_resource_number(grey_img, gold_enemy) + read_resource_number(grey_img, elixir_enemy)
            if current_enemy_resource_sum > enemy_resource_minimum:
                print(f"enemy resource total: {current_enemy_resource_sum}, Start Attacking..")
                total_resource_get += current_enemy_resource_sum
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

                coor_troops_drop = deploy_troops_type(green_zone, deploy_type)
                for type in range(troops[0]):
                    pyin.press(f"{type+1}")
                    time.sleep(1)
                    for num in range(troops[1][type]):
                        t = choice(coor_troops_drop)
                        pyin.click(t[0] + monitor["left"], t[1] + monitor["top"])
                        time.sleep( choice(np.linspace(0, 1, 5)) )

                for hero in ['q', 'w', 'e', 'r', 'z']:
                    pyin.press(hero)
                    time.sleep(0.4)
                    t = choice(coor_troops_drop)
                    pyin.click(t[0] + monitor["left"], t[1] + monitor["top"])
                attack_mode = False
            else:
                print(f"resource to little: {current_enemy_resource_sum}\nskipping..")
                template_next = cv2.imread("model/next_btn.png")
                h, w = template_return.shape[:-1]
                match = cv2.matchTemplate(img, template_next, cv2.TM_CCOEFF_NORMED)
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


    if not lobby:
        screenshot = sct.grab(monitor)
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)

        template_return = cv2.imread("model/return_home.png")
        h, w = template_return.shape[:-1]

        match = cv2.matchTemplate(img, template_return, cv2.TM_CCOEFF_NORMED)
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
            time.sleep(2)
        else:
            time.sleep(2)
