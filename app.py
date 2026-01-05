import streamlit as st
import nltk
import requests
import urllib.parse
import uuid
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# -------------------------------
# NLTK SETUP
# -------------------------------
nltk.download("punkt")
from nltk.tokenize import sent_tokenize

# -------------------------------
# STREAMLIT CONFIG
# -------------------------------
st.set_page_config(page_title="Rural ACT – Phase 2", layout="wide")
st.title("🌾 Rural ACT – Any Language → Tamil")
st.caption("No API keys • Long paragraph safe • PDF + Voice")

# -------------------------------
# SEMANTIC CHUNKING (LONG SAFE)
# -------------------------------
def semantic_chunks(text, max_sentences=4):
    sentences = sent_tokenize(text)
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
# ANY LANGUAGE → TAMIL (LibreTranslate)
# -------------------------------
def translate_to_tamil(text):
    url = "https://libretranslate.de/translate"
    payload = {
        "q": text,
        "source": "auto",
        "target": "ta",
        "format": "text"
    }
    r = requests.post(url, data=payload, timeout=30)
    return r.json()["translatedText"]

# -------------------------------
# TAMIL POLISHING (RULE BASED)
# -------------------------------
def polish_tamil(text):
    rules = {
        "நீங்கள்": "நீங்க",
        "இல்லை என்றால்": "இல்லைனா",
        "ஆகிறது": "ஆகுது",
        "மிகவும்": "ரொம்ப",
        "என்பது": "",
    }
    for k, v in rules.items():
        text = text.replace(k, v)
    return text

# -------------------------------
# TAMIL TTS (NO KEY)
# -------------------------------
def tamil_tts(text):
    audio_files = []
    chunks = semantic_chunks(text, max_sentences=2)

    for c in chunks:
        encoded = urllib.parse.quote(c)
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={encoded}&tl=ta&client=tw-ob"
        r = requests.get(url)
        if r.status_code == 200:
            fname = f"tts_{uuid.uuid4()}.mp3"
            with open(fname, "wb") as f:
                f.write(r.content)
            audio_files.append(fname)

    return audio_files

# -------------------------------
# PDF GENERATION (MULTI PAGE)
# -------------------------------
def generate_pdf(original, tamil):
    file = f"RuralACT_{uuid.uuid4()}.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()

    story = [
        Paragraph("<b>Original Input</b>", styles["Heading2"]),
        Paragraph(original, styles["Normal"]),
        Paragraph("<br/>", styles["Normal"]),
        Paragraph("<b>Tamil Output</b>", styles["Heading2"]),
    ]

    for para in tamil.split("\n\n"):
        story.append(Paragraph(para, styles["Normal"]))

    doc.build(story)
    return file

# -------------------------------
# UI
# -------------------------------
text = st.text_area(
    "📝 Enter text (ANY language, long paragraph supported)",
    height=250
)

if st.button("🚀 Convert to Tamil"):
    if not text.strip():
        st.warning("Please enter some text")
        st.stop()

    with st.spinner("🌍 Translating..."):
        parts = semantic_chunks(text)
        tamil_parts = [translate_to_tamil(p) for p in parts]
        tamil_text = "\n\n".join(tamil_parts)
        tamil_text = polish_tamil(tamil_text)

    st.subheader("📌 Tamil Output")
    st.success(tamil_text)

    st.subheader("🔊 Tamil Voice")
    for audio in tamil_tts(tamil_text):
        st.audio(audio)

    pdf = generate_pdf(text, tamil_text)
    with open(pdf, "rb") as f:
        st.download_button(
            "📄 Download Tamil PDF",
            f,
            file_name="Tamil_Output.pdf",
            mime="application/pdf"
        )

st.markdown("---")
st.caption("Phase-2 | Long-form multilingual Tamil translation engine")



