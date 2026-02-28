import cv2
import mediapipe as mp
import math
import pyautogui
import time  # NEU: Für den Klick-Cooldown

def starte_jedi_maus():
    mp_hands = mp.solutions.hands
    mp_zeichnung = mp.solutions.drawing_utils
    
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )

    kamera = cv2.VideoCapture(0)
    
    # ==========================================
    # NEU: PYAUTOGUI SETUP
    # ==========================================
    pyautogui.FAILSAFE = False  # Verhindert einen Skript-Absturz, wenn die Maus in die Bildschirmecke geht
    bildschirm_breite, bildschirm_hoehe = pyautogui.size()
    letzter_klick_zeit = 0      # Speichert, wann zuletzt geklickt wurde
    
    print("Jedi-Maus aktiviert! Bewege deinen Zeigefinger, um den Cursor zu steuern.")
    print("Kneife Daumen und Zeigefinger zusammen, um zu klicken.")

    while True:
        erfolg, bild = kamera.read()
        if not erfolg:
            break

        bild = cv2.flip(bild, 1)
        bild_rgb = cv2.cvtColor(bild, cv2.COLOR_BGR2RGB)
        ergebnisse = hands.process(bild_rgb)

        if ergebnisse.multi_hand_landmarks:
            for hand_landmarks in ergebnisse.multi_hand_landmarks:
                mp_zeichnung.draw_landmarks(bild, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # 1. Bildgröße auslesen
                h, w, c = bild.shape
                
                # 2. Daumen und Zeigefinger isolieren
                daumen = hand_landmarks.landmark[4]
                zeigefinger = hand_landmarks.landmark[8]
                
                # 3. Kamera-Koordinaten berechnen
                x1, y1 = int(daumen.x * w), int(daumen.y * h)
                x2, y2 = int(zeigefinger.x * w), int(zeigefinger.y * h)
                
                # ==========================================
                # NEU: MAUS BEWEGEN
                # ==========================================
                # Wir rechnen die Position des Zeigefingers auf deine echte Bildschirmgröße um
                maus_x = int(zeigefinger.x * bildschirm_breite)
                maus_y = int(zeigefinger.y * bildschirm_hoehe)
                
                # Bewege die echte Mac-Maus!
                pyautogui.moveTo(maus_x, maus_y)
                
                # 4. Abstand für den Klick berechnen
                abstand = math.hypot(x2 - x1, y2 - y1)
                
                # 5. Die echte Klick-Logik
                if abstand < 30:
                    aktuelle_zeit = time.time()
                    
                    # Cooldown: Nur klicken, wenn der letzte Klick mehr als 0.5 Sekunden her ist
                    if aktuelle_zeit - letzter_klick_zeit > 0.5:
                        pyautogui.click()
                        letzter_klick_zeit = aktuelle_zeit
                        
                        # Visuelles Feedback im Kamera-Bild
                        mitte_x, mitte_y = (x1 + x2) // 2, (y1 + y2) // 2
                        cv2.circle(bild, (mitte_x, mitte_y), 15, (0, 255, 0), cv2.FILLED)
                        print("ECHTER MAC-KLICK!")

        cv2.imshow("Jedi Hand Tracking", bild)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    kamera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    starte_jedi_maus()