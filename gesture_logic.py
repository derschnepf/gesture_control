import math
import time
from collections import deque

class GestureRecognizer:
    def __init__(self):
        self.letzte_aktion_zeit = 0
        self.zeigefinger_pfad = deque(maxlen=20)
        
    def erkenne_geste(self, hand_landmarks, w, h):
        """
        Analysiert die Handpunkte und gibt einen String (die erkannte Geste) 
        sowie eventuelle Zusatzdaten (z.B. Koordinaten) zurück.
        """
        lm = hand_landmarks.landmark
        
        # 1. Fingerstatus (True = Finger ist ausgestreckt)
        zeigefinger_offen = lm[8].y < lm[6].y
        mittelfinger_offen = lm[12].y < lm[10].y
        ringfinger_offen = lm[16].y < lm[14].y
        kleiner_finger_offen = lm[20].y < lm[18].y
        
        aktuelle_zeit = time.time()
        cooldown_vorbei = (aktuelle_zeit - self.letzte_aktion_zeit > 1.0)
        
        # ==========================================
        # GESTE 1: DIE FAUST (Play/Pause)
        # ==========================================
        if not zeigefinger_offen and not mittelfinger_offen and not ringfinger_offen and not kleiner_finger_offen:
            if cooldown_vorbei:
                self.letzte_aktion_zeit = aktuelle_zeit
                self.zeigefinger_pfad.clear()
                return "PLAY_PAUSE", None

        # ==========================================
        # GESTE 2: PEACE (Screenshot)
        # ==========================================
        elif zeigefinger_offen and mittelfinger_offen and not ringfinger_offen and not kleiner_finger_offen:
            if cooldown_vorbei:
                self.letzte_aktion_zeit = aktuelle_zeit
                self.zeigefinger_pfad.clear()
                return "SCREENSHOT", None

        # ==========================================
        # GESTE 3: BMW KREIS (Lautstärke)
        # ==========================================
        elif zeigefinger_offen and not mittelfinger_offen and not ringfinger_offen and not kleiner_finger_offen:
            x, y = int(lm[8].x * w), int(lm[8].y * h)
            self.zeigefinger_pfad.append((x, y))
            
            if len(self.zeigefinger_pfad) == 20:
                drehung = 0
                for i in range(1, 18):
                    p1, p2, p3 = self.zeigefinger_pfad[i-1], self.zeigefinger_pfad[i], self.zeigefinger_pfad[i+1]
                    v1 = (p2[0]-p1[0], p2[1]-p1[1])
                    v2 = (p3[0]-p2[0], p3[1]-p2[1])
                    drehung += (v1[0] * v2[1] - v1[1] * v2[0])
                    
                if drehung > 3000:
                    self.zeigefinger_pfad.clear()
                    return "VOLUME_UP", None
                elif drehung < -3000:
                    self.zeigefinger_pfad.clear()
                    return "VOLUME_DOWN", None
            
            # Wenn wir noch am Zeichnen sind, geben wir den Pfad zurück, damit er gemalt werden kann
            return "DRAW_PATH", self.zeigefinger_pfad

        # ==========================================
        # GESTE 4: STANDARD (Maus bewegen & Klicken)
        # ==========================================
        else:
            self.zeigefinger_pfad.clear()
            
            # Position von Punkt 9 (Handmitte) für die Mausbewegung (Werte zwischen 0 und 1)
            maus_x_ratio = lm[9].x
            maus_y_ratio = lm[9].y
            
            # Echte Pixelkoordinaten von Daumen und Zeigefinger für den Klick und das Zeichnen
            x1, y1 = int(lm[4].x * w), int(lm[4].y * h)
            x2, y2 = int(lm[8].x * w), int(lm[8].y * h)
            
            # Klick prüfen
            if math.hypot(x2 - x1, y2 - y1) < 30 and (aktuelle_zeit - self.letzte_aktion_zeit > 0.3):
                self.letzte_aktion_zeit = aktuelle_zeit
                return "CLICK", (maus_x_ratio, maus_y_ratio, x1, y1, x2, y2)
                
            # Wenn nicht geklickt wird, einfach bewegen
            return "MOVE", (maus_x_ratio, maus_y_ratio)
            
        return "NONE", None