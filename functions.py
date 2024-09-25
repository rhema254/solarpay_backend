

def convert_phone_number(phone_number):
    
    if phone_number.startswith("+254"):
        return "0" + phone_number[4:]
    else:
        return phone_number
    

def send_payment_history(phone_number):
    pass

def get_next_due_date(phone_number):
    pass

def get_outstanding_balance(phone_number):
    pass

def get_last_payment_status(phone_number):
    pass
    
