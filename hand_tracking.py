import cv2
import mediapipe as mp
import math
import pyautogui
import time
from collections import deque

def starte_master_steuerung():
    # 1. MediaPipe vorbereiten
    mp_hands = mp.solutions.hands
    mp_zeichnung = mp.solutions.drawing_utils
    
    hands = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.5
    )

    # 2. Kamera initialisieren (Mit Mac-Fallback für Kamera 1)
    kamera = cv2.VideoCapture(0)
    if not kamera.isOpened():
        print("⚠️ Kamera 0 nicht gefunden. Versuche Kamera 1...")
        kamera = cv2.VideoCapture(1)

    # 3. PyAutoGUI Setup
    pyautogui.FAILSAFE = False
    bildschirm_breite, bildschirm_hoehe = pyautogui.size()
    
    # 4. Variablen für Gesten
    letzte_aktion_zeit = 0
    zeigefinger_pfad = deque(maxlen=20) 
    
    print("\n🌟 JEDI MASTER MODUS AKTIVIERT 🌟")
    print("- Offene Hand: Maus bewegen (Cursor folgt deiner Handmitte)")
    print("- Pinch (Daumen + Zeigefinger): Klick")
    print("- Faust: Play / Pause (Leertaste für YouTube)")
    print("- Peace-Zeichen: Screenshot")
    print("- Nur Zeigefinger + Kreis drehen: Lautstärke (BMW-Geste)\n")

    while True:
        erfolg, bild = kamera.read()
        if not erfolg:
            # Hier bricht er ab, wenn die Kamera blockiert ist
            print("🛑 FEHLER: Die Kamera liefert kein Bild!")
            print("👉 Bitte prüfe die Mac-Systemeinstellungen (Datenschutz & Sicherheit -> Kamera).")
            print("👉 Erlaube deinem Terminal / VS Code den Zugriff.")
            break

        bild = cv2.flip(bild, 1)
        h, w, c = bild.shape
        bild_rgb = cv2.cvtColor(bild, cv2.COLOR_BGR2RGB)
        ergebnisse = hands.process(bild_rgb)

        if ergebnisse.multi_hand_landmarks:
            for hand_landmarks in ergebnisse.multi_hand_landmarks:
                # Zeichne das Skelett
                mp_zeichnung.draw_landmarks(bild, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                lm = hand_landmarks.landmark
                
                # STATUS DER FINGER PRÜFEN (Ist die Spitze höher als das Gelenk darunter?)
                zeigefinger_offen = lm[8].y < lm[6].y
                mittelfinger_offen = lm[12].y < lm[10].y
                ringfinger_offen = lm[16].y < lm[14].y
                kleiner_finger_offen = lm[20].y < lm[18].y
                
                aktuelle_zeit = time.time()
                cooldown_vorbei = (aktuelle_zeit - letzte_aktion_zeit > 1.0)
                
                # ==========================================
                # GESTE 1: DIE FAUST (Play / Pause -> YouTube Leertaste)
                # ==========================================
                if not zeigefinger_offen and not mittelfinger_offen and not ringfinger_offen and not kleiner_finger_offen:
                    if cooldown_vorbei:
                        pyautogui.press('space') # Angepasst für YouTube!
                        print("🎵 PLAY / PAUSE (Faust)")
                        cv2.putText(bild, "PLAY / PAUSE", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                        letzte_aktion_zeit = aktuelle_zeit
                        zeigefinger_pfad.clear()

                # ==========================================
                # GESTE 2: PEACE-ZEICHEN (Screenshot)
                # ==========================================
                elif zeigefinger_offen and mittelfinger_offen and not ringfinger_offen and not kleiner_finger_offen:
                    if cooldown_vorbei:
                        pyautogui.hotkey('command', 'shift', '3') 
                        print("📸 SCREENSHOT (Peace)")
                        cv2.putText(bild, "SCREENSHOT!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 3)
                        letzte_aktion_zeit = aktuelle_zeit
                        zeigefinger_pfad.clear()

                # ==========================================
                # GESTE 3: BMW KREIS-BEWEGUNG (Lautstärke)
                # ==========================================
                elif zeigefinger_offen and not mittelfinger_offen and not ringfinger_offen and not kleiner_finger_offen:
                    x, y = int(lm[8].x * w), int(lm[8].y * h)
                    zeigefinger_pfad.append((x, y))
                    
                    for i in range(1, len(zeigefinger_pfad)):
                        cv2.line(bild, zeigefinger_pfad[i-1], zeigefinger_pfad[i], (0, 255, 255), 3)
                        
                    if len(zeigefinger_pfad) == 20:
                        drehung = 0
                        for i in range(1, 18):
                            p1, p2, p3 = zeigefinger_pfad[i-1], zeigefinger_pfad[i], zeigefinger_pfad[i+1]
                            v1 = (p2[0]-p1[0], p2[1]-p1[1])
                            v2 = (p3[0]-p2[0], p3[1]-p2[1])
                            drehung += (v1[0] * v2[1] - v1[1] * v2[0])
                            
                        if drehung > 3000:
                            pyautogui.press('volumeup')
                            pyautogui.press('volumeup')
                            print("🔊 LAUTER")
                            zeigefinger_pfad.clear()
                        elif drehung < -3000:
                            pyautogui.press('volumedown')
                            pyautogui.press('volumedown')
                            print("🔉 LEISER")
                            zeigefinger_pfad.clear()

                # ==========================================
                # GESTE 4: MAUSBEWEGUNG & KLICK (Ganze Hand offen)
                # ==========================================
                else:
                    zeigefinger_pfad.clear()
                    
                    # Cursor-Bewegung an Punkt 9 (Mittelhand) binden
                    maus_anker = lm[9] 
                    maus_x = int(maus_anker.x * bildschirm_breite)
                    maus_y = int(maus_anker.y * bildschirm_hoehe)
                    pyautogui.moveTo(maus_x, maus_y)
                    
                    # Klick-Logik
                    x1, y1 = int(lm[4].x * w), int(lm[4].y * h)
                    x2, y2 = int(lm[8].x * w), int(lm[8].y * h)
                    if math.hypot(x2 - x1, y2 - y1) < 30 and (aktuelle_zeit - letzte_aktion_zeit > 0.3):
                        pyautogui.click()
                        letzte_aktion_zeit = aktuelle_zeit
                        cv2.circle(bild, ((x1+x2)//2, (y1+y2)//2), 20, (0, 255, 0), cv2.FILLED)
                        print("KLICK!")

        cv2.imshow("Jedi Master Steuerung", bild)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    kamera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    starte_master_steuerung()