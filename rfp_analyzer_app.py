import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI

# -------------------------------
# Page setup
# -------------------------------
st.set_page_config(page_title="AI RFP Analyzer", layout="wide")
st.title("📄 AI RFP Analyzer – Smart Qualification & Red Flag Detector")
st.write(
    "Upload an RFP PDF, and the AI will extract a summary, identify red flags, "
    "and provide a qualification score."
)

# -------------------------------
# OpenAI setup
# -------------------------------
# On Streamlit Cloud, store your API key under Settings → Secrets → OPENAI_API_KEY
client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY", "YOUR_API_KEY_HERE"))

# -------------------------------
# Helper – Extract text from PDF
# -------------------------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text("text")
    return text

# -------------------------------
# File uploader
# -------------------------------
uploaded_file = st.file_uploader("📤 Upload RFP document (PDF only)", type=["pdf"])

if uploaded_file:
    with st.spinner("📚 Extracting text from PDF..."):
        rfp_text = extract_text_from_pdf(uploaded_file)
    st.success("✅ Text extracted successfully!")

    # -------------------------------
    # AI Prompt
    # -------------------------------
    prompt = f"""
    You are an expert RFP analyst. Analyze the following RFP text and provide three clear sections:

    1️⃣ **Summary (≤150 words)**  
    2️⃣ **Red Flags or Concerns** — list risks, unrealistic timelines, complex integrations, or penalties.  
    3️⃣ **Qualification Score (out of 10)** — based on fit, feasibility, and clarity.

    Keep the tone professional and concise.

    RFP TEXT:
    {rfp_text}
    """

    with st.spinner("🤖 Analyzing with AI..."):
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
        )

    analysis = response.choices[0].message.content
    st.subheader("🧠 AI Analysis")
    st.write(analysis)
