import streamlit as st
import fitz  # PyMuPDF for PDF text extraction
import google.generativeai as genai

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(page_title="AI RFP Analyzer – Freshworks Edition", layout="wide")
st.title("📄 AI RFP Analyzer – Freshworks Edition")
st.write(
    "Upload an RFP PDF. The AI will summarize the RFP, highlight key asks, "
    "identify red flags, check Freshworks product fit, and provide a qualification score."
)

# -------------------------------
# Gemini Setup
# -------------------------------
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-1.5-pro")

# -------------------------------
# Helper: Extract Text from PDF
# -------------------------------
def extract_text_from_pdf(uploaded_file):
    text = ""
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text("text")
    return text

# -------------------------------
# File Upload
# -------------------------------
uploaded_file = st.file_uploader("📤 Upload RFP document (PDF only)", type=["pdf"])

if uploaded_file:
    with st.spinner("📚 Extracting text from PDF..."):
        rfp_text = extract_text_from_pdf(uploaded_file)
    st.success("✅ Text extracted successfully!")

    # -------------------------------
    # Gemini Prompt
    # -------------------------------
    prompt = f"""
You are an expert RFP Analyst specializing in Freshworks solutions (Freshservice, Freshdesk, Freshsales, and Freshchat). 
You will analyze RFP text and respond ONLY using verified information from official Freshworks solution or documentation sources 
(such as https://support.freshworks.com, https://freshservice.com, https://freshdesk.com, and related Freshworks product pages). 

Your goal is to review the provided RFP and deliver the following structured analysis:

---

### 🧾 1. Summary of RFP Ask
Summarize the RFP's main objectives and key functional asks in simple, concise language (≤150 words).

---

### 💡 2. Key Requirements / Important Points
List the most important technical, functional, and business requirements mentioned in the RFP.  
Highlight any critical integration or customization needs.

---

### 🚩 3. Red Flags or Gaps
Analyze the RFP to identify **potential risks or red flags** when mapped against Freshworks product capabilities.  
Only use verified Freshworks product information for this.  
Flag issues such as:
- On-premise or self-hosted requirements (Freshworks is cloud-native → count as red flag)
- Strict data residency or custom hosting requirements
- Advanced customizations or integrations not supported natively
- Unrealistic SLAs, response timelines, or penalty clauses
- Conflicting compliance/security demands
- Overly short **proposal submission timelines**

Include the **reason for each red flag** clearly.

---

### 🕒 4. Timeline Analysis
Identify any **proposal due date** or delivery timeline mentioned in the RFP.  
Comment if the timeline is realistic or too short for standard Freshworks RFP turnaround (7 business days).

---

### ⚙️ 5. Scoring
Assign two separate scores (each out of 10):

- **Technical Fit Score** → Based on how well Freshworks products meet the RFP requirements.  
  (10 = Perfect Fit, 1 = Major Gaps)

- **Cloud Compatibility Score** → 
  - If the RFP demands **on-premise** → give 1/10 and flag as a red flag.  
  - If the RFP explicitly prefers **cloud** or **SaaS** → score 9–10.  
  - If unclear, score 5.

Then calculate the **Overall Qualification Score** = (Technical Fit + Cloud Compatibility) / 2.

---

### 🧠 6. Final Recommendation
Based on all the above, recommend one of:
✅ *Proceed* – Strong fit, minimal risks.  
⚠️ *Review with SE* – Moderate fit, needs validation.  
❌ *Do Not Proceed* – Major red flags, poor fit.

---

**RFP TEXT STARTS BELOW:**
{rfp_text}
"""

    # -------------------------------
    # Call Gemini API
    # -------------------------------
    with st.spinner("🤖 Analyzing with Gemini AI.."):
