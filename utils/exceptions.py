from fastapi import HTTPException


class NotFound(Exception):
    pass


class HTTPError(HTTPException):
    pass


def decode_error_message(error_type, field, required):
    if error_type == "string_too_short":
        return f"{field} must at least be {required[0]} characters."
    if error_type == "string_too_long":
        return f"{field} must at most be {required[0]} characters."
    if error_type == "missing":
        return f"{field} is required."
    if error_type == "value_error":
        return f"{field} provided is invalid."

    return "An error occurred validating your data."


def validate_wtc_email(email: str):
    email_split = email.split("@")
    if email_split[1].lower() != "student.wethinkcode.co.za":
        raise HTTPException(status_code=400, detail="Invalid WeThinkCode email")

    if email_split[0][-3:] != "023":
        raise HTTPException(status_code=400, detail=f"Cohost {email_split[0][-3:]} not permitted")