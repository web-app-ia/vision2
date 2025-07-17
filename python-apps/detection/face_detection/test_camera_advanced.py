import cv2
import time

def test_camera_with_directshow():
    """Test spécifiquement avec DirectShow pour Windows."""
    print("=== Test avec DirectShow (Windows) ===")
    
    for i in range(4):
        print(f"\nTest caméra {i} avec DirectShow...")
        try:
            # Forcer l'utilisation de DirectShow
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"  ✓ Caméra {i} : FONCTIONNELLE avec DirectShow")
                    print(f"    Résolution: {frame.shape[1]}x{frame.shape[0]}")
                    cap.release()
                    return i
                else:
                    print(f"  ✗ Caméra {i} : Ouverte mais pas de frame")
            else:
                print(f"  ✗ Caméra {i} : Impossible d'ouvrir avec DirectShow")
            
            cap.release()
            
        except Exception as e:
            print(f"  ✗ Caméra {i} : Erreur - {e}")
    
    return None

def test_camera_with_msmf():
    """Test avec Microsoft Media Foundation."""
    print("\n=== Test avec Microsoft Media Foundation ===")
    
    for i in range(4):
        print(f"\nTest caméra {i} avec MSMF...")
        try:
            cap = cv2.VideoCapture(i, cv2.CAP_MSMF)
            
            if cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    print(f"  ✓ Caméra {i} : FONCTIONNELLE avec MSMF")
                    print(f"    Résolution: {frame.shape[1]}x{frame.shape[0]}")
                    cap.release()
                    return i
                else:
                    print(f"  ✗ Caméra {i} : Ouverte mais pas de frame")
            else:
                print(f"  ✗ Caméra {i} : Impossible d'ouvrir avec MSMF")
            
            cap.release()
            
        except Exception as e:
            print(f"  ✗ Caméra {i} : Erreur - {e}")
    
    return None

def show_opencv_info():
    """Affiche les informations OpenCV."""
    print("\n=== Informations OpenCV ===")
    print(f"Version OpenCV: {cv2.__version__}")
    print(f"Backends disponibles: {cv2.getBuildInformation()}")

if __name__ == "__main__":
    show_opencv_info()
    
    # Test avec DirectShow
    working_camera = test_camera_with_directshow()
    
    if working_camera is None:
        # Test avec MSMF si DirectShow échoue
        working_camera = test_camera_with_msmf()
    
    if working_camera is not None:
        print(f"\n=== Test final avec caméra {working_camera} ===")
        
        # Test avec DirectShow en priorité
        cap = cv2.VideoCapture(working_camera, cv2.CAP_DSHOW)
        
        if cap.isOpened():
            print("✓ Configuration fonctionnelle trouvée avec DirectShow!")
            print("Appuyez sur 'q' pour fermer la fenêtre de test...")
            
            while True:
                ret, frame = cap.read()
                if ret:
                    cv2.imshow('Test Camera - Appuyez sur Q pour fermer', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                else:
                    print("Erreur lors de la lecture du frame")
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            print("Test terminé avec succès !")
        else:
            print("✗ Impossible d'ouvrir la caméra même avec la configuration trouvée")
    else:
        print("\n✗ Aucune caméra fonctionnelle trouvée")
        print("Vérifiez que:")
        print("- Une caméra est connectée et allumée")
        print("- Les pilotes de caméra sont installés")
        print("- Aucune autre application n'utilise la caméra")
        print("- Les permissions d'accès à la caméra sont accordées")
