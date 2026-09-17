import os
import smtplib

from email.mime.text import MIMEText
from dotenv import load_dotenv


load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


def send_verification_email(email: str, token: str):
    """
    Send an email verification message to a registered user.

    The function creates a verification URL containing a JWT token
    and sends it to the user's email address using the configured
    SMTP server.

    Args:
        email: Recipient's email address.
        token: JWT token used to verify the user's email address.

    Returns:
        None
    """
    verification_url = (
        f"http://127.0.0.1:8000/verify-email?token={token}"
    )

    message = MIMEText(
        f"Для підтвердження електронної пошти перейдіть за посиланням:\n"
        f"{verification_url}"
    )

    message["Subject"] = "Підтвердження електронної пошти"
    message["From"] = SMTP_USER
    message["To"] = email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(message)