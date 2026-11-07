
import cv2
import math

def get_video_frames(video_path, nth):
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video.")
        return None
        
    total_frames = int(math.ceil((cap.get(cv2.CAP_PROP_FRAME_COUNT)) / nth))
    cap.release()
    
    return int(total_frames)
