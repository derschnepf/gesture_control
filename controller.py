import pyautogui
import os

class MacController:
    def __init__(self):
        pyautogui.FAILSAFE = False
        self.bildschirm_breite, self.bildschirm_hoehe = pyautogui.size()

    def maus_bewegen(self, x_ratio, y_ratio):
        maus_x = int(x_ratio * self.bildschirm_breite)
        maus_y = int(y_ratio * self.bildschirm_hoehe)
        pyautogui.moveTo(maus_x, maus_y)

    def klicken(self):
        pyautogui.click()

    def play_pause(self):
        pyautogui.press('space')

    def screenshot_machen(self):
        pyautogui.hotkey('command', 'shift', '3')

    def lauter(self):
        os.system("osascript -e 'set volume output volume (output volume of (get volume settings) + 10)'")

    def leiser(self):
        os.system("osascript -e 'set volume output volume (output volume of (get volume settings) - 10)'")