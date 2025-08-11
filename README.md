# Lexora_ai

Lexora_ai is a multi-functional AI-powered assistant designed to help users with **legal guidance**, **document handling**, **form understanding**, and **cybersecurity awareness**.  
It aims to make essential civic and legal processes easier, faster, and more accessible.

---

## 🚀 Key Features

### 1. 🏛 Legal Assistant
- Provides easy-to-understand answers to common legal queries.
- Guides users through basic legal procedures.
- Offers AI-powered explanations tailored to the Indian legal and civic context.

### 2. 📄 Document-related Assistant
- Helps in drafting and guiding official document formats (Aadhaar update, Voter ID applications, etc.).
- Suggests required details and formatting standards.
- Generates downloadable document drafts.

### 3. 📝 Form Reading & Understanding
- Reads scanned forms or uploaded PDFs.
- Explains the purpose and required fields in simple language.
- Highlights important sections for quick action.

### 4. 🔐 Cybersecurity Assistant
- Educates users on safe online practices.
- Detects possible phishing or scam indicators in text.
- Provides step-by-step guidance for filing online cyber complaints.

---

## 🛠 Tech Stack
- **Frontend:** Streamlit (or Flask UI)
- **Backend:** Python 3.8+
- **AI Processing:** LangChain + LLM APIs (Groq/OpenAI)
- **Authentication:** Supabase (Free Auth)
- **Document Parsing:** OCR (Tesseract/Gemini)
- **Security Module:** Custom threat detection logic

---

## 📦 Installation

```bash
git clone https://github.com/itzayush21/Lexora_ai.git
cd Lexora_ai
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
