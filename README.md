# video_summarizer_AI_oneAPI_hack_kpr

# video Summarizer & LSTM Secure Chatbot

This project provides two key features:

1. **Video Summarizer**: A tool that extracts, summarizes, and provides additional functionalities like PDF generation and text-to-speech from YouTube video transcripts.
2. **LSTM Secure Chatbot**: A chatbot powered by an LSTM model with safeguards against vulgar language, using a secure conversational interface.

---

## Features

### Video Summarizer:

- Extract video ID from YouTube links
- Fetch video transcripts
- Summarize video content
- Generate PDF summaries
- Text-to-speech for summaries
- Summary to multi-languages

### LSTM Secure Chatbot:

- Detects and blocks vulgar language
- Engages users in conversations based on input text
- Pretrained on conversational data leads to blocking of accounts.

---

## Prerequisites

- Python 3.7+
- `pip` (Python package manager)

---

## Installation

1. **Install the required packages:**

```bash
pip install -r requirements.txt
```

---

## Usage

### Video Summarizer

1. **Import functions:**

```python
from youtube_summarizer import extract_video_id, summarize_transcript, generate_pdf, speak_text
```

2. **Example usage:**

```python
video_link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
video_id = extract_video_id(video_link)

if video_id:
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    transcript_text = ' '.join([t['text'] for t in transcript])
    summary = summarize_transcript(transcript_text)

    print("Summary:", summary)

    pdf_file = generate_pdf(summary)
    print(f"PDF generated: {pdf_file}")

    speak_text(summary)
else:
    print("Invalid YouTube link")
```

---

### LSTM Secure Chatbot

1. **Running the Streamlit Chatbot:**

```bash
streamlit run chatbot_app.py
```

2. **Features:**
   - Type in a message, and the chatbot will respond.
   - The chatbot checks for inappropriate language using a predefined list of vulgar words.
   - Responses are generated using a pretrained LSTM model based on the input text.

---

## Code Breakdown

### YouTube Summarizer

- `extract_video_id(link)`: Extracts the video ID from a YouTube link.
- `summarize_transcript(transcript_text)`: Summarizes the provided transcript text.
- `chunk_text(text, max_length=1024)`: Splits text into smaller chunks for processing.
- `generate_pdf(summary_text)`: Generates a PDF summary.
- `speak_text(text)`: Uses text-to-speech to read the summary aloud. -`image_txt_summarizer`:Uses extracting the text from any kind of images

### LSTM Secure Chatbot

- **Model Architecture**: Uses an LSTM model built with Keras to predict responses.
- **Vulgarity Detection**: Prevents users from sending inappropriate messages.
- **Conversation Management**: Tracks and stores the conversation history.

---

## Acknowledgments

- YouTube Transcript API for extracting video transcripts.
- Hugging Face Transformers for text summarization.
- pyttsx3 for text-to-speech functionality.
- FPDF for PDF generation.
- TensorFlow and Keras for building the LSTM chatbot model.
- Tesseract for extracting text from images -`Download from this repo`:-https://github.com/UB-Mannheim/tesseract/wiki
