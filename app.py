import streamlit as st
from langdetect import detect
import re

# ----------------------------
# Basic multilingual → Tamil mapping (extendable)
# ----------------------------
BASIC_DICT = {
    "hello": "வணக்கம்",
    "hi": "வணக்கம்",
    "how": "எப்படி",
    "are": "",
    "you": "நீங்கள்",
    "i": "நான்",
    "am": "இருக்கிறேன்",
    "fine": "நன்றாக",
    "what": "என்ன",
    "is": "",
    "your": "உங்கள்",
    "name": "பெயர்",
    "thank": "நன்றி",
    "thanks": "நன்றி",
    "good": "நல்ல",
    "morning": "காலை",
    "evening": "மாலை",
    "night": "இரவு"
}

# ----------------------------
# Sentence cleaner
# ----------------------------
def clean_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s\.]", "", text)
    return text

# ----------------------------
# Core translation logic
# ----------------------------
def translate_to_tamil(sentence):
    words = sentence.split()
    tamil_words = []

    for w in words:
        tamil_words.append(BASIC_DICT.get(w, w))  # new words stay unchanged

    # Tamil SOV order (simple heuristic)
    if len(tamil_words) > 2:
        tamil_words = tamil_words[1:] + tamil_words[:1]

    return " ".join(filter(None, tamil_words))

# ----------------------------
# Paragraph handler
# ----------------------------
def process_paragraph(text):
    sentences = re.split(r"[.!?]", text)
    output = []

    for s in sentences:
        s = clean_text(s.strip())
        if s:
            output.append(translate_to_tamil(s))

    return "। ".join(output)

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="Multilingual → Tamil Translator", layout="centered")

st.title("🌍 Multilingual to Tamil Translator (Rule-Based)")
st.caption("Phase-2 | Offline | Model-Free | Python 3.13 Safe")

input_text = st.text_area("Enter text (any language, long paragraphs supported):", height=180)

if st.button("Translate to Tamil"):
    if not input_text.strip():
        st.warning("Please enter some text.")
    else:
        try:
            lang = detect(input_text)
            result = process_paragraph(input_text)

            st.success("Translation completed")
            st.markdown("### 📝 Output (Tamil)")
            st.write(result)

            st.markdown("### ℹ️ Detected Language")
            st.code(lang)

        except Exception as e:
            st.error(f"Error: {e}")

