import cv2
import mediapipe as mp

from gesture_logic import GestureRecognizer
from controller import MacController

def starte_master_steuerung():
    mp_hands = mp.solutions.hands
    mp_zeichnung = mp.solutions.drawing_utils
    
    hands = mp_hands.Hands(
        static_image_mode=False, max_num_hands=2,
        min_detection_confidence=0.7, min_tracking_confidence=0.5
    )

    kamera = cv2.VideoCapture(0)
    if not kamera.isOpened():
        kamera = cv2.VideoCapture(1)

    erkennung = GestureRecognizer()
    mac = MacController()
    

    while True:
        erfolg, bild = kamera.read()
        if not erfolg:
            break

        bild = cv2.flip(bild, 1)
        h, w, c = bild.shape
        bild_rgb = cv2.cvtColor(bild, cv2.COLOR_BGR2RGB)
        
        rand_x = int(w * 0.2)
        rand_y = int(h * 0.2)
        cv2.rectangle(bild, (rand_x, rand_y), (w - rand_x, h - rand_y), (150, 150, 150), 2)

        ergebnisse = hands.process(bild_rgb)

        if ergebnisse.multi_hand_landmarks:
            for hand_landmarks in ergebnisse.multi_hand_landmarks:
                mp_zeichnung.draw_landmarks(bild, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
            geste, daten = erkennung.erkenne_geste(ergebnisse.multi_hand_landmarks, w, h)
            
            if geste == "WAITING":
                ziel_geste, zusatz_daten = daten
                if ziel_geste == "APP_SWITCH":
                    cv2.putText(bild, f"Lade Wechsel ({zusatz_daten} Apps)...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
                else:
                    cv2.putText(bild, f"Lade {ziel_geste}...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
            
            elif geste == "APP_SWITCH":
                anzahl = daten
                mac.app_wechseln(anzahl)
                cv2.putText(bild, f"APP WECHSEL ({anzahl})", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 100, 255), 3)

            elif geste == "EATING_MODE":
                x, y = daten
                cv2.circle(bild, (x, y), 25, (0, 0, 255), cv2.FILLED)
                cv2.line(bild, (x - 15, y), (x + 15, y), (255, 255, 255), 4)
                cv2.putText(bild, "STANDBY", (x - 40, y - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            elif geste == "PLAY_PAUSE":
                mac.play_pause()
                cv2.putText(bild, "PLAY / PAUSE", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                
            elif geste == "FULLSCREEN":
                mac.vollbild()
                cv2.putText(bild, "VOLLBILD!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 255), 3)

            elif geste == "YOUTUBE":
                mac.youtube_oeffnen()
                cv2.putText(bild, "YOUTUBE GEÖFFNET!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
                
            elif geste == "ROCK":
                mac.whatsapp_oeffnen()
                cv2.putText(bild, "WHATSAPP GEÖFFNET!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3)
                
            elif geste in ["VOLUME_UP", "VOLUME_DOWN", "DRAW_DUAL_SLIDER"]:
                x, y, y_ratio = daten
                if geste == "VOLUME_UP":
                    mac.lauter()
                    cv2.circle(bild, (x, y), 20, (0, 255, 0), cv2.FILLED) 
                elif geste == "VOLUME_DOWN":
                    mac.leiser()
                    cv2.circle(bild, (x, y), 20, (0, 0, 255), cv2.FILLED)
                else:
                    cv2.circle(bild, (x, y), 15, (0, 255, 255), cv2.FILLED)

                cv2.rectangle(bild, (50, int(h/4)), (85, int(h*3/4)), (255, 255, 255), 3)
                fuell_prozent = max(0, min(1, 1.0 - y_ratio))
                balken_start_y = int(h*3/4)
                balken_ende_y = int(h/4)
                balken_aktuelle_y = int(balken_start_y - fuell_prozent * (balken_start_y - balken_ende_y))
                cv2.rectangle(bild, (50, balken_aktuelle_y), (85, balken_start_y), (0, 255, 0), cv2.FILLED)
                cv2.putText(bild, "VOL", (45, balken_start_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
            elif geste in ["SCROLL_UP", "SCROLL_DOWN", "DRAW_SCROLL_SLIDER"]:
                x, y, y_ratio = daten
                if geste == "SCROLL_UP":
                    mac.scroll_hoch()
                    cv2.circle(bild, (x, y), 20, (255, 0, 0), cv2.FILLED) 
                elif geste == "SCROLL_DOWN":
                    mac.scroll_runter()
                    cv2.circle(bild, (x, y), 20, (255, 100, 100), cv2.FILLED) 
                else:
                    cv2.circle(bild, (x, y), 15, (255, 200, 0), cv2.FILLED) 
                
                cv2.rectangle(bild, (w - 85, int(h/4)), (w - 50, int(h*3/4)), (255, 255, 255), 3)
                fuell_prozent = max(0, min(1, 1.0 - y_ratio))
                balken_start_y = int(h*3/4)
                balken_ende_y = int(h/4)
                balken_aktuelle_y = int(balken_start_y - fuell_prozent * (balken_start_y - balken_ende_y))
                cv2.rectangle(bild, (w - 85, balken_aktuelle_y), (w - 50, balken_start_y), (255, 0, 0), cv2.FILLED)
                cv2.putText(bild, "SCR", (w - 90, balken_start_y + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            elif geste == "CLICK":
                mx, my, x1, y1, x2, y2 = daten
                mac.maus_bewegen(mx, my)
                mac.klicken()
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