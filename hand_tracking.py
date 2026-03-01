import cv2
import mediapipe as mp
import threading
import rumps

from gesture_logic import GestureRecognizer
from controller import MacController

class JediApp(rumps.App):
    def __init__(self):
        super(JediApp, self).__init__("🖐️ Jedi")
        
        self.erkennung = GestureRecognizer()
        self.mac = MacController()
        
        self.is_running = False
        self.kamera_thread = None

    @rumps.clicked("▶️ Kamera AN")
    def start_kamera(self, _):
        if not self.is_running:
            self.is_running = True
            self.kamera_thread = threading.Thread(target=self.kamera_loop)
            self.kamera_thread.start()
            self.title = "🟢 Jedi"
            rumps.notification("Jedi Steuerung", "Aktiviert", "Die Handsteuerung läuft jetzt unsichtbar im Hintergrund.")

    @rumps.clicked("⏹️ Kamera AUS")
    def stop_kamera(self, _):
        if self.is_running:
            self.is_running = False
            if self.kamera_thread:
                self.kamera_thread.join()
            self.title = "🖐️ Jedi"
            rumps.notification("Jedi Steuerung", "Deaktiviert", "Die Kamera wurde gestoppt.")

    def kamera_loop(self):
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands(
            static_image_mode=False, max_num_hands=2,
            min_detection_confidence=0.7, min_tracking_confidence=0.5
        )

        kamera = cv2.VideoCapture(0)
        if not kamera.isOpened():
            kamera = cv2.VideoCapture(1)


        while self.is_running:
            erfolg, bild = kamera.read()
            if not erfolg:
                break

            bild = cv2.flip(bild, 1)
            h, w, c = bild.shape
            bild_rgb = cv2.cvtColor(bild, cv2.COLOR_BGR2RGB)
            ergebnisse = hands.process(bild_rgb)

            if ergebnisse.multi_hand_landmarks:
                geste, daten = self.erkennung.erkenne_geste(ergebnisse.multi_hand_landmarks, w, h)
                

                if geste == "APP_SWITCH":
                    self.mac.app_wechseln(daten)
                elif geste == "PLAY_PAUSE":
                    self.mac.play_pause()
                elif geste == "FULLSCREEN":
                    self.mac.vollbild()
                elif geste == "YOUTUBE":
                    self.mac.youtube_oeffnen()
                elif geste == "ROCK":
                    self.mac.whatsapp_oeffnen()
                elif geste == "VOLUME_UP":
                    self.mac.lauter()
                elif geste == "VOLUME_DOWN":
                    self.mac.leiser()
                elif geste == "SCROLL_UP":
                    self.mac.scroll_hoch()
                elif geste == "SCROLL_DOWN":
                    self.mac.scroll_runter()
                elif geste == "CLICK":
                    mx, my, x1, y1, x2, y2 = daten
                    self.mac.maus_bewegen(mx, my)
                    self.mac.klicken()
                elif geste == "MOVE":
                    mx, my = daten
                    self.mac.maus_bewegen(mx, my)

        kamera.release()
        hands.close()

if __name__ == "__main__":

    app = JediApp()
    app.run()