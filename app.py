from flask import Flask, render_template
from flask import request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/feature')
def feature():
    return render_template('feature.html')

@app.route('/legal-assistant')
def legal_assistant():
    return render_template('legal_assistant.html')

@app.route("/get-response", methods=["POST"])
def get_response():
    user_msg = request.json.get("message")
    
    # Simulated basic legal AI reply (replace with real model/API)
    response = legal_ai_response(user_msg)
    return jsonify({"reply": response})

def legal_ai_response(query):
    # Placeholder logic – replace with real RAG model or OpenAI/Gemini calls
    if "FIR" in query.lower():
        return "An FIR (First Information Report) is a written document prepared by the police when they receive information about a cognizable offence."
    elif "divorce" in query.lower():
        return "In India, divorce is governed by various personal laws. The Hindu Marriage Act, 1955 allows for both mutual and contested divorce."
    else:
        return "I'm an AI Legal Assistant. Please ask a specific question related to Indian law, like 'How to file an FIR?'"
    

@app.route("/doc-builder")
def doc_builder():
    return render_template("doc_builder.html")


@app.route("/extract-info", methods=["POST"])
def extract_info():
    file = request.files["document"]
    text = '''
        "Extracted text will appear here. "
        "Please upload a PDF or image document to extract its contents. "
        "Supported formats: PDF, JPG, PNG. "
        "If you need help, contact support." '''


    '''if file.filename.endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        for page in doc:
            text += page.get_text()
    else:
        image = Image.open(file.stream)
        text = pytesseract.image_to_string(image)'''

    return jsonify({"text": text})

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "")
    context = data.get("context", "")

    # Dummy AI logic (replace with real LLM/RAG)
    answer = "Based on the document, here's a simulated answer to your question."
    if "term" in question.lower():
        answer = "The term of the agreement seems to be 12 months, as mentioned in the context."
    elif "parties" in question.lower():
        answer = "The agreement is made between Party A and Party B."

    return jsonify({"answer": answer})

chat_history = []

@app.route("/doc-guild")
def guild():
    return render_template("doc_guild.html")

@app.route("/govt-chat", methods=["POST"])
def govt_chat():
    user_message = request.json.get("message", "").lower()
    chat_history.append({"role": "user", "message": user_message})

    reply = get_doc_info(user_message)
    chat_history.append({"role": "bot", "message": reply})

    return jsonify({"reply": reply})

def get_doc_info(msg):
    if "aadhaar" in msg:
        if "document" in msg or "require" in msg:
            return "You'll need: Proof of Identity, Proof of Address (like Voter ID, Utility Bill), and DOB proof (like Birth Certificate)."
        return """To apply for Aadhaar:
1. Visit the nearest Aadhaar centre or book online at https://uidai.gov.in.
2. Fill out the form, carry valid ID and address proof.
3. Biometrics will be captured. Aadhaar arrives in 2–3 weeks."""

    elif "pan" in msg:
        return """Apply for PAN at https://www.tin-nsdl.com or UTI.
- Fill Form 49A
- Upload ID, address proof, and photo
- Pay ₹107 online
- PAN card delivered in 15 days"""

    elif "passport" in msg:
        return """To apply for a passport:
1. Go to https://passportindia.gov.in
2. Register and apply
3. Schedule an appointment at PSK
4. Carry original documents
5. Police verification required"""

    elif "voter" in msg or "voter id" in msg:
        return """To get a Voter ID:
1. Go to https://www.nvsp.in
2. Fill Form 6 for new voters
3. Upload address and age proof
4. Booth officer will verify it."""

    return "Sorry, I don't have information on that. Please ask about Aadhaar, PAN, Passport, or Voter ID."

@app.route("/form-gen")
def form_gen():
    return render_template("form_generator.html")

@app.route("/form-generator", methods=["GET", "POST"])
def form_generator():
    if request.method == "POST":
        form_type = request.form.get("form_type")
        details = request.form.get("details")

        if not form_type or not details:
            return render_template("form_generator.html", error="Please select a form and provide details.")

        # Create form based on type
        if form_type == "declaration":
            content = f"DECLARATION FORM\n\nI hereby declare:\n\n{details}\n\nDate: __________\nSignature: __________"
        elif form_type == "application":
            content = f"APPLICATION FORM\n\nTo whom it may concern,\n\n{details}\n\nSincerely,\nName: __________\nDate: __________"
        elif form_type == "id_verification":
            content = f"ID VERIFICATION FORM\n\nThis document verifies the identity of:\n\n{details}\n\nVerified by: __________\nSignature: __________"
        else:
            content = "Invalid form type."

        # Return as downloadable file
        '''buffer = io.BytesIO()
        buffer.write(content.encode("utf-8"))
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name="generated_form.txt", mimetype="text/plain")'''
        return render_template("form_generator.html", content=content)
    return render_template("form_generator.html")

@app.route("/cyber-assist")
def cyber_assist():
    return render_template("cyber.html")

if __name__ == '__main__':
    app.run(debug=True)
