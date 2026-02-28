import cv2
import mediapipe as mp

# Wir importieren unsere eigenen neuen Module!
from gesture_logic import GestureRecognizer
from controller import MacController

def starte_master_steuerung():
    mp_hands = mp.solutions.hands
    mp_zeichnung = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        static_image_mode=False, max_num_hands=1,
        min_detection_confidence=0.7, min_tracking_confidence=0.5
    )

    kamera = cv2.VideoCapture(0)
    if not kamera.isOpened():
        print("⚠️ Kamera 0 nicht gefunden. Versuche Kamera 1...")
        kamera = cv2.VideoCapture(1)

    # Unsere Helfer aktivieren
    erkennung = GestureRecognizer()
    mac = MacController()
    
    print("\n🌟 CLEAN CODE MODUS AKTIVIERT 🌟")
    print("Alle Gesten sind geladen. Projekt ist modular aufgebaut!\n")

    while True:
        erfolg, bild = kamera.read()
        if not erfolg:
            print("🛑 FEHLER: Die Kamera liefert kein Bild!")
            break

        bild = cv2.flip(bild, 1)
        h, w, c = bild.shape
        bild_rgb = cv2.cvtColor(bild, cv2.COLOR_BGR2RGB)
        ergebnisse = hands.process(bild_rgb)

        if ergebnisse.multi_hand_landmarks:
            for hand_landmarks in ergebnisse.multi_hand_landmarks:
                # 1. Skelett zeichnen
                mp_zeichnung.draw_landmarks(bild, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # 2. Das "Gehirn" fragen, welche Geste gemacht wird
                geste, daten = erkennung.erkenne_geste(hand_landmarks, w, h)
                
                # 3. Den Mac steuern & Feedback ins Bild zeichnen
                if geste == "PLAY_PAUSE":
                    mac.play_pause()
                    print("🎵 PLAY / PAUSE (Faust)")
                    cv2.putText(bild, "PLAY / PAUSE", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                    
                elif geste == "SCREENSHOT":
                    mac.screenshot_machen()
                    print("📸 SCREENSHOT (Peace)")
                    cv2.putText(bild, "SCREENSHOT!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 3)
                    
                elif geste == "VOLUME_UP":
                    mac.lauter()
                    print("🔊 LAUTER")
                    
                elif geste == "VOLUME_DOWN":
                    mac.leiser()
                    print("🔉 LEISER")
                    
                elif geste == "DRAW_PATH":
                    # Zeichnet die gelbe Linie für die BMW Geste
                    pfad = daten
                    for i in range(1, len(pfad)):
                        cv2.line(bild, pfad[i-1], pfad[i], (0, 255, 255), 3)
                        
                elif geste == "CLICK":
                    mx, my, x1, y1, x2, y2 = daten
                    mac.maus_bewegen(mx, my)
                    mac.klicken()
                    print("KLICK!")
                    cv2.circle(bild, ((x1+x2)//2, (y1+y2)//2), 20, (0, 255, 0), cv2.FILLED)
                    
                elif geste == "MOVE":
                    mx, my = daten
                    mac.maus_bewegen(mx, my)

        cv2.imshow("Jedi Master Steuerung", bild)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    kamera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    starte_master_steuerung()