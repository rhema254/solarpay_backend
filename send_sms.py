import africastalking
from decouple import config

# TODO: Initialize Africa's Talking

username = config('USERNAME')
api_key = config('API_KEY')

africastalking.initialize(username=username, api_key=api_key)
sms = africastalking.SMS


def send_sms(phone_number, message):
    """Send an SMS to the specified phone number."""
    try:
        response = sms.send(message, [phone_number])
        print("SMS sent successfully:", response)
    except Exception as e:
        print("Failed to send SMS:", e)
