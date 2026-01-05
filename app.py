import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from langdetect import detect
import nltk
from nltk.tokenize import sent_tokenize
from gtts import gTTS
import uuid
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

# ---------------------------------------------------
# Setup
# ---------------------------------------------------
st.set_page_config(page_title="Rural ACT – Phase 2", layout="wide")
st.title("🌾 Rural ACT – Any Language ➜ Perfect Tamil (Phase 2)")
st.write("Multilingual → Tamil | Long Paragraph | Voice | PDF")

nltk.download("punkt")

# ---------------------------------------------------
# Load NLLB Model (Multilingual)
# ---------------------------------------------------
@st.cache_resource
def load_model():
    model_name = "facebook/nllb-200-distilled-600M"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_model()

# ---------------------------------------------------
# Language Code Mapping (NLLB)
# ---------------------------------------------------
LANG_MAP = {
    "en": "eng_Latn",
    "hi": "hin_Deva",
    "ta": "tam_Taml",
    "te": "tel_Telu",
    "ml": "mal_Mlym",
    "kn": "kan_Knda",
    "fr": "fra_Latn",
    "de": "deu_Latn",
    "es": "spa_Latn",
    "it": "ita_Latn"
}

# ---------------------------------------------------
# Smart Chunking (Long Paragraph Support)
# ---------------------------------------------------
def smart_chunk(text, max_len=400):
    sentences = sent_tokenize(text)
    chunks, current = [], ""

    for s in sentences:
        if len(current) + len(s) <= max_len:
            current += " " + s
        else:
            chunks.append(current.strip())
            current = s

    if current:
        chunks.append(current.strip())

    return chunks

# ---------------------------------------------------
# Tamil Grammar & Tone Refinement (Post-Editing)
# ---------------------------------------------------
def refine_tamil(text):
    rules = {
        "செய்ய வேண்டும்": "செய்ய வேண்டியது அவசியம்",
        "உடனடியாக": "உடனே",
        "புகார் பதிவு செய்ய வேண்டும்": "புகார் பதிவு செய்யலாம்",
        "அரசு வழங்குகிறது": "அரசு தருகிறது"
    }
    for k, v in rules.items():
        text = text.replace(k, v)
    return text

# ---------------------------------------------------
# Translation Function (Any Language → Tamil)
# ---------------------------------------------------
def translate_to_tamil(text):
    src_lang = detect(text)
    src_code = LANG_MAP.get(src_lang, "eng_Latn")

    chunks = smart_chunk(text)
    tamil_chunks = []
    context_tail = ""

    for chunk in chunks:
        input_text = context_tail + " " + chunk
        tokenizer.src_lang = src_code

        inputs = tokenizer(input_text, return_tensors="pt", truncation=True)
        outputs = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids("tam_Taml"),
            max_length=512
        )

        tamil = tokenizer.decode(outputs[0], skip_special_tokens=True)
        tamil = refine_tamil(tamil)

        tamil_chunks.append(tamil)
        context_tail = tamil[-120:]

    return "\n".join(tamil_chunks)

# ---------------------------------------------------
# Tamil Voice (Chunk-based)
# ---------------------------------------------------
def generate_voice(text):
    files = []
    parts = smart_chunk(text, max_len=300)

    for part in parts:
        tts = gTTS(part, lang="ta")
        fname = f"voice_{uuid.uuid4()}.mp3"
        tts.save(fname)
        files.append(fname)

    return files

# ---------------------------------------------------
# PDF Generator
# ---------------------------------------------------
def generate_pdf(tamil_text):
    filename = "RuralACT_Tamil_Translation.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica", 12)
    y = height - 50

    c.drawString(40, y, "Rural ACT – Tamil Translation")
    y -= 25
    c.drawString(40, y, f"Generated on: {datetime.now()}")
    y -= 30

    for line in tamil_text.split("\n"):
        if y < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 50
        c.drawString(40, y, line)
        y -= 15

    c.save()
    return filename

# ---------------------------------------------------
# UI
# ---------------------------------------------------
user_input = st.text_area("Enter text in ANY language (long paragraph allowed):", height=200)

if st.button("Translate to Tamil"):
    if not user_input.strip():
        st.warning("Please enter text")
        st.stop()

    with st.spinner("Translating..."):
        tamil_text = translate_to_tamil(user_input)

    st.subheader("📌 Tamil Output")
    st.success(tamil_text)

    st.subheader("🔊 Tamil Voice")
    voices = generate_voice(tamil_text)
    for v in voices:
        st.audio(v)

    st.subheader("📄 Download")
    pdf = generate_pdf(tamil_text)
    with open(pdf, "rb") as f:
        st.download_button(
            "Download as PDF",
            f,
            file_name=pdf,
            mime="application/pdf"
        )

st.markdown("---")
st.caption("Phase-2: Document-Level Hybrid Context-Aware Tamil Translation")
