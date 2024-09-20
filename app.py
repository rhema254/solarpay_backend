from flask import Flask, request, make_response

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return 'Welcome to SolarPay'

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
        # Initial interaction, present main menu
        response = "CON Welcome to SolarPay\n"
        response += "1. Buy Solar Energy\n"
        response += "2. Check Payment Status\n"
    elif text == "1":
        # Buy Solar Energy selected
        response = "CON Choose your payment plan:\n"
        response += "1. Pay in 3 installments\n"
        response += "2. Pay in 6 installments\n"
    elif text == "1*1":
        # Pay in 3 installments selected
        response = "CON Enter the amount you wish to pay:\n"
    elif len(user_input) == 3:
        # Handle user entering an amount
        amount = user_input[2]
        response = f"END You will be billed Ksh {amount} in 3 installments."
    else:
        response = "END Invalid option. Please try again."

    # Return the response as plain text
    return make_response(response, 200)

if __name__ == "__main__":
    app.run(debug=True)
