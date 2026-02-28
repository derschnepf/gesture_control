import math
import time

class GestureRecognizer:
    def __init__(self):
        self.letzte_aktion_zeit = 0
        self.start_y = None 
        
    def erkenne_geste(self, hand_landmarks, w, h):
        lm = hand_landmarks.landmark
        
        zeigefinger_offen = lm[8].y < lm[6].y
        mittelfinger_offen = lm[12].y < lm[10].y
        ringfinger_offen = lm[16].y < lm[14].y
        kleiner_finger_offen = lm[20].y < lm[18].y
        
        aktuelle_zeit = time.time()
        cooldown_vorbei = (aktuelle_zeit - self.letzte_aktion_zeit > 1.0)
        
        ist_lautstaerke_geste = zeigefinger_offen and not mittelfinger_offen and not ringfinger_offen and not kleiner_finger_offen
        if not ist_lautstaerke_geste:
            self.start_y = None

        if not zeigefinger_offen and not mittelfinger_offen and not ringfinger_offen and not kleiner_finger_offen:
            if cooldown_vorbei:
                self.letzte_aktion_zeit = aktuelle_zeit
                return "PLAY_PAUSE", None

        elif zeigefinger_offen and mittelfinger_offen and not ringfinger_offen and not kleiner_finger_offen:
            if cooldown_vorbei:
                self.letzte_aktion_zeit = aktuelle_zeit
                return "SCREENSHOT", None

        elif ist_lautstaerke_geste:
            aktuelle_y_position = lm[8].y
            
            if self.start_y is None:
                self.start_y = aktuelle_y_position
                return "DRAW_SLIDER", (int(lm[8].x * w), int(lm[8].y * h))
                
            differenz = self.start_y - aktuelle_y_position
            
            if differenz > 0.04: 
                self.start_y = aktuelle_y_position
                return "VOLUME_UP", (int(lm[8].x * w), int(lm[8].y * h))
                
            elif differenz < -0.04:
                self.start_y = aktuelle_y_position
                return "VOLUME_DOWN", (int(lm[8].x * w), int(lm[8].y * h))
                
            return "DRAW_SLIDER", (int(lm[8].x * w), int(lm[8].y * h))

        else:
            maus_x_ratio = lm[9].x
            maus_y_ratio = lm[9].y
            
            x1, y1 = int(lm[4].x * w), int(lm[4].y * h)
            x2, y2 = int(lm[8].x * w), int(lm[8].y * h)
            
            if math.hypot(x2 - x1, y2 - y1) < 30 and (aktuelle_zeit - self.letzte_aktion_zeit > 0.3):
                self.letzte_aktion_zeit = aktuelle_zeit
                return "CLICK", (maus_x_ratio, maus_y_ratio, x1, y1, x2, y2)
                
            return "MOVE", (maus_x_ratio, maus_y_ratio)
            
        return "NONE", None