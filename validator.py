# TVS_DND/validator.py

import re


def clean_mobile_number(mobile):
    """
    Cleans and validates mobile number.
    Returns valid 10-digit number or None.
    """

    if mobile is None:
        return None

    # Convert to string
    mobile = str(mobile).strip()

    # Keep only digits
    mobile = re.sub(r"\D", "", mobile)

    # Validate 10 digits
    if re.fullmatch(r"\d{10}", mobile):
        return mobile

    return None


def is_active_record(value):
    """
    Checks whether IS_ACTIVE is Y.
    """

    if value is None:
        return False

    return str(value).strip().upper() == "Y"