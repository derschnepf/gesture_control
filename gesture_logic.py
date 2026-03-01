import math
import time
from collections import deque

class GestureRecognizer:
    def __init__(self):
        self.letzte_aktion_zeit = 0
        self.start_y = None
        self.maus_historie = deque(maxlen=5) 
        
    def _ist_finger_offen(self, lm, spitze, gelenk):
        return lm[spitze].y < lm[gelenk].y

    def erkenne_geste(self, multi_hand_landmarks, w, h):
        aktuelle_zeit = time.time()
        cooldown_vorbei = (aktuelle_zeit - self.letzte_aktion_zeit > 1.0)

        if len(multi_hand_landmarks) == 2:
            hand1 = multi_hand_landmarks[0].landmark
            hand2 = multi_hand_landmarks[1].landmark

            if hand1[0].x < hand2[0].x:
                linke_hand, rechte_hand = hand1, hand2
            else:
                linke_hand, rechte_hand = hand2, hand1


            links_nur_zeige = self._ist_finger_offen(linke_hand, 8, 6) and not self._ist_finger_offen(linke_hand, 12, 10) and not self._ist_finger_offen(linke_hand, 16, 14) and not self._ist_finger_offen(linke_hand, 20, 18)
            links_zeige_und_mittel = self._ist_finger_offen(linke_hand, 8, 6) and self._ist_finger_offen(linke_hand, 12, 10) and not self._ist_finger_offen(linke_hand, 16, 14) and not self._ist_finger_offen(linke_hand, 20, 18)
            

            rechts_nur_zeige = self._ist_finger_offen(rechte_hand, 8, 6) and not self._ist_finger_offen(rechte_hand, 12, 10) and not self._ist_finger_offen(rechte_hand, 16, 14) and not self._ist_finger_offen(rechte_hand, 20, 18)

            if links_nur_zeige and rechts_nur_zeige:
                aktuelle_y_position = rechte_hand[8].y 
                
                if self.start_y is None:
                    self.start_y = aktuelle_y_position
                    return "DRAW_DUAL_SLIDER", (int(rechte_hand[8].x * w), int(rechte_hand[8].y * h), aktuelle_y_position)
                    
                differenz = self.start_y - aktuelle_y_position
                
                if differenz > 0.04: 
                    self.start_y = aktuelle_y_position
                    return "VOLUME_UP", (int(rechte_hand[8].x * w), int(rechte_hand[8].y * h), aktuelle_y_position)
                elif differenz < -0.04:
                    self.start_y = aktuelle_y_position
                    return "VOLUME_DOWN", (int(rechte_hand[8].x * w), int(rechte_hand[8].y * h), aktuelle_y_position)
                    
                return "DRAW_DUAL_SLIDER", (int(rechte_hand[8].x * w), int(rechte_hand[8].y * h), aktuelle_y_position)
            
            elif links_zeige_und_mittel and rechts_nur_zeige:
                aktuelle_y_position = rechte_hand[8].y 
                
                if self.start_y is None:
                    self.start_y = aktuelle_y_position
                    return "DRAW_SCROLL_SLIDER", (int(rechte_hand[8].x * w), int(rechte_hand[8].y * h), aktuelle_y_position)
                    
                differenz = self.start_y - aktuelle_y_position
                
                if differenz > 0.04:  
                    self.start_y = aktuelle_y_position
                    return "SCROLL_UP", (int(rechte_hand[8].x * w), int(rechte_hand[8].y * h), aktuelle_y_position)
                elif differenz < -0.04: 
                    self.start_y = aktuelle_y_position
                    return "SCROLL_DOWN", (int(rechte_hand[8].x * w), int(rechte_hand[8].y * h), aktuelle_y_position)
                    
                return "DRAW_SCROLL_SLIDER", (int(rechte_hand[8].x * w), int(rechte_hand[8].y * h), aktuelle_y_position)
                
            self.start_y = None
            return "NONE", None

        elif len(multi_hand_landmarks) == 1:
            self.start_y = None
            lm = multi_hand_landmarks[0].landmark
            
            zeigefinger_offen = self._ist_finger_offen(lm, 8, 6)
            mittelfinger_offen = self._ist_finger_offen(lm, 12, 10)
            ringfinger_offen = self._ist_finger_offen(lm, 16, 14)
            kleiner_finger_offen = self._ist_finger_offen(lm, 20, 18)
            
            daumen_offen = abs(lm[4].x - lm[9].x) > abs(lm[3].x - lm[9].x)

            if not zeigefinger_offen and not mittelfinger_offen and not ringfinger_offen and not kleiner_finger_offen:
                if cooldown_vorbei:
                    self.letzte_aktion_zeit = aktuelle_zeit
                    return "PLAY_PAUSE", None

            elif daumen_offen and not zeigefinger_offen and not mittelfinger_offen and not ringfinger_offen and kleiner_finger_offen:
                if cooldown_vorbei:
                    self.letzte_aktion_zeit = aktuelle_zeit
                    return "YOUTUBE", None

            elif zeigefinger_offen and not mittelfinger_offen and not ringfinger_offen and kleiner_finger_offen:
                if cooldown_vorbei:
                    self.letzte_aktion_zeit = aktuelle_zeit
                    return "ROCK", None

            else:
                maus_x_ratio = lm[9].x
                maus_y_ratio = lm[9].y
                
                self.maus_historie.append((maus_x_ratio, maus_y_ratio))
                avg_x = sum([pos[0] for pos in self.maus_historie]) / len(self.maus_historie)
                avg_y = sum([pos[1] for pos in self.maus_historie]) / len(self.maus_historie)
                
                x1, y1 = int(lm[4].x * w), int(lm[4].y * h)
                x2, y2 = int(lm[8].x * w), int(lm[8].y * h)
                
                if math.hypot(x2 - x1, y2 - y1) < 30 and (aktuelle_zeit - self.letzte_aktion_zeit > 0.3):
                    self.letzte_aktion_zeit = aktuelle_zeit
                    return "CLICK", (avg_x, avg_y, x1, y1, x2, y2) 
                    
                return "MOVE", (avg_x, avg_y) 
            
        return "NONE", None