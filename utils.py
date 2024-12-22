import re

DATE_FORMAT = "%d.%m.%Y"

def validate_and_convert(phone_number):
    pattern = r"^(\+7|7|8)(\d{10})$"
    match = re.match(pattern, phone_number)

    if match:
        normalized_number = '8' + match.group(2)
        return normalized_number
    else:
        return None

def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None