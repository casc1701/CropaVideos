import cv2
import numpy as np
import subprocess
import glob

video_files = glob.glob('*.mp4')
for video_file in video_files:
    if "cropped" in video_file:
       print(f"Skipping processing for video: {video_file} (contains 'cropped')")
       continue
    print(f"Processing video: {video_file}")
    
    
    #cap = cv2.VideoCapture('teste.mp4')
    
    ShowPreview = True
    
    cap = cv2.VideoCapture(video_file)
    
    _, first_frame = cap.read()
    gray_first = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # Initialize variables to find the outermost bounding rectangle
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), 0, 0

    # Define the codec and create a VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Use 'mp4v' or 'h264' for MP4 format
    #out = cv2.VideoWriter('output_video.mp4', fourcc, fps, (width, height))

    while True:
        _, frame = cap.read()
        if frame is None:
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_diff = cv2.absdiff(gray_first, gray_frame)
        _, thresh = cv2.threshold(frame_diff, 200, 255, cv2.THRESH_BINARY)

        # Use contours or other techniques to identify moving parts
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw rectangles around moving parts
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + w)
            max_y = max(max_y, y + h)

        # Write the frame to the output video
        #out.write(frame)

        if ShowPreview:
            cv2.imshow('Moving Parts', frame)
            if cv2.waitKey(30) & 0xFF == 27:
             break

    # Calculate crop coordinates compatible with ffmpeg
    crop_coordinates = f"{max_x - min_x}:{max_y - min_y}:{min_x}:{min_y}"

    # Output the crop coordinates
    print("Crop coordinates:", crop_coordinates)



    # Release the VideoWriter and video capture objects
    #out.release()
    cap.release()
    cv2.destroyAllWindows()

    # Build the FFMPEG command
    input_filename = video_file
    output_filename = f'{input_filename[:-4]}-cropped.mp4'  # Assuming 'teste.mp4' is the input filename
    ffmpeg_command = [
        'ffmpeg',
        '-y',
        '-loglevel',"quiet",
        '-i', input_filename,
        '-vf', f'crop={max_x - min_x}:{max_y - min_y}:{min_x}:{min_y}',
        '-c:a', 'copy',
        output_filename
    ]

    # Call FFMPEG using subprocess
    subprocess.run(ffmpeg_command)

    print(f'Video cropped and saved as: {output_filename}')
