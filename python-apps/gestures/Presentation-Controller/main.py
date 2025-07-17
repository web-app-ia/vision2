'''
Contrôleur de Présentation par Gestes

Fonctionnalités :
- Contrôle de diapositives (suivant/précédent) avec les gestes de la main.
- Pointeur laser virtuel contrôlé par l'index.
- Zoom et dézoom avec les doigts.
- Contrôle du volume.
- Affichage d'un tableau blanc pour dessiner.
'''

import cv2

# Configuration pour le mode fenêtre maximisée
def setup_maximized_window(window_name):
    """Configure une fenêtre pour occuper une grande partie de l'écran"""
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 1200, 800)
    return True

def toggle_window_mode(window_name, is_maximized):
    """Bascule entre mode maximisé et fenêtre normale"""
    if is_maximized:
        cv2.resizeWindow(window_name, 800, 600)
        print("Mode fenêtre normale activé")
        return False
    else:
        cv2.resizeWindow(window_name, 1200, 800)
        print("Mode fenêtre maximisée activé")
        return True

import numpy as np
import HandTrackingModule as htm
import time
import pyautogui

# --- Paramètres --- #
wCam, hCam = 640, 480
frameR = 100 # Marge de réduction du cadre
smoothing = 7 # Facteur de lissage

# --- Initialisation --- #
pTime = 0
plocX, plocY = 0, 0
cLocX, cLocY = 0, 0

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Erreur: Impossible d'ouvrir la caméra.")
    exit()

cap.set(3, wCam)
cap.set(4, hCam)

detector = htm.handDetector(maxHands=1)
wScr, hScr = pyautogui.size()

# Variables pour le tableau blanc
painting = []
color = (0, 0, 255) # Rouge par défaut
show_whiteboard = False
        # Configuration de la fenêtre maximisée
        window_name = "Contrôleur de Présentation"
        setup_maximized_window(window_name)
        maximized_mode = True
        print("Mode fenêtre maximisée activé - Appuyez sur 'f' pour basculer")
        
        

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if show_whiteboard:
        # Dessiner sur le tableau blanc
        for point in painting:
            cv2.circle(img, point, 5, color, -1)

    if len(lmList) != 0:
        x1, y1 = lmList[8][1:] # Index
        x2, y2 = lmList[12][1:] # Majeur

        fingers = detector.fingersUp()

        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR), (255, 0, 255), 2)

        # 1. Doigt levé : Mode déplacement
        if fingers[1] == 1 and fingers[2] == 0:
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            cLocX = plocX + (x3 - plocX) / smoothing
            cLocY = plocY + (y3 - plocY) / smoothing

            pyautogui.moveTo(cLocX, cLocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = cLocX, cLocY

        # 2. Index et majeur levés : Clic
        if fingers[1] == 1 and fingers[2] == 1:
            length, img, lineInfo = detector.findDistance(8, 12, img)
            if length < 40:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                pyautogui.click()

        # 3. Main ouverte : Diapositive suivante
        if fingers == [1, 1, 1, 1, 1]:
            pyautogui.press('right')
            time.sleep(1) # Pour éviter les pressions multiples

        # 4. Poing fermé : Diapositive précédente
        if fingers == [0, 0, 0, 0, 0]:
            pyautogui.press('left')
            time.sleep(1)

        # 5. Pincer pour zoomer/dézoomer
        if fingers[0] == 1 and fingers[4] == 1:
            length, _, _ = detector.findDistance(4, 20, img, draw=False)
            if length > 150:
                pyautogui.hotkey('ctrl', '+')
            else:
                pyautogui.hotkey('ctrl', '-')

        # 6. Activer/désactiver le tableau blanc
        if fingers[1] and fingers[4] and not any(fingers[0:1]) and not any(fingers[2:4]):
            show_whiteboard = not show_whiteboard
            time.sleep(0.5)

        # 7. Dessiner sur le tableau blanc
        if show_whiteboard and fingers[1] and not any(fingers[2:]):
            painting.append((x1, y1))

    # Affichage FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)

    cv2.imshow("Contrôleur de Présentation", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()