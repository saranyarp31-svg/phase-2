import sys
st.write(sys.version)
import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from langdetect import detect
import nltk
from nltk.tokenize import sent_tokenize

# Download tokenizer data
nltk.download("punkt")

st.set_page_config(page_title="Multilingual → Tamil Translator", layout="wide")

st.title("🌍 Multilingual → Tamil Translator")
st.caption("Powered by IndicTrans2 | Supports long paragraphs & new words")

@st.cache_resource
def load_model():
    model_name = "ai4bharat/indictrans2-m2m-100"
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name, trust_remote_code=True)
    return tokenizer, model

tokenizer, model = load_model()

text = st.text_area(
    "Enter text in ANY language",
    height=220,
    placeholder="Type English / Hindi / Telugu / Malayalam / any language..."
)

if st.button("Translate to Tamil"):
    if not text.strip():
        st.warning("Please enter some text")
    else:
        with st.spinner("Translating..."):
            sentences = sent_tokenize(text)
            translated_sentences = []

            for sent in sentences:
                inputs = tokenizer(
                    sent,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=512
                )

                outputs = model.generate(
                    **inputs,
                    max_length=512,
                    num_beams=5
                )

                tamil = tokenizer.decode(outputs[0], skip_special_tokens=True)
                translated_sentences.append(tamil)

            final_output = " ".join(translated_sentences)

        st.subheader("✅ Tamil Translation")
        st.success(final_output)
