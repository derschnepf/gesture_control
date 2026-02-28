import cv2

def starte_kamera():
    """
    Öffnet die Standard-Webcam, zeigt das Live-Bild an und 
    schließt sich wieder, wenn die Taste 'q' gedrückt wird.
    """
    # 1. Kamera initialisieren. 
    # Die '0' steht für die Standardkamera (meist die eingebaute Webcam im Mac).
    # Falls du eine externe Kamera nutzt, könnte es eine '1' oder '2' sein.
    kamera = cv2.VideoCapture(0)

    # Sicherheitscheck: Hat der Zugriff geklappt?
    if not kamera.isOpened():
        print("FEHLER: Konnte nicht auf die Kamera zugreifen.")
        return

    print("Kamera erfolgreich gestartet!")
    print("Drücke die Taste 'q' auf deiner Tastatur, um das Fenster zu schließen.")

    # 2. Die Video-Schleife (Ein Video ist ja nur eine schnelle Abfolge von Bildern)
    while True:
        # Ein einzelnes Bild (Frame) von der Kamera lesen
        # 'erfolg' ist True oder False, 'bild' enthält die tatsächlichen Pixeldaten
        erfolg, bild = kamera.read()

        if not erfolg:
            print("FEHLER: Konnte kein Bild abrufen.")
            break

        # 3. Das Bild spiegeln (Optional, aber extrem wichtig für die Benutzerfreundlichkeit!)
        # Ohne Spiegelung ist rechts auf dem Bildschirm links, was unser Gehirn verwirrt.
        # Die '1' bedeutet: Horizontal spiegeln.
        gespiegeltes_bild = cv2.flip(bild, 1)

        # 4. Das Bild in einem neuen Fenster anzeigen
        cv2.imshow("Mac Webcam Test", gespiegeltes_bild)

        # 5. Abbruchbedingung
        # Wir warten 1 Millisekunde auf einen Tastendruck.
        # Wenn die gedrückte Taste ein 'q' ist, brechen wir die Endlosschleife ab.
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Beende Kamera...")
            break

    # 6. Aufräumen (Sehr wichtig, sonst bleibt die grüne Kamera-LED am Mac an!)
    kamera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    starte_kamera()