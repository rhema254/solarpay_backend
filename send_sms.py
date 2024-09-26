import africastalking
import africastalking.Service
from decouple import config

# Initialize Africa's Talking
username = config('USERNAME')
api_key = config('API_KEY')

africastalking.initialize(username=username, api_key=api_key)
sms = africastalking.SMS




def send_sms(message, recipients):
    """
    Function to send SMS using Africa's Talking
    :param message: The message content to be sent
    :param recipients: List of phone numbers (in international format) to send SMS to
    """
    # Set a default shortCode or senderId (optional)
    sender = ""
    
    try:
        # Send the SMS
        response = sms.send(message, recipients, sender)
        print(f"SMS sent successfully: {response}")
    except Exception as e:
        print(f"Error sending SMS: {e}")
