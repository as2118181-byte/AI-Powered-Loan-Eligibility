from flask import Flask, request, render_template
from markupsafe import escape 
import pickle
import numpy as np

# Use a relative path for portability
try:
    with open('model.pkl', 'rb') as model_file:
        model = pickle.load(model_file)
except FileNotFoundError:
    print("ERROR: model.pkl not found. Ensure the model file is in the same directory as Flask_app.py.")
    model = None # Handle missing model gracefully

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

# NEW ROUTE: For embedding the Streamlit Chatbot
@app.route('/chatbot')
def chatbot_page():
    # Renders the HTML file containing the IFrame to the Streamlit app
    return render_template("chatbot_page.html")

@app.route('/predict', methods = ["GET","POST"]) #get - typically used to show a blank prediction page or result page. #post-used to submit the form with input values that the server uses to make a prediction.
def predict():
    if model is None:
        return render_template("prediction.html", prediction_text="Error: Prediction model is not loaded.")

    if request.method == 'POST':
        # --- Logic remains untouched ---
        gender = request.form['gender']
        married = request.form['married']
        dependents = request.form['dependents']
        education = request.form['education']
        employed = request.form['employed']
        credit  = float(request.form['credit'])
        area = request.form['area']
        ApplicantIncome = float(request.form['ApplicantIncome']) #25000-> 0,1
        CoapplicantIncome = float(request.form['CoapplicantIncome'])
        LoanAmount = float(request.form['LoanAmount'])
        Loan_Amount_Term = float(request.form['Loan_Amount_Term'])


        #gender
        if (gender == "Male"):
            male = 1
        else:
            male = 0
        
        #married
        if (married == "Yes"):
            married_yes = 1
        else:
            married_yes = 0
        
        #dependents
        if ( dependents == '1'):
            dependents_1 = 1
            dependents_2 = 0
            dependents_3 = 0
        elif dependents == '2':
            dependents_1 = 0
            dependents_2 = 1
            dependents_3 = 0
        elif dependents == '3+':
            dependents_1 = 0
            dependents_2 = 0
            dependents_3 = 1
        else:
            dependents_1 = 0
            dependents_2 = 0
            dependents_3 = 0

        #education 
        if education =="Not Graduate":
            not_graduate = 1
        else:
            not_graduate = 0

        #employed
        if (employed == "Yes"):
            employed_yes = 1
        else:
            employed_yes = 0
        
        #property area
        if area == "Semiurban":
            semiurban = 1
            urban = 0
        elif area == "Urban":
            semiurban = 0
            urban = 1
        else:
            semiurban = 0
            urban = 0

        ApplicantIncomeLog = np.log(ApplicantIncome)
        totalincomelog = np.log(ApplicantIncome+CoapplicantIncome)
        LoanAmountLog = np.log(LoanAmount)
        Loan_Amount_Termlog = np.log(Loan_Amount_Term)

        prediction = model.predict([[credit,ApplicantIncomeLog,LoanAmountLog,Loan_Amount_Termlog,totalincomelog,male,married_yes,dependents_1,dependents_2,dependents_3,not_graduate,employed_yes,semiurban,urban]])
        
        #print(prediction)
        if(prediction=="N"):
            prediction = "No"
        else:
            prediction = "Yes"
        return render_template("prediction.html",prediction_text="Loan Status is: {}".format(prediction))
    else:
        # If accessing /predict directly via GET (which shouldn't happen based on the form)
        return render_template("prediction.html")
if __name__ == "__main__":
    app.run(debug=True)