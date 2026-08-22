import streamlit as st

st.set_page_config(
    page_title="Pothole Detection System",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 Pothole Detection System")

st.write(
    "Upload a driving video to detect potholes using YOLO."
)

uploaded_video = st.file_uploader(
    "Upload a driving video",
    type=["mp4", "avi", "mov"]
)

if uploaded_video is not None:

    st.success("Video uploaded successfully!")

    st.video(uploaded_video)
