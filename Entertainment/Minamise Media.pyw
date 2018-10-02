import win32gui
import win32con
import win32api
import sys
from pynput import keyboard

COMBINATIONS = [
    {keyboard.Key.f12}

    # {keyboard.Key.shift, keyboard.KeyCode(char='A')},
]

current = set()

def execute():
    # Finds window of name and minamises it
    hwndMain = win32gui.FindWindow(None, "The Story of Sylvanas Windrunner - Full Version[Lore] - Youtube - Google Chrome")
    if win32gui.IsIconic(hwndMain):
        print('gonna mini')
        win32gui.ShowWindow(hwndMain, win32con.SW_MINIMIZE)  # win32con.SW_MINIMIZE = Minimize, True = Show
    else:
        print('gonna Show')
        win32gui.ShowWindow(hwndMain, True)  # win32con.SW_MINIMIZE = Minimize, True = Show

def on_press(key):
    if any([key in COMBO for COMBO in COMBINATIONS]):
        current.add(key)
        if any(all(k in current for k in COMBO) for COMBO in COMBINATIONS):
            execute()

def on_release(key):
    if any([key in COMBO for COMBO in COMBINATIONS]):
        current.remove(key)

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()



