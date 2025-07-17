import cv2
import time

def test_camera_access():
    """Test l'accès aux différentes caméras disponibles."""
    print("=== Test d'accès aux caméras ===")
    
    working_cameras = []
    
    # Tester les indices de caméra de 0 à 3
    for i in range(4):
        print(f"\nTest de la caméra {i}...")
        
        try:
            cap = cv2.VideoCapture(i)
            
            # Vérifier si la caméra s'ouvre
            if cap.isOpened():
                # Essayer de lire un frame
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"  ✓ Caméra {i} : FONCTIONNELLE")
                    print(f"    Résolution: {frame.shape[1]}x{frame.shape[0]}")
                    working_cameras.append(i)
                else:
                    print(f"  ✗ Caméra {i} : Ouverte mais pas de frame")
            else:
                print(f"  ✗ Caméra {i} : Impossible d'ouvrir")
                
            cap.release()
            
        except Exception as e:
            print(f"  ✗ Caméra {i} : Erreur - {e}")
    
    print(f"\n=== Résultats ===")
    if working_cameras:
        print(f"Caméras fonctionnelles : {working_cameras}")
        return working_cameras[0]  # Retourner le premier index qui fonctionne
    else:
        print("Aucune caméra fonctionnelle trouvée")
        return None

def test_camera_with_different_backends():
    """Test avec différents backends OpenCV."""
    print("\n=== Test avec différents backends ===")
    
    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Microsoft Media Foundation"),
        (cv2.CAP_V4L2, "Video4Linux2"),
        (cv2.CAP_ANY, "Any")
    ]
    
    for backend_id, backend_name in backends:
        print(f"\nTest avec backend {backend_name}...")
        try:
            cap = cv2.VideoCapture(0, backend_id)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"  ✓ Backend {backend_name} : FONCTIONNEL")
                    cap.release()
                    return backend_id
                else:
                    print(f"  ✗ Backend {backend_name} : Pas de frame")
            else:
                print(f"  ✗ Backend {backend_name} : Impossible d'ouvrir")
            cap.release()
        except Exception as e:
            print(f"  ✗ Backend {backend_name} : Erreur - {e}")
    
    return None

if __name__ == "__main__":
    # Test des caméras
    working_camera = test_camera_access()
    
    if working_camera is not None:
        print(f"\n=== Test de la caméra {working_camera} ===")
        
        # Test avec différents backends
        working_backend = test_camera_with_different_backends()
        
        if working_backend is not None:
            print(f"\nTest final avec caméra {working_camera} et backend approprié...")
            cap = cv2.VideoCapture(working_camera, working_backend)
            
            if cap.isOpened():
                print("✓ Configuration fonctionnelle trouvée !")
                print("Appuyez sur une touche pour voir un aperçu (5 secondes)...")
                
                start_time = time.time()
                while time.time() - start_time < 5:
                    ret, frame = cap.read()
                    if ret:
                        cv2.imshow('Test Camera', frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                
                cap.release()
                cv2.destroyAllWindows()
                print("Test terminé avec succès !")
            else:
                print("✗ Impossible d'ouvrir la caméra même avec la configuration trouvée")
        else:
            print("✗ Aucun backend fonctionnel trouvé")
    else:
        print("✗ Impossible de trouver une caméra fonctionnelle")
