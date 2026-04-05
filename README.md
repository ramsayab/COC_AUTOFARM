<div align="center">

<!-- BANNER -->
<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1a1a2e,50:e94560,100:0f3460&height=220&section=header&text=⚡%20CoC%20AutoFarmer&fontSize=52&fontColor=ffffff&fontAlignY=38&desc=Fully%20Automated%20Clash%20of%20Clans%20Farming%20Bot&descAlignY=60&descColor=cccccc" width="100%"/>

<br/>

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![YOLO26](https://img.shields.io/badge/YOLO-v26-00FFCD?style=for-the-badge&logo=opencv&logoColor=black)](https://ultralytics.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org)
[![Stars](https://img.shields.io/github/stars/ramsayab/COC_AUTOFARM?style=for-the-badge&color=e94560)](https://github.com/ramsayab/COC_AUTOFARM/stargazers)

<br/>

> 🤖 **My first big project** — a fully autonomous Clash of Clans farming bot powered by **Computer Vision** and **AI Object Detection**. It logs in, upgrades walls, scouts bases, deploys troops intelligently, and loops forever. Completely hands-free.

<br/>

---

</div>

## 📺 Demo

<video src="https://github.com/user-attachments/assets/7c36ff7c-ee59-4a3d-8fab-d8eaf57cbd31" controls width="100%"></video>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [How It Works — Pipeline](#-how-it-works--pipeline)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Template Setup](#-template-setup)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Disclaimer](#-disclaimer)

---

## 🧠 Overview

CoC AutoFarmer is a fully automated farming bot that runs a continuous attack cycle in Clash of Clans. It combines two computer vision approaches:

- **Template matching** (OpenCV) — for UI navigation: detecting buttons, reading resource numbers, and identifying menu states.
- **Object detection** (YOLO26) — for in-battle intelligence: detecting enemy Air Defenses in real-time to precisely target Lightning Spells.

The bot operates in a loop: checking and upgrading walls → finding a match → evaluating enemy loot → attacking → waiting for battle end → returning to lobby → repeat.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔁 **Full Auto Loop** | Login → Farm → Upgrade Wall → Repeat, forever |
| 🧱 **Auto Wall Upgrade** | Monitors gold/elixir and auto-upgrades walls when resources exceed a set threshold |
| 🔍 **Smart Base Filter** | Reads enemy resource numbers and skips bases that don't meet the minimum loot requirement |
| 🎯 **YOLO26 Air Defense Detection** | Detects Air Defense buildings in real-time and deploys Lightning Spells directly on their coordinates |
| ⚡ **Smart Spell Deployment** | Auto-casts Lightning Spell directly on detected Air Defense coordinates |
| 🎲 **Randomized Troop Deployment** | Deploys troops at random positions — choose between 1-side or all-4-sides mode |
| 🦸 **Auto Hero Deploy** | Automatically activates and deploys all available heroes after troops |
| 🔢 **Troop Count OCR** | Reads the number of available troops from the UI automatically using template matching |
| ♻️ **Continuous Loop** | Fully autonomous cycle — no human intervention needed once started |
| ⏹️ **Safe Stop** | Press `Enter` at any time to gracefully stop the bot |

---

## ⚙️ How It Works — Pipeline

```
┌─────────────┐
│    LOGIN    │  Opens CoC via shortcut, waits for window
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│                   LOBBY MODE                    │
│  1. Check for star bonus pop-up → dismiss       │
│  2. Read gold & elixir (template matching OCR)  │
│  3. If resource > threshold → upgrade walls     │
│  4. Find and click Attack button (3 steps,      │
│     each verified with matchTemplate)           │
└──────┬──────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│                  BATTLE SCAN                    │
│  1. Run YOLO26 on screen → detect buildings     │
│  2. If buildings detected → read enemy loot     │
│  3. If loot < minimum → click Next (skip base)  │
│  4. If loot ≥ minimum → proceed to attack       │
└──────┬──────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│                    ATTACK                       │
│  1. Press spell shortcut → click Air Defense    │
│     coordinates detected by YOLO26              │
│  2. Deploy troops (auto-count via OCR,          │
│     random positions — 1 side or 4 sides)       │
│  3. Deploy heroes                               │
└──────┬──────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────┐
│                  WAIT MODE                      │
│  Loop every 2s → check for "Return Home" button │
│  If found → click → back to LOBBY MODE          │
└─────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Library | Role |
|---|---|
| [ultralytics (YOLO26)](https://github.com/ultralytics/ultralytics) | Real-time object detection for Air Defense buildings |
| [OpenCV (cv2)](https://opencv.org/) | Template matching for UI navigation and digit OCR |
| [mss](https://python-mss.readthedocs.io/) | Fast multi-monitor screen capture |
| [pydirectinput](https://github.com/learncodebygaming/pydirectinput) | DirectX-compatible mouse/keyboard simulation |
| [pynput](https://pynput.readthedocs.io/) | Global keyboard listener for safe stop |
| [pygetwindow](https://github.com/asweigart/PyGetWindow) | Detect and focus the game window |
| [pandas](https://pandas.pydata.org/) | Load YOLO26 class labels from CSV |
| [numpy](https://numpy.org/) | Array math for coordinate calculations |

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/ramsayab/COC_AUTOFARM.git
cd COC_AUTOFARM

# 2. Install dependencies
pip install -r requirements.txt
```

**requirements.txt**
```
ultralytics
opencv-python
mss
pydirectinput
pynput
pygetwindow
pandas
numpy
```

---

## 🔧 Configuration

Open `main.py` and adjust the variables at the top of the file:

```python
shortcut_path = "C:/Users/User/Desktop/Clash of Clans.lnk"  # Path to your CoC shortcut

deploy_type = 2       # 1 = random position on ONE side
                      # 2 = random positions on ALL FOUR sides

troops = 3            # Number of unique troop types (not reliable above 5)
spell_shortcut = "a"  # Keyboard shortcut for Lightning Spell

enemy_resource_minimum = 1_500_000   # Skip bases with total loot below this
wall_upgrade = 20_000_000            # Start upgrading walls when resource exceeds this
```

---

## 🖼️ Template Setup

The `template/` folder must contain the following files:

```
template/
├── number/              # Digit images (0.png – 9.png) for OCR
├── attack_btn_lobby.png # Attack button on the lobby screen
├── attack_btn_2.png     # "Find a Match" button
├── attack_btn_3.png     # Troop confirmation button
├── return_home.png      # "Return Home" button after battle
├── next_btn.png         # "Next" button to skip a base
├── star_bonus.png       # Star bonus pop-up (auto-dismissed)
├── wall_text.png        # "Wall" text in the builder menu
├── classes.txt          # YOLO26 class labels (one per line)
└── best.pt              # Your trained YOLO26 model weights
```

---

## ▶️ Usage

1. Open your emulator and log into Clash of Clans.
2. Make sure the game is on the **main village / lobby screen**.
3. Run the bot:
   ```bash
   python main.py
   ```
4. The bot will automatically find the game window and begin the farming cycle.
5. Press **`Enter`** at any time to safely stop the bot.

---

## 📁 Project Structure

```
COC_AUTOFARM/
├── main.py          # Main bot script
├── requirements.txt
├── template/
│   ├── number/      # OCR digit templates
│   ├── *.png        # UI button templates
│   ├── classes.txt  # YOLO26 class labels
│   └── best.pt      # YOLO26 model weights
└── README.md
```



## ⚠️ Disclaimer

This project was built for **educational purposes** — to explore and learn practical applications of computer vision, object detection, and GUI automation.

Using bots or automation tools in online games may violate the game's Terms of Service and can result in account bans. **Use at your own risk.** The author is not responsible for any consequences arising from the use of this software.

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f3460,50:e94560,100:1a1a2e&height=100&section=footer" width="100%"/>

</div>