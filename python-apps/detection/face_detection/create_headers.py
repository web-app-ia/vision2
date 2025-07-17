import cv2
import numpy as np

# Create header images for color selection
def create_header_images():
    # Image dimensions
    height = 125
    width = 1280
    
    # Create base header with color selection areas
    header = np.ones((height, width, 3), np.uint8) * 255  # White background
    
    # Color selection areas - 6 couleurs maintenant
    # Rouge
    cv2.rectangle(header, (50, 0), (200, height), (0, 0, 255), -1)
    cv2.putText(header, "Rouge", (70, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Bleu (plus foncé)
    cv2.rectangle(header, (220, 0), (370, height), (200, 0, 0), -1)
    cv2.putText(header, "Bleu", (250, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Vert
    cv2.rectangle(header, (390, 0), (540, height), (0, 255, 0), -1)
    cv2.putText(header, "Vert", (420, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Jaune
    cv2.rectangle(header, (560, 0), (710, height), (0, 255, 255), -1)
    cv2.putText(header, "Jaune", (580, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # Violet
    cv2.rectangle(header, (730, 0), (880, height), (255, 0, 255), -1)
    cv2.putText(header, "Violet", (750, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Noir
    cv2.rectangle(header, (900, 0), (1050, height), (0, 0, 0), -1)
    cv2.putText(header, "Noir", (930, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Gomme
    cv2.rectangle(header, (1070, 0), (1220, height), (128, 128, 128), -1)
    cv2.putText(header, "Gomme", (1090, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Save different versions with different highlights
    colors = ['rouge', 'bleu', 'vert', 'jaune', 'violet', 'noir', 'gomme']
    
    for i, color in enumerate(colors):
        header_copy = header.copy()
        # Add highlight border around selected color
        if i == 0:  # Rouge
            cv2.rectangle(header_copy, (45, 5), (205, height-5), (255, 255, 255), 5)
        elif i == 1:  # Bleu
            cv2.rectangle(header_copy, (215, 5), (375, height-5), (255, 255, 255), 5)
        elif i == 2:  # Vert
            cv2.rectangle(header_copy, (385, 5), (545, height-5), (255, 255, 255), 5)
        elif i == 3:  # Jaune
            cv2.rectangle(header_copy, (555, 5), (715, height-5), (255, 255, 255), 5)
        elif i == 4:  # Violet
            cv2.rectangle(header_copy, (725, 5), (885, height-5), (255, 255, 255), 5)
        elif i == 5:  # Noir
            cv2.rectangle(header_copy, (895, 5), (1055, height-5), (255, 255, 255), 5)
        elif i == 6:  # Gomme
            cv2.rectangle(header_copy, (1065, 5), (1225, height-5), (255, 255, 255), 5)
        
        cv2.imwrite(f'Header/{i+1}.png', header_copy)
        print(f"Created Header/{i+1}.png")

if __name__ == "__main__":
    create_header_images()
