from requests.auth import HTTPBasicAuth
import requests
from flask import request, current_app
import datetime
import base64
from decouple import config

# Load configuration values
consumer_key = config('CONSUMER_KEY')
consumer_secret = config('CONSUMER_SECRET')
callback_url = config('CALLBACK_URL')  # Make sure this is set in your .env

def getAccessToken():
    """ Getting the access token from Daraja endpoint """
    endpoint = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = response.json()
    return data["access_token"]

def initiate_payment(phone, amount):
    """ Initiates the payment request using STK Push """
    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    access_token = getAccessToken()
    headers = {"Authorization": f"Bearer {access_token}"}
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"174379{current_app.config['PASSKEY']}{timestamp}".encode('utf-8')).decode('utf-8')

    data = {
        "BusinessShortCode": "174379",
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": "174379",  # This is the business short code
        "PhoneNumber": phone,
        "CallBackURL": f"{callback_url}/callback",
        "AccountReference": "SolarPay Tech",
        "TransactionDesc": "Payment for Solar Energy"
    }

    response = requests.post(endpoint, json=data, headers=headers)
    return response.json()

# @app.route('/payment', methods=['POST'])
def payment():
    """ Endpoint to handle payment requests from the USSD interface """
    if request.method == 'POST':
        phone = request.form.get('phone')  # User's phone number
        amount = request.form.get('amount')  # Payment amount
        print(f"Processing payment for {phone} of amount {amount}")

        # Initiate payment using the STK push function
        payment_response = initiate_payment(phone, amount)
        
        return payment_response  # Return the payment response in JSON format

# @app.route('/callback', methods=['POST'])
def callback():
    """ Callback endpoint to handle payment confirmation from Safaricom """
    data = request.get_json()
    print("Payment callback data:", data)
    # Here you can process the callback data, e.g., confirm payment status and update the database
    return "ok"
