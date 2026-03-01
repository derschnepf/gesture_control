import math
import time
from collections import deque

class GestureRecognizer:
    def __init__(self):
        self.letzte_aktion_zeit = 0
        self.start_y = None
        self.maus_historie = deque(maxlen=7) 
        
        self.aktuelle_geste = None
        self.gesten_start_zeit = 0
        
    def _ist_finger_offen(self, lm, spitze, gelenk):
        return lm[spitze].y < lm[gelenk].y

    def erkenne_geste(self, multi_hand_landmarks, w, h):
        aktuelle_zeit = time.time()
        cooldown_vorbei = (aktuelle_zeit - self.letzte_aktion_zeit > 1.0)
        
        erkannte_pose = "NONE"
        pose_daten = None

        if len(multi_hand_landmarks) == 2:
            hand1 = multi_hand_landmarks[0].landmark
            hand2 = multi_hand_landmarks[1].landmark

            if hand1[0].x < hand2[0].x:
                linke_hand, rechte_hand = hand1, hand2
            else:
                linke_hand, rechte_hand = hand2, hand1

            links_zeige = self._ist_finger_offen(linke_hand, 8, 6)
            links_mittel = self._ist_finger_offen(linke_hand, 12, 10)
            links_ring = self._ist_finger_offen(linke_hand, 16, 14)
            links_klein = self._ist_finger_offen(linke_hand, 20, 18)
            
            links_nur_zeige = links_zeige and not links_mittel and not links_ring and not links_klein
            links_zeige_und_mittel = links_zeige and links_mittel and not links_ring and not links_klein
            links_alle_offen = links_zeige and links_mittel and links_ring and links_klein
            
            rechts_zeige = self._ist_finger_offen(rechte_hand, 8, 6)
            rechts_mittel = self._ist_finger_offen(rechte_hand, 12, 10)
            rechts_ring = self._ist_finger_offen(rechte_hand, 16, 14)
            rechts_klein = self._ist_finger_offen(rechte_hand, 20, 18)
            rechts_daumen = abs(rechte_hand[4].x - rechte_hand[9].x) > abs(rechte_hand[3].x - rechte_hand[9].x)
            
            rechts_nur_zeige = rechts_zeige and not rechts_mittel and not rechts_ring and not rechts_klein

            if links_nur_zeige and rechts_nur_zeige:
                self.aktuelle_geste = None 
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
                self.aktuelle_geste = None 
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
            
            elif links_alle_offen:
                anzahl_finger = [rechts_zeige, rechts_mittel, rechts_ring, rechts_klein, rechts_daumen].count(True)
                if anzahl_finger > 0:
                    erkannte_pose = "APP_SWITCH"
                    pose_daten = anzahl_finger
            
            if erkannte_pose == "NONE":
                self.start_y = None
                return "NONE", None

        elif len(multi_hand_landmarks) == 1:
            self.start_y = None
            lm = multi_hand_landmarks[0].landmark
            
            handgelenk_y = lm[0].y
            mittelhand_y = lm[9].y
            ist_hand_aufrecht = (handgelenk_y - mittelhand_y) > 0.12 
            
            if not ist_hand_aufrecht:
                self.aktuelle_geste = None 
                return "EATING_MODE", (int(lm[9].x * w), int(lm[9].y * h))

            zeigefinger_offen = self._ist_finger_offen(lm, 8, 6)
            mittelfinger_offen = self._ist_finger_offen(lm, 12, 10)
            ringfinger_offen = self._ist_finger_offen(lm, 16, 14)
            kleiner_finger_offen = self._ist_finger_offen(lm, 20, 18)
            daumen_abgespreizt = abs(lm[4].x - lm[9].x) > abs(lm[3].x - lm[9].x)
            daumen_zeigt_hoch = daumen_abgespreizt and (lm[4].y < (lm[5].y - 0.02))

            if not daumen_abgespreizt and not zeigefinger_offen and not mittelfinger_offen and not ringfinger_offen and not kleiner_finger_offen:
                erkannte_pose = "PLAY_PAUSE"
            elif daumen_zeigt_hoch and not zeigefinger_offen and not mittelfinger_offen and not ringfinger_offen and not kleiner_finger_offen:
                erkannte_pose = "FULLSCREEN"
            elif daumen_abgespreizt and not zeigefinger_offen and not mittelfinger_offen and not ringfinger_offen and kleiner_finger_offen:
                erkannte_pose = "YOUTUBE"
            elif zeigefinger_offen and not mittelfinger_offen and not ringfinger_offen and kleiner_finger_offen:
                erkannte_pose = "ROCK"

            if erkannte_pose == "NONE":
                self.aktuelle_geste = None 
                
                rand = 0.2
                nutzbare_breite = 1.0 - (2 * rand) 
                nutzbare_hoehe = 1.0 - (2 * rand)
                
                raw_x = (lm[9].x - rand) / nutzbare_breite
                raw_y = (lm[9].y - rand) / nutzbare_hoehe
                ziel_x = max(0.0, min(1.0, raw_x))
                ziel_y = max(0.0, min(1.0, raw_y))
                
                self.maus_historie.append((ziel_x, ziel_y))
                avg_x = sum([pos[0] for pos in self.maus_historie]) / len(self.maus_historie)
                avg_y = sum([pos[1] for pos in self.maus_historie]) / len(self.maus_historie)
                
                x1, y1 = int(lm[4].x * w), int(lm[4].y * h)
                x2, y2 = int(lm[8].x * w), int(lm[8].y * h)
                
                if math.hypot(x2 - x1, y2 - y1) < 30 and (aktuelle_zeit - self.letzte_aktion_zeit > 0.3):
                    self.letzte_aktion_zeit = aktuelle_zeit
                    return "CLICK", (avg_x, avg_y, x1, y1, x2, y2) 
                    
                return "MOVE", (avg_x, avg_y) 

        if erkannte_pose != "NONE":
            ziel_wartezeit = 0.05 if erkannte_pose == "PLAY_PAUSE" else 0.6
            
            if self.aktuelle_geste != erkannte_pose:
                self.aktuelle_geste = erkannte_pose
                self.gesten_start_zeit = aktuelle_zeit
                return "WAITING", (erkannte_pose, pose_daten) 
            else:
                wartezeit = aktuelle_zeit - self.gesten_start_zeit
                if wartezeit >= ziel_wartezeit: 
                    if cooldown_vorbei:
                        self.letzte_aktion_zeit = aktuelle_zeit
                        self.aktuelle_geste = None 
                        return erkannte_pose, pose_daten 
                
                return "WAITING", (erkannte_pose, pose_daten) 
            
        return "NONE", None