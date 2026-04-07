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
from random import choice, sample, randint, uniform


shortcut_path = "C:/Users/ramsa/OneDrive/Desktop/Clash of Clans.lnk" 
deploy_type = 2    # 1. random place one side 2. random place everyside
troops = 2    # how many unique troops (not accurate if > 5)
spell_shortcut = "a"     # Just work on Lightning spell

enemy_resource_minimum = 1500000   # Minimum Enemy resource (gold and Elxir)
wall_upgrade = 20000000   # How much resource until upgrade wall

# position
green_zone = {
"top_left": [(626, 65), (194, 395)],
"top_right": [(743, 55), (1187, 397)],
"bot_left": [(184, 407), (517, 665)],
"bot_right": [(1203, 414), (871, 667)] }

mygold = (1115, 80, 1234, 100)
myelixir = (1115, 136, 1234, 161)
enemygold = (150, 137, 274, 164)
enemyelixir = (148, 172, 272, 195)

troops_coor_number = [(234, 692, 293, 722), (326, 692, 376, 722), (413, 692, 462, 722), (495, 692, 544, 722), (571, 692, 630, 722)]

print("Opening COC...")
os.startfile(shortcut_path)
time.sleep(4)

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

# --- OCR FUNCTION ---
def read_number(gray_img, position, thresh):
    detected_digits = []

    x1, y1, x2, y2 = position
    crop = gray_img[y1:y2, x1:x2]
    h_crop, w_crop = crop.shape

    
    _, crop_thresh = cv2.threshold(crop, thresh, 255, cv2.THRESH_BINARY)
    cv2.imwrite("debug_crop_thresh.png", crop_thresh)

    for tem in os.listdir("template/number/"):
        digit_value = tem.split(".")[0]
        template = cv2.imread(f"template/number/{tem}", 0)
        for scale in np.linspace(0.4, 2, 16): # Scaling from 20 - 100 %
            w_temp = int(template.shape[1] * scale)
            h_temp = int(template.shape[0] * scale)
            if h_temp > h_crop or w_temp > w_crop or h_temp == 0 or w_temp == 0: # skip if template_size > img
                continue

            resized_template = cv2.resize(template, (w_temp, h_temp))
            match = cv2.matchTemplate(crop_thresh, resized_template, cv2.TM_CCOEFF_NORMED)

            loc = np.where(match >= 0.75)
            for x, y in zip(loc[1], loc[0]):
                score = match[y, x]
                detected_digits.append({
                    "x": int(x),
                    "width": int(w_temp),
                    "number": digit_value, 
                    "confidence": float(score) })
    
    if not detected_digits: return 0
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
    final_digits = int("".join([d["number"] for d in final_digits]))
    return final_digits if final_digits else 0

# find wall upgrade text in bulding list
def find_wall_text_coor(gray_img):
    _, binary = cv2.threshold(gray_img, 200, 255, cv2.THRESH_BINARY)
    template = cv2.imread("template/wall_text.png", 0)
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
            x, y = np.linspace( green_zone[key][0][0], green_zone[key][-1][0], 10 ).astype(int), np.linspace( green_zone[key][0][1], green_zone[key][-1][1], 10 ).astype(int)
            coor.append(sample( list(zip(x, y)), 6) )
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

def auto_upgrade_wall(gray_img, upgrade_min_resource):

    gold_value = read_number(gray_img, mygold, 230)
    elixir_value = read_number(gray_img, myelixir, 200)
    print(f"current resource:\ngold:{gold_value}, elixir:{elixir_value}")
    time.sleep(0.5)
    if (gold_value > upgrade_min_resource) or (elixir_value > upgrade_min_resource):
        click_adapt(coordinate=(651, 67), randomness=1) # builder click
        for _ in range(5):
            time.sleep(1.5)
            gray_img = get_gray_ss(monitor)
            x, y = find_wall_text_coor(gray_img) # wall text coordinat
            if len(x) != 0:
                click_adapt(coordinate=(x[0], y[0]), randomness=1, offset=(40, 30)) #wall click  #####
                if gold_value > elixir_value:
                    click_adapt(coordinate=(801, 657), randomness=1, sleep_between=(0.5, 0.8))
                else:
                    click_adapt(coordinate=(916, 660), randomness=1, sleep_between=(0.5, 0.8))
                
                click_adapt(coordinate=(960, 715), randomness=2)   # confirm upgrade click
                break
            else:
                pyin.moveTo(693 + monitor["left"], 440 + monitor["top"])
                pyin.mouseDown()
                for y in range(420, 200, -30):
                    pyin.moveTo(677, y + randint(5, 10))
                    time.sleep(0.01)
                pyin.mouseUp()
        time.sleep(1)
        gray_img = get_gray_ss(monitor)
        gold_value = read_number(gray_img, mygold, 210)
        elixir_value = read_number(gray_img, myelixir, 200)


classes = pd.read_csv("template/classes.txt", header=None)[0].to_list()
model = YOLO("template/best.pt")
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
        template_bonus = cv2.imread("template/star_bonus.png")
        coor = get_match_template_coor(img, template_bonus, cv2.TM_CCOEFF_NORMED)
        if coor: click_adapt(coordinate=coor, randomness=0, sleep_between=(1, 1.3))

        gray_img = get_gray_ss(monitor) # wall upgrade start
        if not read_number(gray_img, mygold, 230):
            print("lobby not loaded..")
            continue
        
        auto_upgrade_wall(gray_img=gray_img, upgrade_min_resource=wall_upgrade)  

        img = get_bgr_ss(monitor)  # finding attack btn and click it
        template_atk_1 = cv2.imread("template/attack_btn_lobby.png")
        atk_btn_1 = get_match_template_coor(img, template_atk_1, cv2.TM_CCOEFF_NORMED)
        if atk_btn_1:
            click_adapt(coordinate=atk_btn_1, randomness=5, sleep_between=(0.5, 0.7)) # first attk button

            time.sleep(1)
            template_atk_2 = cv2.imread("template/attack_btn_2.png")
            img = get_bgr_ss(monitor)
            atk_btn_2 = get_match_template_coor(img, template_atk_2, cv2.TM_CCOEFF_NORMED)
            while not atk_btn_2:
                print("attack button 2 not found..")
                time.sleep(1)
                img = get_bgr_ss(monitor)
                atk_btn_2 = get_match_template_coor(img, template_atk_2, cv2.TM_CCOEFF_NORMED)
            click_adapt(coordinate=atk_btn_2, randomness=10, sleep_between=(0.5, 0.7)) # find match btn

            template_atk_3 = cv2.imread("template/attack_btn_3.png")
            img = get_bgr_ss(monitor)
            atk_btn_3 = get_match_template_coor(img, template_atk_3, cv2.TM_CCOEFF_NORMED)
            while not atk_btn_3:
                print("attack button 3 not found..")
                time.sleep(1)
                img = get_bgr_ss(monitor)
                atk_btn_3 = get_match_template_coor(img, template_atk_3, cv2.TM_CCOEFF_NORMED)
            click_adapt(coordinate=atk_btn_3, randomness=10, sleep_between=(1, 1.2)) # confirm troops btn


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
            current_enemy_resource_sum = read_number(grey_img, enemygold, 230) + read_number(grey_img, enemyelixir, 230) # gold & elixir enemy read
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

                for shortcut in range(troops):
                    gray_img = get_gray_ss(monitor)
                    crop = troops_coor_number[shortcut]

                    pyin.press(f"{shortcut + 1}")
                    time.sleep(0.4)
                    for _ in range(read_number(gray_img, crop, 200)):
                        click_adapt(coordinate=choice(coor_troops_drop), randomness=1, sleep_between=(0.1, 0.2))

                for hero in ['q', 'w', 'e', 'r', 'z']: # hero deploy
                    pyin.press(hero)
                    click_adapt(coordinate=choice(coor_troops_drop), randomness=1, sleep_between=(0.2, 0.3))

                attack_mode = False  # atck END
            else:
                temp = f"{current_enemy_resource_sum:,}".replace(",", ".")
                print(f"resource to little: {temp}\nskipping..")
                template_next = cv2.imread("template/next_btn.png")
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
        template_return = cv2.imread("template/return_home.png")
        coor = get_match_template_coor(img, template_return, cv2.TM_CCOEFF_NORMED)
        if coor:
            click_adapt(coordinate=coor, randomness=5, sleep_between=(2, 3))
            lobby = True
        else: time.sleep(2)