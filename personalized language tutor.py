import streamlit as st
import os
from openai import OpenAI

# Streamlit app title
st.title("🎙️ Audio Transcription, Translation, Grammar & Pronunciation Feedback")

# Upload audio file
audio_file = st.file_uploader("Upload a WAV/MP3 audio file", type=["wav", "mp3"])

# Set target translation language
target_language = st.selectbox("Select target translation language:", ["French", "Arabic", "German"])

# Input target text for pronunciation comparison
target_text = st.text_area("Enter the target text for pronunciation feedback:", 
                           "Heat brings out flavor, cold restores, salt complements ham, tacos are a favorite, and hot cross buns are zestful.")

# Initialize OpenAI client
openai_api_key = os.environ.get("OPENAI_API_KEY")

if openai_api_key:
    client = OpenAI(api_key=openai_api_key)
else:
    st.error("❌ OPENAI_API_KEY not found in environment variables. Please set it before using the app.")

if audio_file and st.button("🚀 Process Audio"):
    with st.spinner("Processing..."):
        try:
            # Save uploaded file temporarily
            temp_path = "temp.wav"
            with open(temp_path, "wb") as f:
                f.write(audio_file.read())

            # Step 1: Transcribe Audio
            with open(temp_path, "rb") as f_audio:
                transcription_response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f_audio
                )
                transcription_text = transcription_response.text
                st.subheader("📝 Transcribed Text")
                st.success(transcription_text)

            # Step 2: Translate Text
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": f"Please translate the following text to {target_language}: {transcription_text}"}
                ]
            )
            translated_text = completion.choices[0].message.content
            st.subheader(f"🌍 Translated Text ({target_language})")
            st.success(translated_text)

            # Step 3: Grammar Feedback
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a language learning assistant providing grammar feedback."},
                    {"role": "user", "content": f"Please correct any grammar mistakes in the following text and provide feedback: {translated_text}"}
                ]
            )
            grammar_feedback = completion.choices[0].message.content
            st.subheader("✍️ Grammar Feedback")
            st.info(grammar_feedback)

            # Step 4: Pronunciation Feedback
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a language learning assistant providing pronunciation feedback."},
                    {"role": "user", "content": f"I said: {transcription_text}. How close is it to: {target_text}? Give feedback."}
                ]
            )
            pronunciation_feedback = completion.choices[0].message.content
            st.subheader("🎤 Pronunciation Feedback")
            st.warning(pronunciation_feedback)

        except Exception as e:
            st.error(f"An error occurred: {e}")
