import pygetwindow as gw
from pynput import mouse
import mss

WINDOW_TITLE = "Clash of Clans"

def get_window():
    windows = gw.getWindowsWithTitle(WINDOW_TITLE)
    if not windows:
        raise Exception("Game window not found")
    return windows[0]

def on_click(x, y, pressed):
    s = mss.mss()
    if not pressed:
        return

    win = get_window()

    left, top = win.left, win.top

    # Convert to window-relative
    rel_x = x - left
    rel_y = y - top

    print(f"Window rel : ({rel_x}, {rel_y})\n")


with mouse.Listener(on_click=on_click) as listener:
    print("Click anywhere inside the game window...")
    listener.join()

# abs_x1, abs_y1, abs_x2, abs_y2