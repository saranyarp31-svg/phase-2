import streamlit as st
import nltk
import requests
import urllib.parse
import uuid
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

nltk.download("punkt")

# --------------------------------
# STREAMLIT SETUP
# --------------------------------
st.set_page_config(page_title="Rural ACT – Phase 2", layout="wide")
st.title("🌾 Rural ACT – Any Language → Perfect Tamil")
st.caption("No API Keys • Long Paragraph Safe • PDF + Voice")

# --------------------------------
# SEMANTIC CHUNKING
# --------------------------------
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

# --------------------------------
# ANY LANGUAGE → TAMIL (LibreTranslate)
# --------------------------------
def translate_to_tamil(text):
    url = "https://libretranslate.de/translate"
    payload = {
        "q": text,
        "source": "auto",
        "target": "ta",
        "format": "text"
    }

    response = requests.post(url, data=payload, timeout=20)
    return response.json()["translatedText"]

# --------------------------------
# TAMIL POLISHING (RULE-BASED)
# --------------------------------
def polish_tamil(text):
    replacements = {
        "நீங்கள்": "நீங்க",
        "உங்களுக்கு": "உங்களுக்கு",
        "இல்லை என்றால்": "இல்லைனா",
        "ஆகிறது": "ஆகுது",
        "மற்றும்": "மற்றும்",
    }

    for k, v in replacements.items():
        text = text.replace(k, v)

    return text

# --------------------------------
# TAMIL TTS (LONG SAFE)
# --------------------------------
def tamil_tts(text):
    files = []
    chunks = semantic_chunks(text, max_sentences=2)

    for chunk in chunks:
        encoded = urllib.parse.quote(chunk)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded}&tl=ta&client=tw-ob"
        r = requests.get(url)

        if r.status_code == 200:
            filename = f"tts_{uuid.uuid4()}.mp3"
            with open(filename, "wb") as f:
                f.write(r.content)
            files.append(filename)

    return files

# --------------------------------
# PDF GENERATION (LONG TEXT SAFE)
# --------------------------------
def generate_pdf(original, tamil):
    filename = f"RuralACT_{uuid.uuid4()}.pdf"
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()

    story = [
        Paragraph("<b>Original Input</b>", styles["Heading2"]),
        Paragraph(original, styles["Normal"]),
        Paragraph("<br/>", styles["Normal"]),
        Paragraph("<b>Tamil Output</b>", styles["Heading2"])
    ]

    for p in tamil.split("\n\n"):
        story.append(Paragraph(p, styles["Normal"]))

    doc.build(story)
    return filename

# --------------------------------
# UI
# --------------------------------
user_input = st.text_area(
    "📝 Enter text (ANY language, long paragraphs supported)",
    height=220
)

if st.button("🚀 Convert to Tamil"):
    if not user_input.strip():
        st.warning("Please enter text")
        st.stop()

    with st.spinner("🌍 Translating to Tamil..."):
        chunks = semantic_chunks(user_input)
        tamil_chunks = [translate_to_tamil(c) for c in chunks]
        tamil_text = "\n\n".join(tamil_chunks)
        tamil_text = polish_tamil(tamil_text)

    st.subheader("📌 Tamil Output")
    st.success(tamil_text)

    st.subheader("🔊 Tamil Voice")
    audio_files = tamil_tts(tamil_text)
    for f in audio_files:
        st.audio(f)

    pdf = generate_pdf(user_input, tamil_text)
    with open(pdf, "rb") as f:
        st.download_button(
            "📄 Download Tamil PDF",
            f,
            file_name="Tamil_Output.pdf",
            mime="application/pdf"
        )

st.markdown("---")
st.caption("Phase-2 | Rule-Guided Multistage Tamil Reconstruction (RG-MTR)")



