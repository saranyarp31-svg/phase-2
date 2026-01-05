import streamlit as st
import openai
import uuid
import os
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from langdetect import detect
import nltk
import tempfile
import requests
import urllib.parse

# -------------------------------
# INITIAL SETUP
# -------------------------------
st.set_page_config(page_title="Rural ACT – Phase 2", layout="wide")
st.title("🌾 Rural ACT – Phase 2 (Perfect Tamil Engine)")

nltk.download("punkt")

openai.api_key = st.secrets["OPENAI_API_KEY"]

# -------------------------------
# SEMANTIC CHUNKING
# -------------------------------
def semantic_chunks(text, max_sentences=4):
    sentences = nltk.sent_tokenize(text)
    chunks, temp = [], []

    for s in sentences:
        temp.append(s)
        if len(temp) >= max_sentences:
            chunks.append(" ".join(temp))
            temp = []

    if temp:
        chunks.append(" ".join(temp))

    return chunks

# -------------------------------
# PERFECT TAMIL GENERATION
# -------------------------------
def generate_perfect_tamil(english_text):
    prompt = f"""
Rewrite the following content into very clear,
natural, grammatically perfect Tamil.

Rules:
- Tamil only
- Suitable for rural users
- Do NOT translate word by word
- Preserve meaning
- Use spoken but respectful Tamil

Text:
{english_text}
"""

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()

# -------------------------------
# ANY LANGUAGE → ENGLISH
# -------------------------------
def to_english(text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Translate the input text to English accurately."},
            {"role": "user", "content": text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip()

# -------------------------------
# LONG TAMIL TTS (GOOGLE – STABLE)
# -------------------------------
def tamil_tts(text):
    files = []
    chunks = semantic_chunks(text, max_sentences=2)

    for chunk in chunks:
        text_encoded = urllib.parse.quote(chunk)
        url = (
            f"https://translate.google.com/translate_tts?"
            f"ie=UTF-8&q={text_encoded}&tl=ta&client=tw-ob"
        )

        response = requests.get(url)
        if response.status_code == 200:
            filename = f"tts_{uuid.uuid4()}.mp3"
            with open(filename, "wb") as f:
                f.write(response.content)
            files.append(filename)

    return files

# -------------------------------
# PDF GENERATION (LONG SAFE)
# -------------------------------
def generate_pdf(original, tamil_text):
    file_path = f"RuralACT_{uuid.uuid4()}.pdf"
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(file_path)

    story = []
    story.append(Paragraph("<b>Original Input</b>", styles["Heading2"]))
    story.append(Paragraph(original, styles["Normal"]))
    story.append(Paragraph("<br/>", styles["Normal"]))
    story.append(Paragraph("<b>Tamil Output</b>", styles["Heading2"]))

    for para in tamil_text.split("\n\n"):
        story.append(Paragraph(para, styles["Normal"]))

    doc.build(story)
    return file_path

# -------------------------------
# UI INPUT
# -------------------------------
user_input = st.text_area(
    "📝 Enter text (ANY language, long paragraph supported):",
    height=200
)

if st.button("🚀 Convert to Perfect Tamil"):
    if not user_input.strip():
        st.warning("Please enter text.")
        st.stop()

    with st.spinner("🔍 Processing language & meaning..."):
        detected_lang = detect(user_input)
        english_text = to_english(user_input)

    with st.spinner("🧠 Generating perfect Tamil..."):
        eng_chunks = semantic_chunks(english_text)
        tamil_chunks = [generate_perfect_tamil(c) for c in eng_chunks]
        final_tamil = "\n\n".join(tamil_chunks)

    st.subheader("📌 Tamil Output")
    st.success(final_tamil)

    # -------------------------------
    # AUDIO
    # -------------------------------
    st.subheader("🔊 Tamil Voice Output")
    audio_files = tamil_tts(final_tamil)
    for f in audio_files:
        st.audio(f)

    # -------------------------------
    # PDF DOWNLOAD
    # -------------------------------
    pdf_file = generate_pdf(user_input, final_tamil)
    with open(pdf_file, "rb") as f:
        st.download_button(
            "📄 Download Tamil PDF",
            data=f,
            file_name="RuralACT_Tamil_Output.pdf",
            mime="application/pdf"
        )

    st.caption("✅ Works for long paragraphs | Any language | Natural Tamil")

# -------------------------------
# FOOTER
# -------------------------------
st.markdown("---")
st.caption("Phase 2 – Hierarchical Semantic Tamil Reconstruction (HSTR)")


