import os
from pathlib import Path
import shutil
import cv2


def extract(vid_path, nth):
    video_dir = os.path.dirname(os.path.abspath(vid_path))
    out_folder = os.path.join(video_dir, "out/frames")

    if Path(f"{video_dir}/out").is_dir():
        shutil.rmtree(Path(f"{video_dir}/out"))
        print("Removed old scan")

    os.makedirs(out_folder, exist_ok=True)

    cap = cv2.VideoCapture(vid_path)

    if not cap.isOpened():
        print(f"Error: Could not open video file: {vid_path}")
        return

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if frame_count % nth == 0:
            frame_filename = os.path.join(out_folder, f"frame_{frame_count:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(
        f"Done! Processed {frame_count} frames. Saved {saved_count} frames to {out_folder}"
    )
