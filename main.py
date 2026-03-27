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
from random import choice, sample, randint, uniform


shortcut_path = "C:/Users/User/Desktop/Clash of Clans.lnk" 
deploy_type = 2    # 1. random place one side 2. random place everyside
troops = [3, [10, 10, 10] ]    # [how many unique troops, [each quantity] ] --> eg; 10 e-drag & 4 baloon [2, [10, 4]] - this mean your e-drag shortcut is 1 and ballon is 2
spell_shortcut = "a"     # Just work on Lightning spell

enemy_resource_minimum = 1500000   # Minimum Enemy resource (gold and Elxir)
wall_upgrade = 20000000   # How much resource until upgrade wall


green_zone = {
"top_left": [(1039, 164), (339, 654)],
"top_right": [(1548, 67), (2410, 711)],
"bot_left": [(296, 728), (904, 1214)],
"bot_right": [(2424, 722), (1779, 1210)] }

# --- TESSERACT PATH ---
base = os.path.join(os.getcwd(), "Tesseract")
pytesseract.pytesseract.tesseract_cmd = os.path.join(base, "tesseract.exe")
os.environ["TESSDATA_PREFIX"] = os.path.join(base, "tessdata")


print("Opening COC...")
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
def read_resource_number(gray_img, position, thresh=200):
    x1, y1, x2, y2 = position
    crop = gray_img[y1:y2, x1:x2]
    _, binary = cv2.threshold(crop, thresh, 255, cv2.THRESH_BINARY)
    text = pytesseract.image_to_string(binary, config=TESS_CONFIG)
    digits = ''.join(filter(str.isdigit, text))
    return int(digits) if digits else 0

# find wall upgrade text in bulding list
def find_wall_text_coor(gray_img):
    _, binary = cv2.threshold(gray_img, 200, 255, cv2.THRESH_BINARY)
    template = cv2.imread("model/wall_text.png", 0)
    _, template_bin = cv2.threshold(template, 200, 255, cv2.THRESH_BINARY)
    res = cv2.matchTemplate(binary, template_bin, cv2.TM_CCOEFF_NORMED)
    y, x = np.where(res >= 0.7)
    return x, y

def deploy_troops_type(type):
    if type == 1:
        side = green_zone[choice(list(green_zone))]
        x, y = np.linspace(side[0][0], side[-1][0], 100).astype(int), np.linspace(side[0][1], side[-1][1], 100).astype(int)
        return list( zip(x, y) )
    else:
        coor = []
        for key in list(green_zone):
            avg = int( sum(troops[1]) / len(green_zone.keys()) )
            x, y = np.linspace( green_zone[key][0][0], green_zone[key][-1][0], 10 ).astype(int), np.linspace( green_zone[key][0][1], green_zone[key][-1][1], 10 ).astype(int)
            coor.append(sample( list(zip(x, y)), avg) )
        return [row for rows in coor for row in rows]

def get_gray_ss(monitor):
    screenshot = sct.grab(monitor)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2GRAY)
def get_bgr_ss(monitor):
    screenshot = sct.grab(monitor)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGRA2BGR)

def click_adapt(coordinate, randomness=1, sleep_between=(0.3, 0.7), offset=(0,0)):
    time.sleep(uniform(sleep_between[0], sleep_between[1]))
    pyin.click( (coordinate[0] + monitor["left"] + randint(-(randomness*2), randomness*2) + offset[0]), (coordinate[1] + monitor["top"] + randint(-randomness, randomness) + offset[1]) )

def get_match_template_coor(img, template, method): # didnt return window relative coor
    h, w = template.shape[:-1]
    match = cv2.matchTemplate(img, template, method)
    loc = np.where(match >= 0.8)
    if len(loc[0]) > 0:
        y = loc[0][0] + h // 2
        x = loc[1][0] + w // 2
        return (x, y)
    else: return 0

def auto_upgrade_wall(gray_img, save_resource, upgrade_min_resource):
    gold_value = read_resource_number(gray_img, (2280, 100, 2507, 149), thresh=220)
    elixir_value = read_resource_number(gray_img, (2280, 211, 2507, 260), thresh=200)
    time.sleep(0.5)
    if (gold_value > upgrade_min_resource) or (elixir_value > upgrade_min_resource):
        while (gold_value > save_resource) or (elixir_value > save_resource):
            click_adapt(coordinate=(1303, 119), randomness=3) # builder click
            for _ in range(5):
                time.sleep(1.5)
                gray_img = get_gray_ss(monitor)
                x, y = find_wall_text_coor(gray_img) # wall text coordinat
                if len(x) != 0:
                    click_adapt(coordinate=(x[0], y[0]), randomness=1, offset=(40, 30)) #wall click
                    if gold_value > elixir_value:
                        click_adapt(coordinate=(1561, 1190), randomness=5, sleep_between=(0.5, 0.8))
                    else:
                        click_adapt(coordinate=(1774, 1190), randomness=5, sleep_between=(0.5, 0.8))
                    
                    click_adapt(coordinate=(1860, 1280), randomness=6)   # confirm upgrade click
                    break
                else:
                    pyin.moveTo(1400 + monitor["left"], 900 + monitor["top"])
                    pyin.mouseDown()
                    for y in range(880, 600, -30):
                        pyin.moveTo(1380, y + randint(5, 10))
                        time.sleep(0.01)
                    pyin.mouseUp()
            time.sleep(1)
            gray_img = get_gray_ss(monitor)
            gold_value = read_resource_number(gray_img, (2280, 100, 2507, 149))
            elixir_value = read_resource_number(gray_img, (2280, 211, 2507, 260))


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
        time.sleep(1) # If there's an event or star bonus confirmation
        img = get_bgr_ss(monitor)
        template_bonus = cv2.imread("model/star_bonus.png")
        coor = get_match_template_coor(img, template_bonus, cv2.TM_CCOEFF_NORMED)
        if coor: click_adapt(coordinate=coor, randomness=2, sleep_between=(1, 1.3))

        gray_img = get_gray_ss(monitor) # wall upgrade start
        auto_upgrade_wall(gray_img=gray_img, save_resource=10000000, upgrade_min_resource=wall_upgrade)  

        img = get_bgr_ss(monitor)  # finding attack btn and click it
        template_atk = cv2.imread("model/attack_btn_lobby.png")
        coor = get_match_template_coor(img, template_atk, cv2.TM_CCOEFF_NORMED)
        if coor:
            click_adapt(coordinate=coor, randomness=5, sleep_between=(0.5, 0.7)) # first attk button
            click_adapt(coordinate=(442, 1029), randomness=10, sleep_between=(0.5, 0.7)) # find match btn
            click_adapt(coordinate=(2210, 1265), randomness=10, sleep_between=(1, 1.2)) # confirm troops btn
            lobby = False
            attack_mode = True
            time.sleep(2)
        else:
            print("atk btn not found waiting 1 sec..")
            continue

    if not lobby and attack_mode: # attack / farming
        time.sleep(1.5)
        img = get_bgr_ss(monitor)
        result = model(img, conf=0.6)
        if len(result[0].boxes) != 0:
            grey_img = get_gray_ss(monitor)
            current_enemy_resource_sum = read_resource_number(grey_img, (198, 215, 421, 259), thresh=225) + read_resource_number(grey_img, (198, 275, 421, 321), thresh=225) # gold & elixir enemy read
            if current_enemy_resource_sum > enemy_resource_minimum:
                temp = f"{current_enemy_resource_sum:,}".replace(",", ".")
                print(f"enemy resource total: {temp}, Start Attacking..")

                pyin.press(spell_shortcut) # start deploying spells
                for r in result: 
                    for box in r.boxes:
                        cls = int(box.cls[0])
                        if classes[cls] == "air_defense":
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            cx = int((x1 + x2) / 2)
                            cy = int((y1 + y2) / 2)
                            time.sleep(0.5)
                            for each in range(3):
                                click_adapt(coordinate=(cx, cy), randomness=4, sleep_between=(0.1, 0.2))
                        else: continue

                coor_troops_drop = deploy_troops_type(deploy_type) ## troops deploy
                for type in range(troops[0]):
                    pyin.press(f"{type+1}")
                    time.sleep(0.4)
                    for num in range(troops[1][type]):
                        click_adapt(coordinate=choice(coor_troops_drop), randomness=1, sleep_between=(0.2, 0.4))

                for hero in ['q', 'w', 'e', 'r', 'z']: # hero deploy
                    pyin.press(hero)
                    click_adapt(coordinate=choice(coor_troops_drop), randomness=1, sleep_between=(0.3, 0.5))

                attack_mode = False  # atck END
            else:
                temp = f"{current_enemy_resource_sum:,}".replace(",", ".")
                print(f"resource to little: {temp}\nskipping..")
                template_next = cv2.imread("model/next_btn.png")
                coor = get_match_template_coor(img, template_next, cv2.TM_CCOEFF_NORMED)
                if coor:
                    click_adapt(coordinate=coor, randomness=15, sleep_between=(0.7 ,1))
                else:
                    print("next btn not found, waiting 1 sec...")
                    time.sleep(1)
        else:
            print("no building detected, waiting 1 sec..")

    if not lobby:
        img = get_bgr_ss(monitor)
        template_return = cv2.imread("model/return_home.png")
        coor = get_match_template_coor(img, template_return, cv2.TM_CCOEFF_NORMED)
        if coor:
            click_adapt(coordinate=coor, randomness=5, sleep_between=(2, 3))
            lobby = True
        else: time.sleep(2)