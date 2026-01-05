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
# PAGE SETUP
# ---------------------------------------------------
st.set_page_config(
    page_title="Rural ACT – Phase 2",
    layout="wide"
)

st.title("🌾 Rural ACT – Any Language ➜ Perfect Tamil")
st.write(
    "Multilingual Input • Long Paragraph Support • Natural Tamil • Voice • PDF Download"
)

# ---------------------------------------------------
# NLTK SETUP
# ---------------------------------------------------
nltk.download("punkt")

# ---------------------------------------------------
# LOAD MULTILINGUAL MODEL (STABLE)
# ---------------------------------------------------
@st.cache_resource
def load_translation_model():
    model_name = "facebook/nllb-200-distilled-600M"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model

tokenizer, model = load_translation_model()

# ---------------------------------------------------
# LANGUAGE CODE MAP (NLLB)
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
# SMART CHUNKING FOR LONG PARAGRAPHS
# ---------------------------------------------------
def smart_chunk(text, max_len=400):
    sentences = sent_tokenize(text)
    chunks = []
    current = ""

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
# TAMIL GRAMMAR & TONE REFINEMENT (POST-EDITING)
# ---------------------------------------------------
def refine_tamil(text):
    rules = {
        "செய்ய வேண்டும்": "செய்ய வேண்டியது அவசியம்",
        "உடனடியாக": "உடனே",
        "புகார் பதிவு செய்ய வேண்டும்": "புகார் பதிவு செய்யலாம்",
        "அரசு வழங்குகிறது": "அரசு தருகிறது",
        "நீங்கள் வேண்டும்": "நீங்கள் செய்ய வேண்டும்"
    }

    for k, v in rules.items():
        text = text.replace(k, v)

    return text

# ---------------------------------------------------
# TRANSLATION: ANY LANGUAGE → TAMIL
# ---------------------------------------------------
def translate_to_tamil(text):
    try:
        detected_lang = detect(text)
    except:
        detected_lang = "en"

    src_lang_code = LANG_MAP.get(detected_lang, "eng_Latn")

    chunks = smart_chunk(text)
    tamil_chunks = []
    context_tail = ""

    for chunk in chunks:
        tokenizer.src_lang = src_lang_code

        input_text = context_tail + " " + chunk
        inputs = tokenizer(
            input_text,
            return_tensors="pt",
            truncation=True
        )

        outputs = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids("tam_Taml"),
            max_length=512
        )

        tamil = tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        tamil = refine_tamil(tamil)
        tamil_chunks.append(tamil)

        # carry last part for context continuity
        context_tail = tamil[-120:]

    return "\n".join(tamil_chunks)

# ---------------------------------------------------
# TAMIL VOICE (CHUNK-BASED)
# ---------------------------------------------------
def generate_voice(tamil_text):
    audio_files = []
    parts = smart_chunk(tamil_text, max_len=300)

    for part in parts:
        tts = gTTS(part, lang="ta")
        filename = f"voice_{uuid.uuid4()}.mp3"
        tts.save(filename)
        audio_files.append(filename)

    return audio_files

# ---------------------------------------------------
# PDF GENERATION
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
# USER INTERFACE
# ---------------------------------------------------
user_input = st.text_area(
    "Enter text in ANY language (long paragraphs supported):",
    height=220
)

if st.button("🔁 Translate to Tamil"):
    if not user_input.strip():
        st.warning("⚠️ Please enter text.")
        st.stop()

    with st.spinner("Translating and refining Tamil..."):
        tamil_text = translate_to_tamil(user_input)

    st.subheader("📌 Tamil Output")
    st.success(tamil_text)

    st.subheader("🔊 Tamil Voice")
    voices = generate_voice(tamil_text)
    for audio in voices:
        st.audio(audio)

    st.subheader("📄 Download as PDF")
    pdf_file = generate_pdf(tamil_text)

    with open(pdf_file, "rb") as f:
        st.download_button(
            label="Download PDF",
            data=f,
            file_name=pdf_file,
            mime="application/pdf"
        )

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")
st.caption(
    "Phase-2: Document-Level Hybrid Context-Aware Tamil Translation System"
)

