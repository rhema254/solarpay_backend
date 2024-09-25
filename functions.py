

def convert_phone_number(phone_number):
    
    if phone_number.startswith("+254"):
        return "0" + phone_number[4:]
    else:
        return phone_number