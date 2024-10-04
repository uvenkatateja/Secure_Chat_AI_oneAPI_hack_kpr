import http.client
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from fpdf import FPDF
from googletrans import Translator
import json
import pyttsx3

# Set up the translator and text-to-speech engine
translator = Translator()
tts_engine = pyttsx3.init()

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
        'x-rapidapi-key': "b3f00fe5cemshc7eaab2ade19a85p12e03bjsnc5a15b5ce04b",
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
st.title("YouTube Video Summarizer & Chatbot")

# Add sidebar for navigation
st.sidebar.title("Navigation")
option = st.sidebar.radio("Choose a feature:", ("YouTube Summarizer", "Chatbot"))

if option == "YouTube Summarizer":
    st.header("YouTube Video Summarizer")

    # Sidebar text input for YouTube video link
    youtube_link = st.sidebar.text_input("Enter YouTube video link:")

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
        st.write("Please enter a valid YouTube video link in the sidebar.")

elif option == "Chatbot":
    st.header("Chatbot")

    message = st.text_input("You : ")
    if st.button("Send"):
        response = get_chatgpt_response(message)
        response_json = json.loads(response)
        chatgpt_response = response_json.get("result", "No response from ChatGPT.")
        st.write("ChatGPT: " + chatgpt_response)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Telugu"):
                telugu_response = translate_text(chatgpt_response, 'te')
                st.write("Telugu: " + telugu_response)
        with col2:
            if st.button("Tamil"):
                tamil_response = translate_text(chatgpt_response, 'ta')
                st.write("Tamil: " + tamil_response)
        with col3:
            if st.button("Hindi"):
                hindi_response = translate_text(chatgpt_response, 'hi')
                st.write("Hindi: " + hindi_response)
