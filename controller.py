import pyautogui
import os
import time

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

    def youtube_oeffnen(self):
        os.system("open -a 'Brave Browser' 'https://www.youtube.com'")

    def whatsapp_oeffnen(self):
        os.system("open -a 'WhatsApp'")

    def lauter(self):
        os.system("osascript -e 'set volume output volume (output volume of (get volume settings) + 10)'")

    def leiser(self):
        os.system("osascript -e 'set volume output volume (output volume of (get volume settings) - 10)'")

    def scroll_hoch(self):
        pyautogui.scroll(20) 

    def scroll_runter(self):
        pyautogui.scroll(-20)

    def vollbild(self):
        pyautogui.press('f')

    def app_wechseln(self, anzahl):
        pyautogui.keyDown('command')
        for _ in range(anzahl):
            pyautogui.press('tab')
            time.sleep(0.05)
        pyautogui.keyUp('command')