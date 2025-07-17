import cv2
import numpy as np
import time
import os
import HandTrackingModule as htm

#######################
# Épaisseurs disponibles
thickness_options = [5, 15, 25, 35, 50]
current_thickness_index = 2  # 25 par défaut
brushThickness = thickness_options[current_thickness_index]
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
cv2.namedWindow("Hand Drawing - Final", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Hand Drawing - Final", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

# Variables pour le contrôle d'épaisseur
thickness_change_time = 0
THICKNESS_CHANGE_DELAY = 0.5  # Délai en secondes entre les changements

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
        
        # tip of ring finger for thickness control
        x3, y3 = lmList[16][1:]

        # 3. Check which fingers are up
        fingers = detector.fingersUp()

        # 4. Contrôle de l'épaisseur avec l'annulaire (3 doigts: index, majeur, annulaire)
        if fingers[1] and fingers[2] and fingers[3] and not fingers[4]:
            current_time = time.time()
            if current_time - thickness_change_time > THICKNESS_CHANGE_DELAY:
                if y3 < 300:  # Mouvement vers le haut
                    current_thickness_index = min(current_thickness_index + 1, len(thickness_options) - 1)
                    thickness_change_time = current_time
                elif y3 > 400:  # Mouvement vers le bas
                    current_thickness_index = max(current_thickness_index - 1, 0)
                    thickness_change_time = current_time
                
                brushThickness = thickness_options[current_thickness_index]
                print(f"Thickness changed to: {brushThickness}")
            
            # Afficher l'indicateur d'épaisseur
            cv2.circle(img, (640, 300), brushThickness, (255, 255, 255), 3)
            cv2.putText(img, f"Epaisseur: {brushThickness}", (540, 350), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # 5. Mode sélection de couleur - 2 doigts levés (index + majeur seulement)
        elif fingers[1] and fingers[2] and not fingers[3]:
            print("Selection Mode")
            # Checking for the click in header area
            if y1 < 125:
                if 50 < x1 < 200:  # Rouge
                    header = overlayList[0]
                    drawColor = (0, 0, 255)
                    isEraser = False
                elif 220 < x1 < 370:  # Bleu (plus foncé)
                    header = overlayList[1]
                    drawColor = (200, 0, 0)
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
                elif 900 < x1 < 1050:  # Noir - traité comme une couleur normale
                    header = overlayList[5]
                    drawColor = (0, 0, 0)
                    isEraser = False
                elif 1070 < x1 < 1220:  # Gomme
                    header = overlayList[6]
                    drawColor = (0, 0, 0)  # Couleur pour la gomme
                    isEraser = True
            
            # Afficher le rectangle de sélection
            if not isEraser:
                cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), drawColor, cv2.FILLED)
            else:
                cv2.rectangle(img, (x1, y1 - 25), (x2, y2 + 25), (128, 128, 128), cv2.FILLED)

        # 6. Mode dessin/gomme - Index finger seulement
        elif fingers[1] and not fingers[2] and not fingers[3]:
            if isEraser:
                cv2.circle(img, (x1, y1), eraserThickness//2, (255, 255, 255), 3)
                print("Eraser Mode")
            else:
                cv2.circle(img, (x1, y1), brushThickness//2, drawColor, cv2.FILLED)
                print("Drawing Mode")
            
            if xp == 0 and yp == 0:
                xp, yp = x1, y1

            if isEraser:
                # Effacer en dessinant avec la couleur de fond (noir)
                cv2.line(img, (xp, yp), (x1, y1), (0, 0, 0), eraserThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), (0, 0, 0), eraserThickness)
            else:
                # Dessiner normalement avec la couleur sélectionnée
                cv2.line(img, (xp, yp), (x1, y1), drawColor, brushThickness)
                cv2.line(imgCanvas, (xp, yp), (x1, y1), drawColor, brushThickness)

            xp, yp = x1, y1

        # Reset position when not drawing
        else:
            xp, yp = 0, 0

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
        cv2.putText(img, "Mode: GOMME - Seule la gomme peut effacer", 
                   (10, img.shape[0] - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    else:
        cv2.putText(img, f"Mode: DESSIN - Couleur active - Epaisseur: {brushThickness}", 
                   (10, img.shape[0] - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    cv2.putText(img, "1 doigt: Dessiner | 2 doigts: Couleur | 3 doigts: Epaisseur", 
               (10, img.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    cv2.putText(img, "q: Quitter | ESC: Fenetre normale", 
               (10, img.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Afficher en plein écran
    cv2.imshow("Hand Drawing - Final", img)
    
    # Contrôles clavier
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == 27:  # ESC key
        # Sortir du plein écran
        cv2.setWindowProperty("Hand Drawing - Final", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
    elif key == ord('c'):  # Touche 'c' pour effacer tout
        imgCanvas = np.zeros((720, 1280, 3), np.uint8)
        print("Canvas cleared manually!")

# Release camera and close windows
cap.release()
cv2.destroyAllWindows()
