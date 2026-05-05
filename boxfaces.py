#!/data/data/com.termux/files/usr/bin/python
import os
from pathlib import Path
import sys

import cv2
from loguru import logger


def detect_and_save_faces(input_video_path, output_video_path="out.mp4"):
    """
    Reads a video file, detects faces using OpenCV's Haar Cascade classifier,
    draws rectangles around them, and saves the annotated video.

    Args:
        input_video_path (str): The path to the input video file.
        output_video_path (str): The path to save the output annotated video.
                                 Defaults to "out.mp4".
    """
    if not Path(input_video_path).exists():
        logger.info(f"Error: Input video file not found at '{input_video_path}'")
        sys.exit(1)

    # Load the face cascade classifier
    # Ensure you have 'haarcascade_frontalface_default.xml' in the same directory
    # or provide the full path to the classifier file.
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    if not Path(cascade_path).exists():
        logger.info(f"Error: Haar Cascade classifier file not found at '{cascade_path}'")
        logger.info("Please download it or ensure OpenCV is correctly installed.")
        sys.exit(1)

    face_cascade = cv2.CascadeClassifier(cascade_path)

    # Open the video file
    cap = cv2.VideoCapture(input_video_path)
    if not cap.isOpened():
        logger.info(f"Error: Could not open video file '{input_video_path}'")
        sys.exit(1)

    # Get video properties for output writer
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    # Use MJPG codec for broader compatibility, or XVID if MJPG is not available/desired
    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')

    # Create VideoWriter object
    out = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))
    if not out.isOpened():
        logger.info(f"Error: Could not open video writer for '{output_video_path}'")
        cap.release()
        sys.exit(1)

    logger.info(f"Processing video: '{input_video_path}'")
    logger.info(f"Saving annotated video to: '{output_video_path}'")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of video or error reading frame

        frame_count += 1
        # Convert frame to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the grayscale frame
        # Adjust parameters (scaleFactor, minNeighbors) as needed for better detection
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        # Draw rectangles around the detected faces
        for x, y, w, h in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)  # Blue rectangle, thickness 2

        # Write the annotated frame to the output video
        out.write(frame)

        # Optional: Display the processed frame (useful for debugging)
        # cv2.imshow('frame', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

        if frame_count % 100 == 0:
            logger.info(f"Processed {frame_count} frames...")

    logger.info(f"Finished processing. Total frames processed: {frame_count}")

    # Release everything when done
    cap.release()
    out.release()
    # cv2.destroyAllWindows() # Uncomment if you use cv2.imshow


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.info("Usage: python detect_faces.py <input_video_path> [output_video_path]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = "out.mp4"  # Default output name

    if len(sys.argv) > 2:
        output_file = sys.argv[2]

    # Ensure output directory exists if specified in path
    output_dir = Path(output_file).parent
    if output_dir and not Path(output_dir).exists():
        Path(output_dir).mkdir(parents=True)
        logger.info(f"Created output directory: {output_dir}")

    detect_and_save_faces(input_file, output_file)
    logger.info("Video processing complete.")
