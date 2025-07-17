# main.py
"""
Virtual Piano – Windows build
- Web-cam hand tracking via Mediapipe
- Bass keys (row 1-8)  : C3–C4
- Treble keys (row Q-I) : C4–C5
- Press ESC to quit
"""

import cv2

# Configuration pour le mode plein écran
def setup_fullscreen_window(window_name):
    """Configure une fenêtre pour le mode plein écran"""
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    return True

def toggle_fullscreen(window_name, is_fullscreen):
    """Bascule entre mode plein écran et fenêtre normale"""
    if is_fullscreen:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        print("Mode fenêtre normale activé")
        return False
    else:
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        print("Mode plein écran activé")
        return True

import mediapipe as mp
import numpy as np
import pygame
import threading
import time
import sys
from pathlib import Path

# ---------- CONFIG ----------
WIDTH, HEIGHT = 640, 480
FPS = 30
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
KEY_COLORS = [(  0,   0, 255), (  0, 255, 255), (  0, 255,   0),
              (255, 255,   0), (255,   0, 255), (255,   0,   0),
              (128,   0, 128), (  0, 128, 128)]

LEFT_KEYS   = "12345678"
RIGHT_KEYS  = "qwertyui"
LEFT_NOTES  = ["C3", "D3", "E3", "F3", "G3", "A3", "B3", "C4"]
RIGHT_NOTES = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
# ----------------------------

# ---------- Audio ----------
print("Initializing pygame mixer...")
pygame.mixer.init(frequency=22050, buffer=512)
print("Pygame mixer initialized")
NOTE_FREQ = {
    "C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4,
    "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2
}
SOUNDS = {}

def build_sound(note):
    name, octave = note[:-1], int(note[-1])
    f = 440 * 2 ** ((NOTE_FREQ[name] + (octave - 4) * 12) / 12)
    samples = (np.sin(2 * np.pi * np.arange(22050 * 0.35) * f / 22050) * 0.5 * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack((samples, samples)))

for n in set(LEFT_NOTES + RIGHT_NOTES):
    SOUNDS[n] = build_sound(n)

# ---------- Display ----------
print("Initializing display...")
# Create blank image for keyboard display
blank_img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
cv2.namedWindow("Virtual Piano", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Virtual Piano", WIDTH, HEIGHT)
print("Display initialized")

# ---------- Helpers ----------
pressed = set()
last_played = {}

def draw_keyboard(img):
    h, w = img.shape[:2]
    kw = w // 8
    # Top row (left hand)
    for i, k in enumerate(LEFT_KEYS):
        color = KEY_COLORS[i] if k in pressed else WHITE
        cv2.rectangle(img, (i * kw, 0), ((i + 1) * kw, h // 2), color, -1)
        cv2.putText(img, k.upper(), (i * kw + 10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, BLACK, 2)
    # Bottom row (right hand)
    for i, k in enumerate(RIGHT_KEYS):
        color = KEY_COLORS[i] if k in pressed else WHITE
        cv2.rectangle(img, (i * kw, h // 2), ((i + 1) * kw, h), color, -1)
        cv2.putText(img, k.upper(), (i * kw + 10, h // 2 + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, BLACK, 2)
    return img

def play(note):
    SOUNDS[note].play()

# ---------- Keyboard hook ----------
import pynput.keyboard as kb

def on_press(key):
    try:
        k = key.char.lower()
        if k in LEFT_KEYS or k in RIGHT_KEYS:
            pressed.add(k)
    except AttributeError:
        pass

def on_release(key):
    try:
        pressed.discard(key.char.lower())
    except AttributeError:
        pass

listener = kb.Listener(on_press=on_press, on_release=on_release)
listener.start()

# ---------- Main loop ----------
print("Entering main loop...")
        # Configuration de la fenêtre plein écran
        window_name = "Virtual Piano"
        setup_fullscreen_window(window_name)
        fullscreen_mode = True
        print("Mode plein écran activé - Appuyez sur 'f' pour basculer")
        
        
while True:
    frame = draw_keyboard(blank_img.copy())

    # Hand tracking disabled
    results = None

    cv2.imshow("Virtual Piano", frame)
    if cv2.waitKey(1000 // FPS) & 0xFF == 27:  # ESC
        break

cv2.destroyAllWindows()
listener.stop()
pygame.quit()
