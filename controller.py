import pyautogui

class MacController:
    def __init__(self):
        # Sicherheitsfunktion von PyAutoGUI deaktivieren, damit es am Rand nicht abstürzt
        pyautogui.FAILSAFE = False
        # Bildschirmgröße einmalig beim Start auslesen
        self.bildschirm_breite, self.bildschirm_hoehe = pyautogui.size()

    def maus_bewegen(self, x_ratio, y_ratio):
        """Bewegt die echte Mac-Maus. Erwartet Werte zwischen 0.0 und 1.0"""
        maus_x = int(x_ratio * self.bildschirm_breite)
        maus_y = int(y_ratio * self.bildschirm_hoehe)
        pyautogui.moveTo(maus_x, maus_y)

    def klicken(self):
        pyautogui.click()

    def play_pause(self):
        pyautogui.press('space') # Für YouTube

    def screenshot_machen(self):
        pyautogui.hotkey('command', 'shift', '3')

    def lauter(self):
        pyautogui.press('volumeup')
        pyautogui.press('volumeup') # Doppelt für stärkeren Effekt

    def leiser(self):
        pyautogui.press('volumedown')
        pyautogui.press('volumedown')