import cv2
import mediapipe as mp
import pyautogui
import os
import time
from gesture_logic import GestureRecognizer

def main():
    pyautogui.FAILSAFE = False
    screen_w, screen_h = pyautogui.size()
    
    mp_hands = mp.solutions.hands
    mp_zeichnung = mp.solutions.drawing_utils
    hands = mp_hands.Hands(
        max_num_hands=2, 
        min_detection_confidence=0.7, 
        min_tracking_confidence=0.7
    )
    
    recognizer = GestureRecognizer()
    kamera = cv2.VideoCapture(0)
    cmd_gedrueckt = False

    while True:
        erfolg, bild = kamera.read()
        if not erfolg:
            break
            
        bild = cv2.flip(bild, 1)
        h, w, _ = bild.shape
        bild_rgb = cv2.cvtColor(bild, cv2.COLOR_BGR2RGB)
        
        ergebnisse = hands.process(bild_rgb)
        
        if ergebnisse.multi_hand_landmarks:
            for hand_landmarks in ergebnisse.multi_hand_landmarks:
                mp_zeichnung.draw_landmarks(bild, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
            geste, daten = recognizer.erkenne_geste(ergebnisse.multi_hand_landmarks, w, h)
            
            if geste == "APP_SWITCH":
                if not cmd_gedrueckt:
                    pyautogui.keyDown('command')
                    pyautogui.press('tab')
                    cmd_gedrueckt = True
                    time.sleep(0.2)
                else:
                    pyautogui.press('tab')
            elif cmd_gedrueckt and geste != "WAITING":
                pyautogui.keyUp('command')
                cmd_gedrueckt = False
            
            if geste == "MOVE":
                x, y = daten
                pyautogui.moveTo(x * screen_w, y * screen_h, _pause=False)
            elif geste == "CLICK":
                pyautogui.click()
                
            elif geste == "PLAY_PAUSE":
                pyautogui.press('space')
            elif geste == "FULLSCREEN":
                pyautogui.press('f')
            elif geste == "ROCK":
                os.system('open -a "WhatsApp"') 
                time.sleep(1)
            elif geste == "YOUTUBE":
                os.system('open -a "Brave Browser" "https://www.youtube.com"')
                time.sleep(1)
                
            elif geste == "VIDEO_FORWARD":
                pyautogui.press('right')
            elif geste == "VIDEO_BACKWARD":
                pyautogui.press('left')
            elif geste == "VOLUME_UP":
                os.system("osascript -e 'set volume output volume ((output volume of (get volume settings)) + 5)'")
            elif geste == "VOLUME_DOWN":
                os.system("osascript -e 'set volume output volume ((output volume of (get volume settings)) - 5)'")
            elif geste == "SCROLL_UP":
                pyautogui.scroll(10)
            elif geste == "SCROLL_DOWN":
                pyautogui.scroll(-10)
                
            elif geste == "LOCK_SCREEN":
                os.system('''osascript -e 'tell application "System Events" to keystroke "q" using {control down, command down}' ''')
                time.sleep(1)
                
            elif geste == "DRAW_DUAL_SLIDER":
                x_pos, y_pos, _ = daten
                cv2.putText(bild, "Lautstaerke", (x_pos, y_pos - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                cv2.circle(bild, (x_pos, y_pos), 15, (255, 0, 0), cv2.FILLED)
            elif geste == "DRAW_SCROLL_SLIDER":
                x_pos, y_pos, _ = daten
                cv2.putText(bild, "Scrollen", (x_pos, y_pos - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.circle(bild, (x_pos, y_pos), 15, (0, 255, 0), cv2.FILLED)
            elif geste == "DRAW_SCRUB_SLIDER":
                x_pos, y_pos, _ = daten
                cv2.putText(bild, "Spulen", (x_pos, y_pos - 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                cv2.circle(bild, (x_pos, y_pos), 15, (0, 0, 255), cv2.FILLED)
            
            if geste not in ["NONE", "WAITING", "MOVE"] and not str(geste).startswith("DRAW"):
                cv2.putText(bild, f"Aktion: {geste}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        else:
            if cmd_gedrueckt:
                pyautogui.keyUp('command')
                cmd_gedrueckt = False

        if recognizer.letzte_ki_vorhersage:
            cv2.putText(bild, recognizer.letzte_ki_vorhersage, (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.imshow("Jedi Control Center", bild)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    if cmd_gedrueckt:
        pyautogui.keyUp('command')
    kamera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()