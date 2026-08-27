import cv2
from ultralytics import YOLO
import winsound
import wave
import struct
import math
import subprocess
import os
import sys


# ==========================================
# VIDEO INPUT
# ==========================================

if len(sys.argv) > 1:
    VIDEO_PATH = sys.argv[1]
else:
    VIDEO_PATH = "test-vid.mp4"


# ==========================================
# FILE NAMES
# ==========================================

TEMP_VIDEO = "pothole_detected_no_audio.avi"
FINAL_VIDEO = "pothole_detected_final.mp4"
BEEP_FILE = "beep.wav"


# ==========================================
# LOAD YOLO MODEL
# ==========================================

model = YOLO("best.pt")

print("Model loaded successfully!")


# ==========================================
# OPEN VIDEO
# ==========================================

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("Error: Could not open video.")
    print("Video:", VIDEO_PATH)
    exit()

print("Video opened successfully!")
print("Processing:", VIDEO_PATH)


# ==========================================
# VIDEO INFORMATION
# ==========================================

fps = cap.get(cv2.CAP_PROP_FPS)

width = int(
    cap.get(cv2.CAP_PROP_FRAME_WIDTH)
)

height = int(
    cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
)


# ==========================================
# CREATE TEMPORARY OUTPUT VIDEO
# ==========================================

fourcc = cv2.VideoWriter_fourcc(*"XVID")

out = cv2.VideoWriter(
    TEMP_VIDEO,
    fourcc,
    fps,
    (width, height)
)


# ==========================================
# VARIABLES
# ==========================================

frame_count = 0

total_detections = 0

previous_detection = False

# Store the exact times when a new pothole appears
beep_times = []


# ==========================================
# PROCESS VIDEO
# ==========================================

while True:

    ret, frame = cap.read()

    if not ret:
        break

    frame_count += 1


    # --------------------------------------
    # YOLO DETECTION
    # --------------------------------------

    results = model(
        frame,
        verbose=False
    )


    # Number of potholes detected
    potholes = len(
        results[0].boxes
    )


    # --------------------------------------
    # POTHOLE DETECTED
    # --------------------------------------

    if potholes > 0:

        total_detections += potholes


        # New pothole appearance
        if not previous_detection:

            current_time = frame_count / fps

            beep_times.append(
                current_time
            )


            print(
                f"Frame {frame_count}: "
                f"POTHOLE DETECTED - "
                f"BEEP at {current_time:.2f}s"
            )


            # Play beep during processing
            winsound.PlaySound(
                BEEP_FILE,
                winsound.SND_FILENAME |
                winsound.SND_ASYNC
            )


        previous_detection = True


    else:

        previous_detection = False


    # --------------------------------------
    # DRAW YOLO BOXES
    # --------------------------------------

    annotated_frame = results[0].plot()


    # --------------------------------------
    # SAVE FRAME
    # --------------------------------------

    out.write(
        annotated_frame
    )


# ==========================================
# CLOSE VIDEO
# ==========================================

cap.release()

out.release()


print("\nVideo processing complete!")

print(
    f"Total frames processed: "
    f"{frame_count}"
)

print(
    f"Total detections: "
    f"{total_detections}"
)

print(
    f"Beep events: "
    f"{len(beep_times)}"
)

print(
    f"Beep times: "
    f"{beep_times}"
)


# ==========================================
# CREATE WARNING AUDIO
# ==========================================

duration = frame_count / fps

sample_rate = 44100

beep_duration = 0.15

frequency = 1000


audio_frames = []

total_samples = int(
    duration * sample_rate
)


for i in range(total_samples):

    time = i / sample_rate

    active = False


    # Check if a beep should play
    for beep_time in beep_times:

        if (
            beep_time
            <= time
            <
            beep_time + beep_duration
        ):

            active = True

            break


    if active:

        value = int(
            32767
            * 0.5
            * math.sin(
                2
                * math.pi
                * frequency
                * time
            )
        )

    else:

        value = 0


    audio_frames.append(
        struct.pack(
            "<h",
            value
        )
    )


# ==========================================
# SAVE AUDIO
# ==========================================

with wave.open(
    "warning_audio.wav",
    "w"
) as audio:

    audio.setnchannels(1)

    audio.setsampwidth(2)

    audio.setframerate(
        sample_rate
    )

    audio.writeframes(
        b"".join(audio_frames)
    )


print(
    "Warning audio created."
)


# ==========================================
# COMBINE VIDEO + AUDIO
# ==========================================

command = [

    "ffmpeg",

    "-y",

    "-i",
    TEMP_VIDEO,

    "-i",
    "warning_audio.wav",

    "-c:v",
    "libx264",

    "-c:a",
    "aac",

    "-shortest",

    FINAL_VIDEO
]


print(
    "\nCreating final video..."
)


subprocess.run(
    command
)


# ==========================================
# FINAL RESULT
# ==========================================

print(
    "\nFINAL VIDEO CREATED:"
)

print(
    FINAL_VIDEO
)


if os.path.exists(
    FINAL_VIDEO
):

    file_size = (
        os.path.getsize(
            FINAL_VIDEO
        )
        / (1024 * 1024)
    )

    print(
        "File size:",
        round(
            file_size,
            2
        ),
        "MB"
    )

else:

    print(
        "ERROR: Final video was not created."
    )