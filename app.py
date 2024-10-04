
import http.client
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from fpdf import FPDF
from googletrans import Translator
import json
import pyttsx3
from PIL import Image
import pytesseract  # You may need to install pytesseract and the Tesseract-OCR executable

# Set up the translator and text-to-speech engine
translator = Translator()
tts_engine = pyttsx3.init()

# Violations list with keywords, descriptions, and risk levels
violations = [
    {"keywords": ["harm", "hurt", "kill", "abuse", "violence"], "description": "Harmful content", "risk_level": 5},
    {"keywords": ["age", "disability", "manipulate", "exploit"], "description": "Exploiting vulnerabilities (age, disability)", "risk_level": 4},
    {"keywords": ["subliminal", "manipulative"], "description": "Subliminal techniques to impair decision-making", "risk_level": 3},
    {"keywords": ["threat", "intimidation"], "description": "Threatening behavior", "risk_level": 4},
    {"keywords": ["racism", "sexism", "discrimination"], "description": "Discriminatory language", "risk_level": 4},
    {"keywords": ["assault", "harassment", "abduction"], "description": "Harassment or assault", "risk_level": 5},
]

# Function to extract video ID from link
def extract_video_id(link):
    try:
        if not link or "v=" not in link:
            return None
        video_id = link.split("v=")[1]
        return video_id if video_id else None
    except Exception as e:
        print(f"Error extracting video ID: {str(e)}")
        return None

# Function to get ChatGPT response
def get_chatgpt_response(message):
    conn = http.client.HTTPSConnection("chatgpt-42.p.rapidapi.com")
    payload = json.dumps({"messages": [{"role": "user", "content": message}], "web_access": False})
    headers = {
        'x-rapidapi-key': "your_rapidapi_key_here",
        'x-rapidapi-host': "chatgpt-42.p.rapidapi.com",
        'Content-Type': "application/json"
    }
    conn.request("POST", "/gpt4", payload, headers)
    res = conn.getresponse()
    data = res.read()
    return data.decode("utf-8")

# Function to translate text
def translate_text(text, lang):
    result = translator.translate(text, dest=lang)
    return result.text

# Function to generate PDF
def generate_pdf(summary_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="YouTube Video Summary", ln=True, align="C")
    pdf.multi_cell(0, 10, summary_text)
    pdf_file = "summary.pdf"
    pdf.output(pdf_file)
    return pdf_file

# Function to speak text
def speak_text(text):
    tts_engine.setProperty('rate', 150)  # Speed of speech
    tts_engine.say(text)
    tts_engine.runAndWait()

# Function to chunk text into smaller pieces
def chunk_text(text, max_length=1024):
    words = text.split()
    for i in range(0, len(words), max_length):
        yield ' '.join(words[i:i+max_length])

# Function to check for violations in a message
def check_for_violations(message):
    for violation in violations:
        if any(keyword in message.lower() for keyword in violation["keywords"]):
            return violation
    return None

# Function to convert image to text
def image_to_text(image):
    # Using pytesseract to extract text from the image
    return pytesseract.image_to_string(image)

# Available languages for translation
languages = {
    'English': 'en',
    'Spanish': 'es',
    'French': 'fr',
    'German': 'de',
    'Chinese': 'zh-cn',
    'Hindi': 'hi',
}

# Set up Streamlit app
st.title("Video Summarizer.ai & Chatbot")

# Add sidebar for navigation
st.sidebar.title("Navigation")
option = st.sidebar.radio("Choose a feature:", ("YouTube Summarizer", "Chatbot", "Image to Text"))

if option == "YouTube Summarizer":
    st.header("Video Summarizer.ai")

    # Sidebar text input for YouTube video link
    youtube_link = st.sidebar.text_input("Enter video link:")

    # Main content logic for summarization
    video_id = extract_video_id(youtube_link)
    if video_id:
        try:
            # Get video transcript
            transcript = YouTubeTranscriptApi.get_transcript(video_id)

            # Convert transcript to text
            transcript_text = ' '.join([t['text'] for t in transcript])

            # Summarize transcript in chunks
            summarizer = pipeline("summarization")
            chunked_texts = list(chunk_text(transcript_text, max_length=400))  # Chunk transcript into 400-word pieces
            summaries = [summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]['summary_text'] for chunk in chunked_texts]
            
            # Join all chunked summaries
            full_summary = ' '.join(summaries)

            # Display full summary in original language (English)
            st.write("Summary of the video:")
            st.write(full_summary)

            # Translate summary to the selected language
            selected_language = st.sidebar.selectbox("Select language for translation:", list(languages.keys()))
            translated_summary = translator.translate(full_summary, dest=languages[selected_language]).text

            # Display translated summary
            st.write(f"Translated Summary in {selected_language}:")
            st.write(translated_summary)

            # Speak the translated summary
            if st.sidebar.button("Listen to Summary"):
                speak_text(translated_summary)

            # Sidebar button to download the summary as PDF
            if st.sidebar.button("Download Summary as PDF"):
                pdf_file = generate_pdf(translated_summary)
                with open(pdf_file, "rb") as file:
                    st.sidebar.download_button(
                        label="Download PDF",
                        data=file,
                        file_name="summary.pdf",
                        mime="application/octet-stream"
                    )
        except Exception as e:
            print(f"Error summarizing video: {str(e)}")
            st.write("Error summarizing video. Please check the video link and try again.")
    else:
        st.write("Please enter a valid video link in the sidebar.")

elif option == "Chatbot":
    st.header("Chatbot")

    message = st.text_input("You : ")
    if st.button("Send"):
        # Check if the message contains inappropriate content
        violation = check_for_violations(message)
        
        if violation:
            # Display a red warning symbol and message
            st.markdown(
                f"""
                <div style="background-color:#ffcccb; padding: 10px; border-radius: 5px;">
                    <span style="color:red; font-size:24px; font-weight:bold;">⚠️</span>
                    <span style="color:red; font-size:18px; font-weight:bold;"> **Warning**: {violation['description']} detected.</span>
                    <br>
                    <span style="color:red;">Risk Level: {violation['risk_level']}</span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.write("Next chat interaction is blocked due to violation.")
        else:
            # Proceed with getting ChatGPT response
            response = get_chatgpt_response(message)
            response_json = json.loads(response)
            chatgpt_response = response_json.get("result", "No response from ChatGPT.")
            st.write("ChatGPT: " + chatgpt_response)

elif option == "Image to Text":
    st.header("Image to Text")

    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        # Convert the uploaded image to text
        image = Image.open(uploaded_file)
        extracted_text = image_to_text(image)
        
        # Display the extracted text
        st.write("Extracted Text:")
        st.write(extracted_text)

        # Optionally, translate the extracted text
        selected_language = st.selectbox("Select language for translation:", list(languages.keys()))
        if st.button("Translate"):
            translated_text = translate_text(extracted_text, languages[selected_language])
            st.write(f"Translated Text in {selected_language}:")
            st.write(translated_text)

            # Speak the translated text
            if st.button("Listen to Translated Text"):
                speak_text(translated_text)
