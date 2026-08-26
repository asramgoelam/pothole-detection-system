import streamlit as st
import cv2
import tempfile
import os
import time
import subprocess
import winsound

from ultralytics import YOLO

# Load trained YOLO model
model = YOLO("best.pt")

print("YOLO model loaded successfully!")

# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Pothole Detection System",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0e1117;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #aab2bf;
        margin-bottom: 20px;
    }

    .road-clear {
        background-color: #12351f;
        border: 1px solid #238636;
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        font-size: 28px;
        font-weight: 700;
        color: #3fb950;
        margin: 10px 0 20px 0;
    }

    .pothole-warning {
        background-color: #3b1818;
        border: 2px solid #f85149;
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        font-size: 28px;
        font-weight: 800;
        color: #ff7b72;
        margin: 10px 0 20px 0;
    }

    .system-ready {
        background-color: #12351f;
        border: 1px solid #238636;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        font-weight: 700;
        color: #3fb950;
    }

    .live-indicator {
        background-color: #3b1818;
        border: 1px solid #f85149;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        font-weight: 700;
        color: #ff7b72;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="main-title">🚗 POTHOLE DETECTION SYSTEM</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">AI Road Safety & Computer Vision System</div>',
    unsafe_allow_html=True
)


# =========================================================
# SYSTEM STATUS
# =========================================================

status1, status2 = st.columns(2)

with status1:

    st.markdown(
        """
        <div class="system-ready">
        🟢 SYSTEM READY
        </div>
        """,
        unsafe_allow_html=True
    )

with status2:

    st.markdown(
        """
        <div class="live-indicator">
        🤖 YOLO MODEL LOADED
        </div>
        """,
        unsafe_allow_html=True
    )


st.write("")


# =========================================================
# ABOUT THE SYSTEM
# =========================================================

with st.expander("ℹ️ About the System"):

    st.write(
        """
        The Pothole Detection System uses a trained YOLO
        computer vision model to detect potholes in road
        images and videos.

        When a pothole is detected, the system draws a
        bounding box around it and generates an audio
        warning.

        The system supports recorded video analysis and
        a LIVE demonstration mode.

        For the LIVE demonstration, a recorded driving
        video is processed frame-by-frame to simulate
        a live camera feed.
        """
    )


# =========================================================
# DETECTION MODE
# =========================================================

st.subheader("Detection Mode")

mode = st.radio(
    "Choose a detection mode:",
    [
        "📁 Upload Video",
        "📡 LIVE"
    ],
    horizontal=True
)


# =========================================================
# UPLOAD VIDEO MODE
# =========================================================

if mode == "📁 Upload Video":

    st.header("📁 Upload Driving Video")

    st.write(
        "Upload a recorded driving video. "
        "The trained YOLO model will detect potholes "
        "and generate a new video with visual and "
        "audio warnings."
    )

    uploaded_video = st.file_uploader(
        "Choose a driving video",
        type=["mp4", "avi", "mov"],
        key="normal_video"
    )

    if uploaded_video is not None:

        st.success(
            "Video uploaded successfully! ✅"
        )

        # =================================================
        # SAVE UPLOADED VIDEO
        # =================================================

        input_path = "uploaded_video.mp4"

        with open(
            input_path,
            "wb"
        ) as f:

            f.write(
                uploaded_video.getbuffer()
            )

        # =================================================
        # SHOW ORIGINAL VIDEO
        # =================================================

        st.subheader("🎥 Original Video")

        st.video(
            input_path
        )

        st.write("")

        # =================================================
        # DETECT POTHOLES
        # =================================================

        if st.button(
            "🔍 DETECT POTHOLES",
            use_container_width=True
        ):

            st.info(
                "AI is processing the video. "
                "Please wait..."
            )

            progress = st.progress(0)

            try:

                # -----------------------------------------
                # Remove previous output files
                # -----------------------------------------

                old_files = [
                    "pothole_detected_no_audio.avi",
                    "pothole_detected_final.mp4",
                    "warning_audio.wav"
                ]

                for file in old_files:

                    if os.path.exists(file):

                        try:
                            os.remove(file)

                        except PermissionError:
                            pass

                # -----------------------------------------
                # RUN WORKING VIDEO DETECTOR
                # -----------------------------------------

                result = subprocess.run(
                    [
                        "python",
                        "video_detector.py",
                        input_path
                    ],
                    capture_output=True,
                    text=True
                )

                progress.progress(100)

                # -----------------------------------------
                # SHOW PROCESSING INFORMATION
                # -----------------------------------------

                if result.stdout:

                    with st.expander(
                        "🔧 Processing Information"
                    ):

                        st.text(
                            result.stdout
                        )

                # -----------------------------------------
                # CHECK FOR ERRORS
                # -----------------------------------------

                if result.returncode != 0:

                    st.error(
                        "Video processing failed."
                    )

                    if result.stderr:

                        st.code(
                            result.stderr
                        )

                else:

                    # -------------------------------------
                    # FINAL VIDEO
                    # -------------------------------------

                    output_path = (
                        "pothole_detected_final.mp4"
                    )

                    if os.path.exists(
                        output_path
                    ):

                        st.success(
                            "Pothole detection completed! ✅"
                        )

                        st.subheader(
                            "🕳️ Detected Video"
                        )

                        # Show final video
                        st.video(
                            output_path
                        )

                        # Download button
                        with open(
                            output_path,
                            "rb"
                        ) as video_file:

                            st.download_button(
                                label="⬇️ Download Detected Video",
                                data=video_file,
                                file_name="pothole_detected_final.mp4",
                                mime="video/mp4",
                                use_container_width=True
                            )

                    else:

                        st.error(
                            "The detector finished, "
                            "but the final video was "
                            "not created."
                        )

            except Exception as e:

                st.error(
                    f"Error while processing video: {e}"
                )


# =========================================================
# LIVE MODE
# =========================================================

else:

    st.header("📡 LIVE Detection Mode")

    st.info(
        "The system processes the feed frame-by-frame "
        "and detects potholes as they appear."
    )

    st.caption(
        "For demonstration purposes, a recorded driving "
        "video is used as the LIVE feed."
    )

    # =====================================================
    # LIVE SOURCE
    # =====================================================

    st.subheader(
        "📡 Live Feed Source"
    )

    source = st.radio(
        "Choose your source:",
        [
            "🎥 Demonstration Video",
            "📷 Webcam",
            "🚗 Dashcam"
        ],
        horizontal=True
    )


    # =====================================================
    # DEMONSTRATION VIDEO
    # =====================================================

    if source == "🎥 Demonstration Video":

        live_video = st.file_uploader(
            "Choose LIVE demonstration video",
            type=["mp4", "avi", "mov"],
            key="live_video"
        )

        if live_video is not None:

            st.success(
                "LIVE demonstration feed ready! ✅"
            )

            # =================================================
            # SAVE TEMPORARY VIDEO
            # =================================================

            temp_file = tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".mp4"
            )

            temp_path = temp_file.name

            temp_file.write(
                live_video.getbuffer()
            )

            temp_file.close()


            # =================================================
            # OPEN VIDEO
            # =================================================

            cap = cv2.VideoCapture(
                temp_path
            )

            if not cap.isOpened():

                st.error(
                    "Could not open the demonstration video."
                )

                cap.release()

                try:

                    os.remove(
                        temp_path
                    )

                except PermissionError:

                    pass

            else:

                # =============================================
                # VIDEO INFORMATION
                # =============================================

                fps = cap.get(
                    cv2.CAP_PROP_FPS
                )

                if fps <= 0:
                    fps = 30

                frame_delay = 1 / fps


                # =============================================
                # DASHBOARD
                # =============================================

                st.subheader(
                    "🔴 LIVE Monitoring Dashboard"
                )

                col1, col2, col3 = st.columns(3)

                with col1:

                    pothole_counter = st.empty()

                with col2:

                    warning_counter = st.empty()

                with col3:

                    system_status = st.empty()


                pothole_counter.metric(
                    "🕳️ POTHOLES",
                    0
                )

                warning_counter.metric(
                    "⚠️ WARNINGS",
                    0
                )

                system_status.metric(
                    "🤖 SYSTEM",
                    "READY"
                )


                # =============================================
                # WARNING DISPLAY
                # =============================================

                warning_display = st.empty()

                warning_display.markdown(
                    """
                    <div class="road-clear">
                    🟢 ROAD CLEAR
                    </div>
                    """,
                    unsafe_allow_html=True
                )


                # =============================================
                # VIDEO DISPLAY
                # =============================================

                st.subheader(
                    "🎥 LIVE FEED"
                )

                video_display = st.empty()


                # =============================================
                # START BUTTON
                # =============================================

                start_live = st.button(
                    "▶️ START LIVE DETECTION",
                    use_container_width=True
                )


                # =============================================
                # LIVE PROCESSING
                # =============================================

                if start_live:

                    total_potholes = 0

                    total_warnings = 0

                    previous_detection = False

                    system_status.metric(
                        "🤖 SYSTEM",
                        "ACTIVE"
                    )


                    while True:

                        ret, frame = cap.read()

                        if not ret:
                            break


                        # =====================================
                        # YOLO DETECTION
                        # =====================================

                        results = model(
                            frame,
                            verbose=False,
                            conf=0.25
                        )


                        # =====================================
                        # COUNT POTHOLES
                        # =====================================

                        potholes = len(
                            results[0].boxes
                        )


                        # =====================================
                        # POTHOLE DETECTED
                        # =====================================

                        if potholes > 0:

                            # Only trigger once when a
                            # new detection starts
                            if not previous_detection:

                                total_potholes += potholes

                                total_warnings += 1


                                # =================================
                                # 🔊 LIVE BEEP
                                # =================================

                                try:

                                    winsound.PlaySound(
                                        "beep.wav",
                                        winsound.SND_FILENAME
                                        | winsound.SND_ASYNC
                                    )

                                except Exception as e:

                                    print(
                                        "Beep error:",
                                        e
                                    )


                            previous_detection = True


                            # =================================
                            # WARNING DISPLAY
                            # =================================

                            warning_display.markdown(
                                """
                                <div class="pothole-warning">
                                ⚠️ POTHOLE DETECTED
                                <br>
                                🔊 AUDIO WARNING
                                </div>
                                """,
                                unsafe_allow_html=True
                            )


                        else:

                            previous_detection = False


                            warning_display.markdown(
                                """
                                <div class="road-clear">
                                🟢 ROAD CLEAR
                                </div>
                                """,
                                unsafe_allow_html=True
                            )


                        # =====================================
                        # DRAW YOLO BOXES
                        # =====================================

                        annotated_frame = (
                            results[0].plot()
                        )


                        # Convert BGR → RGB
                        annotated_frame = cv2.cvtColor(
                            annotated_frame,
                            cv2.COLOR_BGR2RGB
                        )


                        # =====================================
                        # DISPLAY FRAME
                        # =====================================

                        video_display.image(
                            annotated_frame,
                            channels="RGB",
                            use_container_width=True
                        )


                        # =====================================
                        # UPDATE DASHBOARD
                        # =====================================

                        pothole_counter.metric(
                            "🕳️ POTHOLES",
                            total_potholes
                        )

                        warning_counter.metric(
                            "⚠️ WARNINGS",
                            total_warnings
                        )


                        # =====================================
                        # VIDEO SPEED
                        # =====================================

                        time.sleep(
                            frame_delay
                        )


                    # =========================================
                    # RELEASE VIDEO
                    # =========================================

                    cap.release()


                    system_status.metric(
                        "🤖 SYSTEM",
                        "FINISHED"
                    )


                    warning_display.markdown(
                        """
                        <div class="road-clear">
                        ✅ LIVE DETECTION FINISHED
                        </div>
                        """,
                        unsafe_allow_html=True
                    )


                    st.success(
                        f"LIVE detection completed. "
                        f"Total potholes detected: "
                        f"{total_potholes}"
                    )


                    # =========================================
                    # DELETE TEMP FILE
                    # =========================================

                    try:

                        if os.path.exists(
                            temp_path
                        ):

                            os.remove(
                                temp_path
                            )

                    except PermissionError:

                        st.warning(
                            "Temporary video could not "
                            "be deleted immediately. "
                            "This does not affect the result."
                        )


    # =====================================================
    # WEBCAM MODE
    # =====================================================

    elif source == "📷 Webcam":

        st.warning(
            "📷 Webcam mode is prepared for future "
            "real-time camera integration."
        )

        st.info(
            "For the current presentation, use "
            "'🎥 Demonstration Video'."
        )


    # =====================================================
    # DASHCAM MODE
    # =====================================================

    elif source == "🚗 Dashcam":

        st.warning(
            "🚗 Dashcam mode is prepared for future "
            "hardware integration."
        )

        st.info(
            "A physical dashcam can be connected in a "
            "future version to provide a real camera feed."
        )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header(
        "⚙️ System Information"
    )

    st.write(
        "### 🤖 AI Model"
    )

    st.write(
        "YOLO Pothole Detector"
    )

    st.write(
        "### 🕳️ Detection Class"
    )

    st.write(
        "Pothole"
    )

    st.write(
        "### 🔊 Audio Warning"
    )

    st.write(
        "Enabled"
    )

    st.write(
        "### 📡 Detection Sources"
    )

    st.write(
        """
        • Upload Video
        • LIVE Demonstration
        • Webcam (future)
        • Dashcam (future)
        """
    )

    st.divider()

    st.caption(
        "Pothole Detection System"
    )

    st.caption(
        "AI • Computer Vision • Road Safety"
    )
