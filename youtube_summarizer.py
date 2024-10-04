# youtube_summarizer.py
import http.client
from youtube_transcript_api import YouTubeTranscriptApi
from transformers import pipeline
from fpdf import FPDF
import pyttsx3

# Initialize text-to-speech engine
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

# Function to summarize video transcript
def summarize_transcript(transcript_text):
    summarizer = pipeline("summarization")
    chunked_texts = list(chunk_text(transcript_text, max_length=400))  # Chunk transcript into 400-word pieces
    summaries = [summarizer(chunk, max_length=150, min_length=50, do_sample=False)[0]['summary_text'] for chunk in chunked_texts]
    return ' '.join(summaries)

# Function to chunk text into smaller pieces
def chunk_text(text, max_length=1024):
    words = text.split()
    for i in range(0, len(words), max_length):
        yield ' '.join(words[i:i+max_length])

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


