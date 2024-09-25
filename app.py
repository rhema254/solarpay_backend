from flask import Flask, request, make_response
from flask_restx import Api, Resource, fields
from config import DevConfig
from models import *
from exts import db
from decouple import config
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



def send_payment_history(phone_number):
    pass

def get_next_due_date(phone_number):
    pass

def get_outstanding_balance(phone_number):
    pass

def get_last_payment_status(phone_number):
    pass
    




@app.route('/ussd/callback', methods=['POST'])
def ussd_callback():
    session_id = request.form.get('sessionId')
    service_code = request.form.get('serviceCode')
    phone_number = request.form.get('phoneNumber')
    text = request.form.get('text')
    print(phone_number)
    # Split the input text (user interaction)
    user_input = text.split('*')
    
    existing_user = User.get_by_phone_number(phone_number)  # Check if the user exists

   # Menu navigation logic
    if text == "":
        response = "CON Welcome to SolarPay\n"
        response += "0. Register into SolarPay "
        response += "1. Solar-Power For Home\n"
        response += "2. My Installment\n"
        response += "3. Report/Complaints\n"
        response += "4. Check Payment Status\n"

    elif text == "0":
        # Start registration process
        if existing_user:
            response = "END You are already registered with SolarPay."
        else:
            response = "CON Please enter your phone number:\n"
    elif text == "0*1":
        # Capture phone number
        phone_no = text.split("*")[1]  # Assuming the phone number is part of the text input
        if phone_no == phone_number:
            response = "CON Please enter the phone number you are currently using to make this request."
            response += "0. Go back\n"
        else:            
            response = f"CON Enter your first name:\n"  # Prompt for first name
    elif text == "0*1*0":
        response = "CON Please enter your phone number:\n"  # Prompt to re-enter phone number     

    elif text == "0*1*1":
        # Capture first name
        first_name = text.split("*")[2]
        response = f"CON Enter your last name:\n"  # Prompt for last name
    elif text == "0*1*1*":
        # Capture last name
        last_name = text.split("*")[3]
        response = f"CON Enter your county:\n"  # Prompt for county
    elif text == "0*1*1*1":
        # Capture county
        county = text.split("*")[4]
        response = f"CON Enter your nearest town:\n"  # Prompt for town
    elif text == "0*1*1*1*":
        # Capture town
        town = text.split("*")[5]
        
        # Now save the user to the database
        new_user = User(
            phone_number=phone_number,
            f_name= first_name,
            l_name= last_name,
            county=county,
            town=town
        )
        try:
            new_user.save()  # Save the new user
            response = "END Registration successful! Welcome to SolarPay.\n"


        except Exception as e:
            response = "END Registration failed. Please try again later.\n"


    elif text == "1":
        # Buy Solar Energy selected
        response = "CON Enter the desired Purchase Mode:\n (Solar-Power for Home costs Ksh.100,000)\n"
        response += "1. One-Time Payment\n"
        response += "2. Lipa Mdogo Mdogo\n"
    elif text == "1*1":
        # Buy Solar Energy selected
        response = "END An Agent will contact you soon:\n Solar power for Home goes for Ksh. 100,000\n END"
        # Send a follow-up message informing the user that their request has been recieved and an agent from Solar pay 
        # will call them to do a site visit or they visit the agent and get sorted out. 
    elif text == "1*2":
        #Enrol in a Lipa Mdogo Mdogo Scheme. 
        response = "END An Agent will contact you soon:\n Solar power for Home goes for Ksh. 100,000\n" 
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

    elif text == "3": 
        # This option allows users to send complaints or report technical problems to SolarPay.
        # A reference number should be sent for logging and resolution.
        response = "CON You want to report:\n"
        response += "1. Solar System Failure\n"
        response += "2. Billing or Payment Issues\n"
        response += "3. Account Issues\n"
        response += "4. Product/Service Support\n"
        response += "5. General Inquiries\n"

    elif text == "3*1": 
        # Solar System Failure submenu
        response = "CON Please select the type of failure:\n"
        response += "1. System not powering on\n"
        response += "2. Solar panel damage\n"
        response += "3. Battery not charging\n"
        response += "4. Inverter malfunction\n"
        response += "5. Other technical issue\n"

    elif text == "3*2": 
        # Billing or Payment Issues submenu
        response = "CON Please select your issue:\n"
        response += "1. Failed payment\n"
        response += "2. Incorrect billing amount\n"
        response += "3. Missed installment\n"
        response += "4. Request payment history\n"
        response += "5. Other billing issue\n"

    elif text == "3*3": 
        # Account Issues submenu
        response = "CON Please select the account issue:\n"
        response += "1. Account locked\n"
        response += "2. Incorrect personal details\n"
        response += "3. Change payment plan\n"
        response += "4. Unable to access account\n"
        response += "5. Other account issue\n"

    elif text == "3*4": 
        # Product/Service Support submenu
        response = "CON Please select the issue:\n"
        response += "1. Delayed service (installation, activation, etc.)\n"
        response += "2. Poor customer service experience\n"
        response += "3. Inquiry about product/service upgrade\n"
        response += "4. Service termination\n"
        response += "5. Other service issue\n"
    
    elif text == "3*5": 
        # General Inquiries submenu
        response = "CON Please select the type of inquiry:\n"
        response += "1. Inquiry about SolarPay services\n"
        response += "2. Request for documentation (receipts, invoices)\n"
        response += "3. Clarification on terms or conditions\n"
        response += "4. Request for customer support contact\n"
        response += "5. Other general inquiry\n"


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

    else:
        response = "END Invalid option. Please try again."

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