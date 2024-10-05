import streamlit as st
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import pandas as pd
import re

# Load the chatbot dataset from the CSV file
df = pd.read_csv("chatbot_dataset.csv")

# Load the list of vulgar words from a separate dataset
vulgar_df = pd.read_csv("vulgar_words.csv")
vulgar_words = vulgar_df['vulgar_words'].tolist()

# Define the maximum sequence length
max_length = 100

# Create a Tokenizer instance
tokenizer = Tokenizer(num_words=10000)

# Sample training data (replace with your actual data)
training_texts = df['input'].tolist()
training_labels = [1] * len(training_texts)  # Assuming all inputs are for conversation

# Fit the tokenizer on training data
tokenizer.fit_on_texts(training_texts)

# Prepare the padded input and output data
padded_inputs = pad_sequences(tokenizer.texts_to_sequences(training_texts), maxlen=max_length)
outputs = np.array(training_labels)

# Define the LSTM model architecture
model = Sequential()
model.add(Embedding(input_dim=10000, output_dim=128, input_length=max_length))
model.add(LSTM(128, dropout=0.2))
model.add(Dense(64, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# Compile the model
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# Sample validation data (replace with your actual validation data)
validation_texts = ["hi there", "see you later"]
validation_labels = [1, 0]

# Prepare the validation data
padded_inputs_val = pad_sequences(tokenizer.texts_to_sequences(validation_texts), maxlen=max_length)
outputs_val = np.array(validation_labels)

# Train the model
model.fit(padded_inputs, outputs, epochs=10, batch_size=32, validation_data=(padded_inputs_val, outputs_val))

# Create a Streamlit interface
st.title("LSTM Secure Chatbot")

# Initialize session state to keep track of conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

def contains_vulgar(text):
    # Check if any vulgar words are present in the text
    return any(re.search(r'\b' + re.escape(word.replace('*', '')) + r'\b', text.lower()) for word in vulgar_words)

user_input = st.text_input("Enter your message")

if st.button("Send"):
    # Check for vulgar language
    if contains_vulgar(user_input):
        st.warning("Your message contains inappropriate language. Please refrain from using such language. Repeated offenses may lead to account ban.")
    else:
        # Preprocess the user input
        input_seq = tokenizer.texts_to_sequences([user_input])
        input_seq = pad_sequences(input_seq, maxlen=max_length)

        # Generate a response using the LSTM model
        response = model.predict(input_seq)

        # Generate a conversational response
        if response[0][0] > 0.5:  # Simple threshold for conversation
            # Search for a matching input in the DataFrame
            reply = df[df['input'].str.lower().isin([user_input.lower()])]['response']
            if not reply.empty:
                reply = reply.values[0]
            else:
                reply = "Chatbot: That's interesting! Tell me more."
        else:
            reply = "Chatbot: Goodbye! Have a great day!"

        # Append the user input and chatbot response to conversation history
        st.session_state.conversation_history.append(f"You: {user_input}")
        st.session_state.conversation_history.append(reply)

    # Display the conversation history
    for message in st.session_state.conversation_history:
        st.write(message)