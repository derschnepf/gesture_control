import cv2

def starte_kamera():
    kamera = cv2.VideoCapture(0)

    if not kamera.isOpened():
        return

    while True:
        erfolg, bild = kamera.read()

        if not erfolg:
            break

        gespiegeltes_bild = cv2.flip(bild, 1)

        cv2.imshow("Mac Webcam Test", gespiegeltes_bild)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    kamera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    starte_kamera()