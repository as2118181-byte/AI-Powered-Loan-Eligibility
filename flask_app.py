from flask import Flask, request, render_template, redirect, url_for, jsonify
import pickle
import numpy as np
import requests
import json
import os # Import os for environment variables

# --- Configuration ---
# NOTE: The model is loaded from the root directory based on your provided path: 'model.pkl'
try:
    with open('model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
    print("Model loaded successfully from model.pkl")
except FileNotFoundError:
    print("ERROR: model.pkl not found. Ensure the model file is in the root directory.")
    model = None

# --- FIX: Changed '_name_' to '__name__' for the Flask initialization ---
app = Flask(__name__)

# --- Gemini API Configuration ---
# RECOMMENDATION: Use os.environ.get('GEMINI_API_KEY') instead of hardcoding or leaving empty.
# For local testing, you might need to set it in your shell or .env file.
API_KEY = os.environ.get('GEMINI_API_KEY', "") # Use environment variable if available
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={API_KEY}"

# --- Utility Routes (Login/Logout placeholders) ---
@app.route('/login')
def login():
    # Renders the login form (now a dummy gateway)
    return render_template("login.html")

@app.route('/logout')
def logout():
    # Renders the logout confirmation/page
    return render_template("logout.html")

@app.route('/create_account')
def create_account():
    # DUMMY: Redirects to the login page as account creation is disabled.
    return redirect(url_for('login'))
    
# --- Main Routes ---

@app.route('/')
def home():
    # Renders the main prediction form
    return render_template("index.html")

# NEW: Route to render the custom chatbot page
@app.route('/chatbot')
def chatbot_page():
    # Renders the interactive chatbot questionnaire
    return render_template("chatbot_page.html")

@app.route('/predict', methods=["GET", "POST"])
def predict():
    if model is None:
        return render_template("prediction.html", 
                               prediction_text="Error: Prediction model is not loaded. Please check server logs.")

    if request.method == 'POST':
        try:
            # --- 1. Get and Convert Form Data ---
            gender = request.form['gender']
            married = request.form['married']
            dependents = request.form['dependents']
            education = request.form['education']
            employed = request.form['employed']
            # Credit history is simplified to 0.0 or 1.0 in the form inputs
            credit = float(request.form['credit']) 
            area = request.form['area']
            ApplicantIncome = float(request.form['ApplicantIncome'])
            CoapplicantIncome = float(request.form['CoapplicantIncome'])
            LoanAmount = float(request.form['LoanAmount'])
            Loan_Amount_Term = float(request.form['Loan_Amount_Term'])

            # --- 2. Feature Engineering and One-Hot Encoding (Based on your logic) ---
            
            male = 1 if gender == "Male" else 0
            married_yes = 1 if married == "Yes" else 0
            not_graduate = 1 if education == "Not Graduate" else 0
            employed_yes = 1 if employed == "Yes" else 0

            dependents_1 = dependents_2 = dependents_3 = 0
            if dependents == '1': dependents_1 = 1
            elif dependents == '2': dependents_2 = 1
            elif dependents == '3+': dependents_3 = 1

            semiurban = urban = 0
            if area == "Semiurban": semiurban = 1
            elif area == "Urban": urban = 1

            # Log Transformations (Check for positive values before log)
            ApplicantIncomeLog = np.log(ApplicantIncome) if ApplicantIncome > 0 else 0
            totalincomelog = np.log(ApplicantIncome + CoapplicantIncome) if (ApplicantIncome + CoapplicantIncome) > 0 else 0
            LoanAmountLog = np.log(LoanAmount) if LoanAmount > 0 else 0
            Loan_Amount_Termlog = np.log(Loan_Amount_Term) if Loan_Amount_Term > 0 else 0

            features = [
                credit, ApplicantIncomeLog, LoanAmountLog, Loan_Amount_Termlog,
                totalincomelog, male, married_yes, dependents_1, dependents_2,
                dependents_3, not_graduate, employed_yes, semiurban, urban
            ]

            # --- 4. Prediction ---
            # Model expects a 2D array: [[feature1, feature2, ...]]
            prediction = model.predict([features])[0] 
            prediction_text = "Loan Status is: Yes (Approved)" if prediction != "N" else "Loan Status is: No (Rejected)"
            
            return render_template("prediction.html", prediction_text=prediction_text)

        except Exception as e:
            print(f"Prediction processing error: {e}")
            return render_template("prediction.html", prediction_text=f"An error occurred: {e}")

    else:
        return redirect(url_for('home'))

@app.route('/chat_api', methods=['POST'])
def chat_api():
    """Handles the user query and sends it to the Gemini API."""
    if not API_KEY:
        if not GEMINI_API_URL or GEMINI_API_URL.endswith("key="):
            return jsonify({"error": "Gemini API Key is missing. Please set the API_KEY."}), 500

    data = request.json
    chat_history = data.get('history', [])
    
    # System Instruction incorporating your 11 loan questions as context
    system_instruction_text = (
        "You are the 'Loan Eligibility Assistant,' a friendly and professional chatbot designed to guide users "
        "through the loan application process. Your role is to answer questions, explain concepts, and primarily "
        "help the user understand the factors affecting their loan eligibility. "
        "The 11 key factors in our model are: Gender, Marital Status, Dependents (0, 1, 2, 3+), Education (Graduate/Not Graduate), "
        "Self-Employed (Yes/No), Applicant Income, Coapplicant Income, Loan Amount, Loan Term (days), "
        "Credit History Score (binary 0/1 based on 850+), and Property Area (Urban/Semiurban/Rural). "
        "Use this context to give helpful and relevant advice without making a definitive prediction. "
        "Keep responses concise and helpful."
    )

    try:
        payload = {
            "contents": chat_history,
            "tools": [{"google_search": {} }],
            "systemInstruction": {"parts": [{"text": system_instruction_text}]}
        }

        # Making the API call to the Gemini endpoint
        response = requests.post(GEMINI_API_URL, json=payload)
        response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
        
        result = response.json()
        
        # Extract the generated text
        generated_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Sorry, I could not process that request.')
        
        return jsonify({"text": generated_text})

    except requests.exceptions.RequestException as e:
        print(f"API Request Error: {e}")
        return jsonify({"error": f"Failed to connect to the AI: {e}"}), 500
    except Exception as e:
        print(f"General Chat Error: {e}")
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)