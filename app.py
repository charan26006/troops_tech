# ==============================================================================
# 1. IMPORTS AND SETUP
# ==============================================================================
# --- This section imports all the necessary tools and sets up the API key ---

import streamlit as st
import cv2  # For video processing
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image  # To handle images

# Load the API key from the .env file
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


# ==============================================================================
# 2. HELPER FUNCTIONS
# ==============================================================================
# --- This section contains the core logic for video and AI processing ---

def video_to_frames(uploaded_file):
    """
    Takes an uploaded video file, saves it temporarily, and extracts
    one frame per second.
    Returns a list of image objects (Pillow format).
    """
    # Create a temporary directory to store frames
    temp_frame_dir = "temp_frames"
    if not os.path.exists(temp_frame_dir):
        os.makedirs(temp_frame_dir)

    # Save the uploaded file to a temporary path
    temp_video_path = os.path.join(temp_frame_dir, uploaded_file.name)
    with open(temp_video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Use OpenCV to capture the video
    cap = cv2.VideoCapture(temp_video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    
    frame_images = []
    frame_count = 0
    saved_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        
        # Extract one frame per second
        # Sample one frame every 5 seconds. This is a good balance.
        if frame_count % (fps * 5) == 0:
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)

            # NEW LINE: Resize the image to a smaller resolution
            pil_img = pil_img.resize((640, 360)) # A standard 16:9 low resolution

            frame_images.append(pil_img)
            saved_count += 1
        
        frame_count += 1
        
    cap.release()
    return frame_images


def get_video_summary(frames, guideline_prompt):
    """
    Sends the extracted frames and a guideline prompt to the Gemini 1.5 Pro model
    to get a descriptive summary.
    Returns the summary text.
    """
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    # The prompt is a mix of text instructions and the list of image frames
    prompt_parts = [guideline_prompt] + frames
    
    try:
        response = model.generate_content(prompt_parts)
        return response.text
    except Exception as e:
        st.error(f"An error occurred during analysis: {e}")
        return None

def get_chat_response(summary, question):
    """
    Sends the video summary and a user's question to the Gemini Pro model
    to get a conversational answer.
    """
    model = genai.GenerativeModel('gemini-pro')
    
    # Create a context-rich prompt for the chat model
    prompt = (
        "You are an AI assistant. A user has provided a video, and an initial analysis was performed. "
        "Based on the following summary, please answer the user's follow-up question.\n\n"
        f"--- VIDEO SUMMARY ---\n{summary}\n\n"
        f"--- USER'S QUESTION ---\n{question}\n\n"
        "Your Answer:"
    )
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"An error occurred during chat: {e}")
        return "Sorry, I couldn't process that question."


# ==============================================================================
# 3. STREAMLIT USER INTERFACE (UI)
# ==============================================================================
# --- This section defines how the web page looks and behaves ---

st.set_page_config(page_title="Visual Understanding Assistant", layout="wide")
st.title("👁️ Visual Understanding Chat Assistant")

# Initialize session state to store data across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []
if "video_summary" not in st.session_state:
    st.session_state.video_summary = None

# --- Sidebar for Upload and Analysis ---
with st.sidebar:
    st.header("1. Upload Video")
    uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "mov", "avi"])
    
    st.header("2. Define Guidelines")
    guideline = st.text_area(
        "Enter the guidelines for the AI to follow:",
        value="You are a traffic safety inspector. Analyze this sequence of video frames. "
              "Identify key events like vehicle movements, pedestrian crossings, and traffic light changes. "
              "Most importantly, detect and list any traffic violations with an approximate timestamp (e.g., 'at around second 5'). "
              "Provide a concise summary of the scene and a list of any violations found."
    )

    if st.button("Analyze Video"):
        if uploaded_file is not None:
            with st.spinner("Extracting frames from video..."):
                frames = video_to_frames(uploaded_file)
            
            if frames:
                st.success(f"{len(frames)} frames extracted successfully!")
                with st.spinner("AI is analyzing the video... This may take a minute."):
                    summary = get_video_summary(frames, guideline)
                    if summary:
                        st.session_state.video_summary = summary
                        st.session_state.messages = [
                            {"role": "assistant", "content": f"**Video Analysis Complete.**\n\n{summary}"}
                        ]
                        st.success("Analysis complete!")
                        # This command makes the app rerun to display the chat message
                        st.rerun() 
            else:
                st.error("Could not extract frames from the video.")
        else:
            st.warning("Please upload a video file first.")

# --- Main Chat Area ---
st.header("Chat about the Video")

# Display existing chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get new input from user
if prompt := st.chat_input("Ask a follow-up question..."):
    if st.session_state.video_summary:
        # Add user's message to display
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant's response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_chat_response(st.session_state.video_summary, prompt)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        st.warning("Please analyze a video before asking questions.")