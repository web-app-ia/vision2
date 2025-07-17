import cv2
import numpy as np
import time
import os
import HandTrackingModule as htm

#######################
brushThickness = 25
eraserThickness = 50
########################

folderPath = "Header"
myList = os.listdir(folderPath)
print(myList)
overlayList = []
for imPath in myList:
    image = cv2.imread(f'{folderPath}/{imPath}')
    overlayList.append(image)
print(len(overlayList))
header = overlayList[0]
drawColor = (0, 0, 255)  # Rouge par défaut
isEraser = False

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

# Check if camera is opened
if not cap.isOpened():
    print("Error: Could not open camera")
    exit()

detector = htm.handDetector(detectionCon=0.65, maxHands=1)
xp, yp = 0, 0
imgCanvas = np.zeros((720, 1280, 3), np.uint8)

# Créer la fenêtre en plein écran
cv2.namedWindow("Hand Drawing - Enhanced", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Hand Drawing - Enhanced", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    # 1. Import image
    success, img = cap.read()
    if not success:
        print("Failed to read from camera")
        break
    img = cv2.flip(img, 1)

    # 2. Find Hand Landmarks
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        # tip of index and middle fingers
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]

        # 3. Check which fingers are up
        fingers = detector.fingersUp()

        # 4. If Selection Mode - Two fingers are up
        if fingers[1] and fingers[2]:
            print("Selection Mode")
            # Checking for the click in header area
            if y1 < 125:
                if 50 < x1 < 200:  # Rouge
                    header = overlayList[0]
                    drawColor = (0, 0, 255)
                    isEraser = False
                elif 220 < x1 < 370:  # Bleu
                    header = overlayList[1]
                    drawColor = (255, 0, 0)
                    isEraser = False
                elif 390 < x1 < 540:  # Vert
                    header = overlayList[2]
                    drawColor = (0, 255, 0)
                    isEraser = False
                elif 560 < x1 < 710:  # Jaune
                    header = overlayList[3]
                    drawColor = (0, 255, 255)
                    isEraser = False
                elif 730 < x1 < 880:  # Violet
                    header = overlayList[4]
                    drawColor = (255, 0, 255)
                    isEraser = False
                elif 900 < x1 < 1050:  # Noir
                    header = overlayList[5]
                    drawColor = (0, 0, 0)
                    isEraser = False
                elif 1070 < x1 < 1220:  # Gomme
                    header = overlayList[6]
                    drawColor = (0, 0, 0)  # Noir pour effacer
                    isEraser = True
            
            # Afficher le rectangle de sélection
            cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)

        # 5. If Drawing Mode - Index finger is up
        elif fingers[1] and fingers[2] == False:
            if isEraser:
                cv2.circle(img, (x1, y1), eraserThickness//2, (255, 255, 255), 3)
                print("Eraser Mode")
            else:
                cv2.circle(img, (x1, y1), 15, drawColor, cv2.FILLED)
                print("Drawing Mode")
            
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            if isEraser:
                # Effacer en dessinant en noir (couleur du fond)
                cv2.line(img, (xp, yp), (x1, y1), (0, 0, 0), eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), (0, 0, 0), eraserThickness)
            else:
                # Dessiner normalement
                cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)

            xp, yp = x1, y1

        # Reset position when not drawing
        else:
            xp, yp = 0, 0

        # Clear Canvas seulement si on fait un geste spécial (poing fermé puis tous les doigts levés)
        if all(x >= 1 for x in fingers) and fingers.count(1) == 5:
            imgCanvas = np.zeros((720, 1280, 3), np.uint8)
            print("Canvas cleared!")

    # Process image blending
    imgGray = cv2.cvtColor(imgCanvas, cv2.COLOR_BGR2GRAY)
    _, imgInv = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY_INV)
    imgInv = cv2.cvtColor(imgInv, cv2.COLOR_GRAY2BGR)
    img = cv2.bitwise_and(img, imgInv)
    img = cv2.bitwise_or(img, imgCanvas)

    # Setting the header image
    img[0:125, 0:1280] = header

    # Afficher les instructions
    if isEraser:
        cv2.putText(img, "Mode: GOMME - Levez tous les doigts pour effacer tout", 
                   (10, img.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    else:
        cv2.putText(img, "Mode: DESSIN - Levez tous les doigts pour effacer tout", 
                   (10, img.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    cv2.putText(img, "q: Quitter | ESC: Fenetre normale | 2 doigts: Couleur | 1 doigt: Dessiner", 
               (10, img.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Afficher en plein écran
    cv2.imshow("Hand Drawing - Enhanced", img)
    
    # Contrôles clavier
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == 27:  # ESC key
        # Sortir du plein écran
        cv2.setWindowProperty("Hand Drawing - Enhanced", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)

# Release camera and close windows
cap.release()
cv2.destroyAllWindows()
