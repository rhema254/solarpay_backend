from flask import Flask, request, make_response
from flask_restx import Api, Resource, fields
from config import DevConfig
from models import *
from exts import db
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

# Import the payment function
from mpesa import initiate_payment

@app.route('/ussd/callback', methods=['POST'])
def ussd_callback():
    session_id = request.form.get('sessionId')
    service_code = request.form.get('serviceCode')
    phone_number = request.form.get('phoneNumber')
    text = request.form.get('text')

    # Split the input text (user interaction)
    user_input = text.split('*')

    # Menu navigation logic
    if text == "":
        response = "CON Welcome to SolarPay\n"
        response += "1. Buy Solar Energy\n"
        response += "2. Check Payment Status\n"
    elif text == "1":
        # Buy Solar Energy selected
        response = "CON Choose your payment plan:\n"
        response += "1. Standard Plan (3 installments)\n"
        response += "2. Flexible Plan (6 installments)\n"
        response += "3. Low-Income Support Plan (12 installments)\n"
    elif text == "1*1":
        # Standard Plan selected
        response = "CON You will pay Ksh 5,000 in 3 installments of Ksh 5,000.\n"
        response += "CON Enter the amount you wish to pay:\n"
    elif text == "1*2":
        # Flexible Plan selected
        response = "CON You will pay Ksh 2,500 in 6 installments of Ksh 2,500.\n"
        response += "CON Enter the amount you wish to pay:\n"
    elif text == "1*3":
        # Low-Income Support Plan selected
        response = "CON You will pay Ksh 1,250 in 12 installments of Ksh 1,250.\n"
        response += "CON Enter the amount you wish to pay:\n"
    elif len(user_input) == 3:
        # Handle user entering an amount for Standard Plan
        amount = user_input[2]
        payment_response = initiate_payment(phone_number, amount, request.url_root)
        response = f"END You will be billed Ksh {amount} in installments. Payment status: {payment_response['ResponseDescription']}"
    elif len(user_input) == 4 and user_input[1] == "2":
        # Handle user entering an amount for Flexible Plan
        amount = user_input[3]
        payment_response = initiate_payment(phone_number, amount, request.url_root)
        response = f"END You will be billed Ksh {amount} in installments. Payment status: {payment_response['ResponseDescription']}"
    elif len(user_input) == 4 and user_input[1] == "3":
        # Handle user entering an amount for Low-Income Support Plan
        amount = user_input[3]
        payment_response = initiate_payment(phone_number, amount, request.url_root)
        response = f"END You will be billed Ksh {amount} in installments. Payment status: {payment_response['ResponseDescription']}"
    else:
        response = "END Invalid option. Please try again."

    # Return the response as plain text
    return make_response(response, 200)


@app.route('/enroll', methods=['POST'])
def enroll_user():
    phone_number = request.form.get('phone_number')
    payment_plan = request.form.get('payment_plan')

    # Find the user in the database
    user = User.query.filter_by(phone_number=phone_number).first()

    if user:
        user.payment_plan = payment_plan  # Update user's payment plan
        db.session.commit()  # Commit changes to the database
        return "User enrolled successfully", 200
    else:
        return "User not found", 404


@app.route('/payment', methods=['POST'])
def payment():
    """ Endpoint to handle payment requests from the USSD interface """
    if request.method == 'POST':
        phone = request.form.get('phone')  # User's phone number
        amount = request.form.get('amount')  # Payment amount
        print(f"Processing payment for {phone} of amount {amount}")

        # Initiate payment using the STK push function
        callback_url = request.url_root  # Get the root URL for the callback
        payment_response = initiate_payment(phone, amount, callback_url)
        
        return payment_response  # Return the payment response in JSON format

@app.route('/callback', methods=['POST'])
def callback():
    """ Callback endpoint to handle payment confirmation from Safaricom """
    data = request.get_json()
    print("Payment callback data:", data)
    # Here you can process the callback data, e.g., confirm payment status and update the database
    return "ok"





if __name__ == "__main__":
    app.run(debug=True)
