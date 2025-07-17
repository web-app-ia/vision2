import cv2
import mediapipe as mp
import time
import numpy as np

class PoseEstimationApp:
    def __init__(self):
        # Initialiser MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Configuration de la détection de la pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Configurations diverses
        self.color_active = (0, 255, 0)  # Vert pour les points détectés
        self.color_inactive = (0, 0, 255)  # Rouge pour les points non visibles
        self.point_radius = 5

        # Suivi du comptage des frames pour FPS
        self.fps_counter = 0
        self.fps_time = time.time()
        self.current_fps = 0

    def render_landmarks(self, frame, landmarks):
        """Dessine les landmarks de la pose sur le frame."""
        if landmarks is not None:
            for idx, landmark in enumerate(landmarks.landmark):
                if landmark.visibility > 0.5:
                    frame_height, frame_width, _ = frame.shape
                    cx, cy = int(landmark.x * frame_width), int(landmark.y * frame_height)
                    cv2.circle(frame, (cx, cy), self.point_radius, self.color_active, -1)

            self.mp_drawing.draw_landmarks(
                frame,
                landmarks,
                self.mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())

    def run(self):
        """Lance l'application de suivi de la pose corporelle."""
        print("=== Application de Suivi de Pose Corporelle ===")
        print("Initialisation de la caméra...")

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("Erreur: Impossible d'ouvrir la caméra")
            return

        # Configurer la caméra
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        print("Caméra initialisée avec succès")
        print("Appuyez sur 'q' pour quitter")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Erreur lors de la lecture du frame")
                    break

                # Retourner horizontalement pour effet miroir
                frame = cv2.flip(frame, 1)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Processus de détection de la pose
                results = self.pose.process(frame_rgb)

                # Dessiner les landmarks
                if results.pose_landmarks:
                    self.render_landmarks(frame, results.pose_landmarks)

                # Mettre à jour le FPS
                self.update_fps()

                # Ajouter des informations
                self.draw_info_panel(frame)

                # Afficher le frame
                cv2.imshow('Suivi de Pose Corporelle - Computer Vision App', frame)

                # Gestion des touches
                key = cv2.waitKey(1) & 0xFF

                if key == ord('q'):  # 'q' pour quitter
                    print("Arrêt demandé par l'utilisateur")
                    break

        except KeyboardInterrupt:
            print("Arrêt demandé par Ctrl+C")
        except Exception as e:
            print(f"Erreur: {e}")
        finally:
            print("Nettoyage des ressources...")
            cap.release()
            cv2.destroyAllWindows()
            print("Application terminée")

    def update_fps(self):
        """Met à jour le compteur FPS."""
        self.fps_counter += 1
        current_time = time.time()

        if current_time - self.fps_time >= 1.0:
            self.current_fps = self.fps_counter / (current_time - self.fps_time)
            self.fps_counter = 0
            self.fps_time = current_time

    def draw_info_panel(self, frame):
        """Dessine les informations sur le frame."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"FPS: {self.current_fps:.1f}", (10, 30), font, 0.8, self.color_active, 2)

def main():
    print("Démarrage de l'application de suivi de la pose corporelle...")
    app = PoseEstimationApp()
    app.run()

if __name__ == "__main__":
    main()

