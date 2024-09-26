from flask import Flask, request, make_response
from flask_restx import Api, Resource, fields
from config import DevConfig
from models import *
from exts import db
from decouple import config
from functions import *
from send_sms import *
# from flask_cors import CORS
# from flask_sqlalchemy import SQLAlchemy


# Import the payment function
from mpesa import initiate_payment

app = Flask(__name__)
app.config.from_object(DevConfig)
app.config['SQLALCHEMY_DATABASE_URI'] = config('SQLALCHEMY_DATABASE_URI')
db.init_app(app)


callback_url = config('CALLBACK_URL')

@app.route('/', methods=['GET'])
def index():
    return 'hello world'


@app.route('/ussd/callback', methods=['POST'])
def ussd_callback():
    session_id = request.form.get('sessionId')
    service_code = request.form.get('serviceCode')
    phone = request.form.get('phoneNumber')
    phone_number = convert_phone_number(phone)  # Convert phone to standard format
    text = request.form.get('text')

    print(phone_number)
    # Split the input text (user interaction)
    user_input = text.split('*')
    
    existing_user = User.get_by_phone_number(phone_number)  # Check if the user exists

    # Menu navigation logic
    if text == "":
        response = "CON Welcome to SolarPay\n"
        response += "0. Register into SolarPay\n"
        response += "1. Solar-Power For Home\n"
        response += "2. My Installment\n"
        response += "3. Report/Complaints\n"
        response += "4. Check Payment Status\n"

    elif text == "0":  
        # Start registration process
        if existing_user:
            response = "END You are already registered with SolarPay."
        else:
            response = "CON Please enter OFFICIAL your First Name as It appears on Your National ID: \n"

    elif len(user_input) == 2 and user_input[0] == "0" and user_input[1].isalpha():  # Capture first name
        f_name = user_input[1]
        response = "CON Please enter your OFFICIAL Last Name as it appears on Your National ID:\n"

    elif len(user_input) == 3 and user_input[0] == "0" and user_input[2].isalpha():  # Capture last name
        l_name = user_input[2]
        response = "CON Enter your County:\n"

    elif len(user_input) == 4 and user_input[0] == "0":  # Capture county
        county_name = user_input[3]
        if county_name.isalpha():
            response = "CON Enter your Nearest Town:\n"
        else:
            response = "CON Invalid County. Please enter your County again:\n"

    elif len(user_input) == 5 and user_input[0] == "0" and user_input[4].isalpha():  # Capture town
        town = user_input[4]
        # Save user to the database
        new_user = User(
            phone_number=phone_number,
            f_name=user_input[1],  # First name
            l_name=user_input[2],  # Last name
            county=user_input[3],
            town=user_input[4]
        )
        try:
            new_user.save()  # Save the new user
            response = f"Welcome to SolarPay {f_name} {l_name}!!\nThank you for signing up. An agent will contact you within the next 24hours to get to give you a brief of our solar solutions.\n\n Regards,\nSolarPay"
            send_sms().send()
        except Exception as e:
            print(e)
            response = "END Registration failed. Please try again later.\n"
    
    
    elif text == "1":
        # Buy Solar Energy selected
        response = "CON Enter the desired Purcha`se Mode:\n (Solar-Power for Home costs Ksh.100,000)\n"
        response += "1. One-Time Payment\n"
        response += "2. Lipa Mdogo Mdogo\n"
    elif text == "1*1":
        # Buy Solar Energy selected
        response = "END An Agent will contact you soon:\n Solar power for Home goes for Ksh. 100,000\n END"
        message = f"Welcome to SolarPay {f_name} {l_name}!!\nThank you for signing up. An agent will contact you within the next 24hours to get to give you a brief of our solar solutions.\n\n Regards,\nSolarPay"
        send_sms(message, phone_number)
        # Send a follow-up message informing the user that their request has been recieved and an agent from Solar pay 
        # will call them to do a site visit or they visit the agent and get sorted out. 
    elif text == "1*2":
        #Enrol in a Lipa Mdogo Mdogo Scheme. 
        response = "END An Agent will contact you soon:\n Solar power for Home goes for Ksh. 100,000\n" 
        message = f"Welcome to SolarPay {f_name} {l_name}!!\nThank you for signing up. An agent will contact you within the next 24hours to get to give you a brief of our solar solutions.\n\n Regards,\nSolarPay"
        send_sms(message, phone_number)
        # Send a follow-up message informing the user that their request has been recieved and an agent from Solar pay 
        # will call them to do a site visit or they visit the agent and get sorted out and also verify their eligibility
        # for the Buy Now Pay Later scheme. Tell them to prepare their financial statements and records(M-Pesa, Bank)

    elif text == "2":
        response = "CON Welcome to your BYPL\n\n"
        response += "1. Check my Payment Status\n"
        response += "2. Pay installment\n"
        response += "3. Check Previous Payments\n"

    elif text == "2*1":
        # payment_status , Amount_due, Previous Payment, Upcoming payment, previous_Amount_paid
        # Checks whether the user is on course with payment/ or in-default. Sends a message after this confirming the same. 
        # if payment_status == "On-course": response should affirm the same. else, should send a warning of the days left to pay.
        response = "END You're on course with payment for now."

    elif text == "2*2":
        # Select installment. If a user has a missed installment, they should only be able to pay for the missed installment. 
        response = "CON Select which installment you want to make:\n"
        response += "1. Upcoming Installment\n"
        response += "2. Missed Installment\n"

    elif text == "2*2*1":
        #If a user is on course with their installment, then they can initiate payment for their installment.  
        # The amount should be dynamic, depending on the payment plan a user is on or the custom payment plan that a user agreed on.   
        # An sms should be sent upon receipt of the callback response confirming pay.
        amount = 1
        payment_response = initiate_payment(phone_number, amount, callback_url)
        send_sms(message, recipients=phone_number)
        response = f"END You will be billed Ksh {amount} in installments. Payment status: {payment_response['ResponseDescription']}"

    elif text == "2*2*2":
        # As mentioned, this should only be accessible if the condition payment_status is defaulted. 
        # The amount should be the same amount specified in the payment plan. 
        # In the event a user literally pays mdogo mdogo, the amount will be a deduction of the total sum paid, from the expected amount
        # An sms should be sent upon receipt of the callback response confirming pay.
        amount = 1
        payment_response = initiate_payment(phone_number, amount, callback_url)
        response = f"END You will be billed Ksh {amount} in installments. Payment status: {payment_response['ResponseDescription']}"

    elif text == "2*3":
        # This should send an sms to a user with the last 5 payments. 
        response = "END You will receive a message with your payment history shortly\n"

    
    if text == "3": 
        # Main complaints menu
        response = "CON What issue would you like to report?\n"
        response += "1. Power Supply Problems\n"
        response += "2. Payment or Billing Issues\n"

      
    elif text == "3*1": 
        # Power Supply Problems submenu
        response = "CON Please specify the issue:\n"
        response += "1. Solar system not turning on\n"
        response += "2. Power outage or low power\n"
        response += "3. System shutting down unexpectedly\n"
        response += "4. Other power-related issue\n"

    elif text == "3*1*1":
        # Solar system not turning on
        category = "Power Supply Problems"
        description = "Solar system not turning on"
        user = User.get_by_phone_number(phone_number)
        new_complaint = Complaint(user_id=user.id, category=category, description=description)
        new_complaint.save()
        response = "END Your complaint about the solar system not turning on has been logged. We will resolve it shortly."

    elif text == "3*1*2":
        # Power outage or low power
        category = "Power Supply Problems"
        description = "Power outage or low power"
        user = User.get_by_phone_number(phone_number)
        new_complaint = Complaint(user_id=user.id, category=category, description=description)
        new_complaint.save()
        response = "END Your complaint about power outage or low power has been logged. We will resolve it shortly."

    elif text == "3*1*3":
        # System shutting down unexpectedly
        category = "Power Supply Problems"
        description = "System shutting down unexpectedly"
        user = User.get_by_phone_number(phone_number)
        new_complaint = Complaint(user_id=user.id, category=category, description=description)
        new_complaint.save()
        response = "END Your complaint about the system shutting down unexpectedly has been logged. We will resolve it shortly."

    elif text == "3*1*4":
        # Other power-related issue
        category = "Power Supply Problems"
        description = "Other power-related issue"
        user = User.get_by_phone_number(phone_number)
        new_complaint = Complaint(user_id=user.id, category=category, description=description)
        new_complaint.save()
        response = "END Your complaint has been logged. We will resolve it shortly."

    elif text == "3*2": 
        # Payment or Billing Issues submenu
        response = "CON Please specify your issue:\n"
        response += "1. Payment not reflected\n"
        response += "2. Incorrect billing amount\n"
        response += "3. Missed payment reminders\n"
        response += "4. Overcharge or duplicate payment\n"
        response += "5. Other billing issue\n"

    elif text == "3*2*1":
        category = "Payment or Billing Issues"
        description = "Payment not reflected"
        user = User.get_by_phone_number(phone_number)
        new_complaint = Complaint(user_id=user.id, category=category, description=description)
        new_complaint.save()
        response = "END Your complaint about payment not being reflected has been logged. We will resolve it shortly."

    elif text == "3*2*2":
        category = "Payment or Billing Issues"
        description = "Incorrect billing amount"
        user = User.get_by_phone_number(phone_number)
        new_complaint = Complaint(user_id=user.id, category=category, description=description)
        new_complaint.save()
        response = "END Your complaint about incorrect billing amount has been logged. We will resolve it shortly."

    elif text == "3*2*3":
        category = "Payment or Billing Issues"
        description = "Missed payment reminders"
        user = User.get_by_phone_number(phone_number)
        new_complaint = Complaint(user_id=user.id, category=category, description=description)
        new_complaint.save()
        response = "END Your complaint about missed payment reminders has been logged. We will resolve it shortly."

    elif text == "3*2*4":
        category = "Payment or Billing Issues"
        description = "Overcharge or duplicate payment"
        user = User.get_by_phone_number(phone_number)
        new_complaint = Complaint(user_id=user.id, category=category, description=description)
        new_complaint.save()
        response = "END Your complaint about overcharge or duplicate payment has been logged. We will resolve it shortly."

    elif text == "3*2*5":
        category = "Payment or Billing Issues"
        description = "Other billing issue"
        user = User.get_by_phone_number(phone_number)
        new_complaint = Complaint(user_id=user.id, category=category, description=description)
        new_complaint.save()
        response = "END Your complaint has been logged. We will resolve it shortly."

    elif text == "4":
        # Check Payment Status submenu
        response = "CON Please select the type of payment status inquiry:\n"
        response += "1. Check last payment status\n"
        response += "2. Check outstanding balance\n"
        response += "3. View full payment history\n"
        response += "4. Check next installment due date\n"
        response += "5. Other payment-related inquiries\n"
        response += "0. Back\n" 


    elif text == "4*1":
        # Handle check last payment status
        payment_status = get_last_payment_status(phone_number)  # Call a function to check payment status
        response = f"END Your last payment status is: {payment_status}."

    elif text == "4*2":
        # Handle check outstanding balance
        outstanding_balance = get_outstanding_balance(phone_number)  # Call a function to check balance
        response = f"END Your outstanding balance is: Ksh {outstanding_balance}."

    elif text == "4*3":
        # Handle view full payment history
        response = "END Your full payment history has been sent to your phone via SMS."
        send_payment_history(phone_number)  # Function to send the user their payment history

    elif text == "4*4":
        
        # Handle check next installment due date
        next_due_date = get_next_due_date(phone_number)  # Call a function to retrieve next due date
        response = f"END Your next installment is due on: {next_due_date}."

    # Return the response as plain text
    return make_response(response, 200)



@app.route('/payment', methods=['POST'])
def payment():
    """ Endpoint to handle payment requests from the USSD interface """
    if request.method == 'POST':
        phone = request.form.get('phone')  # User's phone number
        amount = request.form.get('amount')  # Payment amount
        print(f"Processing payment for {phone} of amount {amount}")

        # Initiate payment using the STK push function
        # callback_url = request.url_root  # Get the root URL for the callback
        payment_response = initiate_payment(phone, amount, callback_url )
        
        return payment_response  # Return the payment response in JSON format

@app.route('/callback', methods=['POST'])
def callback():
    """ Callback endpoint to handle payment confirmation from Safaricom """
    data = request.get_json()
    print("Payment callback data:", data)
    # Here you can process the callback data, e.g., confirm payment status and update the database
    return "ok"


@app.route('/incoming-messages', methods=[])




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



if __name__ == "__main__":
    with app.app_context():
        app.run(
            debug=True
            )

        
     













    # elif text == "1*2":
    #     # Buy Solar Energy selected
    #     response = "CON Choose your payment plan:\n"
    #     response += "1. Standard Plan (12 installments)\n"
    #     response += "2. Flexible Plan (24 installments)\n"
    #     response += "3. Low-Income Support Plan (36 installments)\n"