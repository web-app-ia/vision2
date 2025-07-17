import cv2

def test_camera():
    # Test multiple camera indices
    for i in range(3):
        print(f"Testing camera {i}...")
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Camera {i} is working!")
                print(f"Frame shape: {frame.shape}")
                
                # Show a test window
                cv2.imshow(f"Camera {i} Test", frame)
                cv2.waitKey(1000)  # Show for 1 second
                cv2.destroyAllWindows()
                cap.release()
                return i
            else:
                print(f"Camera {i} opened but failed to read frame")
        else:
            print(f"Camera {i} could not be opened")
        cap.release()
    
    print("No working cameras found")
    return None

if __name__ == "__main__":
    working_camera = test_camera()
    if working_camera is not None:
        print(f"Use camera index {working_camera} in your app")
    else:
        print("No cameras available. Please check your camera connections.")
