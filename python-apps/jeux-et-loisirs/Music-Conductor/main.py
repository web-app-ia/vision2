import pygame
import numpy as np
import math
import sys

# Initialisation de pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Constantes
WIDTH = 1200
HEIGHT = 400
FPS = 60

# Couleurs
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
BLUE = (0, 100, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Notes et fréquences
NOTES = {
    'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63,
    'F4': 349.23, 'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00,
    'A#4': 466.16, 'B4': 493.88, 'C5': 523.25, 'C#5': 554.37, 'D5': 587.33,
    'D#5': 622.25, 'E5': 659.25, 'F5': 698.46, 'F#5': 739.99, 'G5': 783.99,
    'G#5': 830.61, 'A5': 880.00, 'A#5': 932.33, 'B5': 987.77, 'C6': 1046.50
}

WHITE_KEYS = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B5', 'C6']
BLACK_KEYS = ['C#4', 'D#4', 'F#4', 'G#4', 'A#4', 'C#5', 'D#5', 'F#5', 'G#5', 'A#5']

# Touches du clavier
KEY_MAPPING = {
    pygame.K_q: 'C4', pygame.K_2: 'C#4', pygame.K_w: 'D4', pygame.K_3: 'D#4',
    pygame.K_e: 'E4', pygame.K_r: 'F4', pygame.K_5: 'F#4', pygame.K_t: 'G4',
    pygame.K_6: 'G#4', pygame.K_y: 'A4', pygame.K_7: 'A#4', pygame.K_u: 'B4',
    pygame.K_i: 'C5', pygame.K_9: 'C#5', pygame.K_o: 'D5', pygame.K_0: 'D#5',
    pygame.K_p: 'E5', pygame.K_z: 'F5', pygame.K_s: 'F#5', pygame.K_x: 'G5',
    pygame.K_d: 'G#5', pygame.K_c: 'A5', pygame.K_f: 'A#5', pygame.K_v: 'B5',
    pygame.K_b: 'C6'
}

class SoundGenerator:
    def __init__(self):
        self.sample_rate = 22050
        self.playing_notes = {}
        
    def generate_wave(self, frequency, duration, wave_type='sine'):
        frames = int(duration * self.sample_rate)
        arr = np.zeros(frames)
        
        for i in range(frames):
            time = float(i) / self.sample_rate
            if wave_type == 'sine':
                wave = np.sin(2 * np.pi * frequency * time)
            elif wave_type == 'square':
                wave = np.sign(np.sin(2 * np.pi * frequency * time))
            elif wave_type == 'sawtooth':
                wave = 2 * (time * frequency - np.floor(time * frequency + 0.5))
            
            # Envelope pour éviter les clics
            envelope = 1.0
            if i < frames * 0.1:  # Attack
                envelope = i / (frames * 0.1)
            elif i > frames * 0.9:  # Release
                envelope = (frames - i) / (frames * 0.1)
            
            arr[i] = wave * envelope * 0.3
        
        # Convertir en format pygame
        arr = (arr * 32767).astype(np.int16)
        stereo_arr = np.zeros((frames, 2), dtype=np.int16)
        stereo_arr[:, 0] = arr
        stereo_arr[:, 1] = arr
        
        return pygame.sndarray.make_sound(stereo_arr)
    
    def play_note(self, note, wave_type='sine'):
        if note in NOTES:
            sound = self.generate_wave(NOTES[note], 2.0, wave_type)
            sound.play()
            self.playing_notes[note] = sound
    
    def stop_note(self, note):
        if note in self.playing_notes:
            self.playing_notes[note].stop()
            del self.playing_notes[note]

class PianoKey:
    def __init__(self, note, x, y, width, height, is_black=False):
        self.note = note
        self.rect = pygame.Rect(x, y, width, height)
        self.is_black = is_black
        self.is_pressed = False
        self.color = BLACK if is_black else WHITE
        self.pressed_color = DARK_GRAY if is_black else LIGHT_GRAY
    
    def draw(self, screen):
        color = self.pressed_color if self.is_pressed else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        # Nom de la note
        font = pygame.font.Font(None, 24)
        text_color = WHITE if self.is_black else BLACK
        text = font.render(self.note, True, text_color)
        text_rect = text.get_rect(center=(self.rect.centerx, self.rect.bottom - 20))
        screen.blit(text, text_rect)
    
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class Piano:
    def __init__(self):
        self.keys = []
        self.sound_generator = SoundGenerator()
        self.current_wave = 'sine'
        self.volume = 0.5
        self.octave = 4
        self.recording = False
        self.recorded_notes = []
        self.playing_recording = False
        self.setup_keys()
    
    def setup_keys(self):
        # Touches blanches
        white_key_width = WIDTH // len(WHITE_KEYS)
        white_key_height = HEIGHT - 100
        
        for i, note in enumerate(WHITE_KEYS):
            x = i * white_key_width
            y = 50
            key = PianoKey(note, x, y, white_key_width, white_key_height, False)
            self.keys.append(key)
        
        # Touches noires
        black_key_width = white_key_width // 2
        black_key_height = white_key_height // 2
        black_positions = [0.7, 1.7, 3.7, 4.7, 5.7, 7.7, 8.7, 10.7, 11.7, 12.7]
        
        for i, note in enumerate(BLACK_KEYS):
            x = int(black_positions[i] * white_key_width - black_key_width // 2)
            y = 50
            key = PianoKey(note, x, y, black_key_width, black_key_height, True)
            self.keys.append(key)
    
    def handle_key_press(self, key):
        if key in KEY_MAPPING:
            note = KEY_MAPPING[key]
            self.play_note(note)
    
    def handle_key_release(self, key):
        if key in KEY_MAPPING:
            note = KEY_MAPPING[key]
            self.stop_note(note)
    
    def handle_mouse_press(self, pos):
        # Vérifier les touches noires en premier (elles sont au-dessus)
        for key in reversed(self.keys):
            if key.is_black and key.is_clicked(pos):
                self.play_note(key.note)
                return
        
        # Puis les touches blanches
        for key in self.keys:
            if not key.is_black and key.is_clicked(pos):
                self.play_note(key.note)
                return
    
    def handle_mouse_release(self, pos):
        for key in self.keys:
            if key.is_clicked(pos):
                self.stop_note(key.note)
    
    def play_note(self, note):
        # Marquer la touche comme pressée
        for key in self.keys:
            if key.note == note:
                key.is_pressed = True
                break
        
        # Jouer le son
        self.sound_generator.play_note(note, self.current_wave)
        
        # Enregistrer si en mode enregistrement
        if self.recording:
            self.recorded_notes.append((note, pygame.time.get_ticks()))
    
    def stop_note(self, note):
        # Marquer la touche comme relâchée
        for key in self.keys:
            if key.note == note:
                key.is_pressed = False
                break
        
        self.sound_generator.stop_note(note)
    
    def draw(self, screen):
        # Fond
        screen.fill(GRAY)
        
        # Titre
        font = pygame.font.Font(None, 48)
        title = font.render("Piano Virtuel", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 10))
        
        # Dessiner les touches blanches d'abord
        for key in self.keys:
            if not key.is_black:
                key.draw(screen)
        
        # Puis les touches noires
        for key in self.keys:
            if key.is_black:
                key.draw(screen)
        
        # Interface de contrôle
        self.draw_controls(screen)
    
    def draw_controls(self, screen):
        y_pos = HEIGHT - 90
        
        # Type d'onde
        font = pygame.font.Font(None, 24)
        wave_text = font.render(f"Onde: {self.current_wave}", True, BLACK)
        screen.blit(wave_text, (10, y_pos))
        
        # Boutons de type d'onde
        wave_types = ['sine', 'square', 'sawtooth']
        for i, wave_type in enumerate(wave_types):
            x = 150 + i * 100
            color = BLUE if wave_type == self.current_wave else LIGHT_GRAY
            pygame.draw.rect(screen, color, (x, y_pos, 80, 30))
            pygame.draw.rect(screen, BLACK, (x, y_pos, 80, 30), 2)
            text = font.render(wave_type, True, BLACK)
            screen.blit(text, (x + 5, y_pos + 5))
        
        # Bouton d'enregistrement
        rec_color = RED if self.recording else LIGHT_GRAY
        pygame.draw.rect(screen, rec_color, (500, y_pos, 60, 30))
        pygame.draw.rect(screen, BLACK, (500, y_pos, 60, 30), 2)
        rec_text = font.render("REC", True, BLACK)
        screen.blit(rec_text, (515, y_pos + 5))
        
        # Bouton de lecture
        play_color = GREEN if self.playing_recording else LIGHT_GRAY
        pygame.draw.rect(screen, play_color, (570, y_pos, 60, 30))
        pygame.draw.rect(screen, BLACK, (570, y_pos, 60, 30), 2)
        play_text = font.render("PLAY", True, BLACK)
        screen.blit(play_text, (580, y_pos + 5))
        
        # Instructions
        instructions = [
            "Utilisez la souris ou le clavier pour jouer",
            "Q-U-I-P: touches blanches | 2-3-5-6-7-9-0: touches noires",
            "Cliquez sur les boutons pour changer le type d'onde"
        ]
        
        for i, instruction in enumerate(instructions):
            text = pygame.font.Font(None, 20).render(instruction, True, BLACK)
            screen.blit(text, (10, y_pos + 35 + i * 20))
    
    def handle_control_click(self, pos):
        y_pos = HEIGHT - 90
        
        # Boutons de type d'onde
        wave_types = ['sine', 'square', 'sawtooth']
        for i, wave_type in enumerate(wave_types):
            x = 150 + i * 100
            if pygame.Rect(x, y_pos, 80, 30).collidepoint(pos):
                self.current_wave = wave_type
                return
        
        # Bouton d'enregistrement
        if pygame.Rect(500, y_pos, 60, 30).collidepoint(pos):
            self.recording = not self.recording
            if self.recording:
                self.recorded_notes = []
        
        # Bouton de lecture
        if pygame.Rect(570, y_pos, 60, 30).collidepoint(pos):
            if self.recorded_notes:
                self.play_recording()
    
    def play_recording(self):
        if not self.recorded_notes:
            return
        
        # Jouer les notes enregistrées
        start_time = pygame.time.get_ticks()
        first_note_time = self.recorded_notes[0][1]
        
        for note, timestamp in self.recorded_notes:
            delay = timestamp - first_note_time
            pygame.time.wait(delay)
            self.sound_generator.play_note(note, self.current_wave)
            pygame.time.wait(200)  # Durée de la note

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Piano Virtuel")
    clock = pygame.time.Clock()
    
    piano = Piano()
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    piano.handle_key_press(event.key)
            
            elif event.type == pygame.KEYUP:
                piano.handle_key_release(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    # Vérifier les contrôles d'abord
                    piano.handle_control_click(event.pos)
                    # Puis les touches de piano
                    piano.handle_mouse_press(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    piano.handle_mouse_release(event.pos)
        
        piano.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
