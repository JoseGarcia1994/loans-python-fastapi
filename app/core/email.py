# 📦 Standard library
import os

# 🌐 Third-party
from dotenv import load_dotenv
from fastapi_mail import ConnectionConfig

load_dotenv()

mail_conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_FROM_NAME=os.getenv(
        "MAIL_FROM_NAME",
        "PrestaControl",
    ),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv(
        "MAIL_SERVER",
        "smtp.gmail.com",
    ),
    MAIL_STARTTLS=os.getenv(
        "MAIL_STARTTLS",
        "true",
    ).lower() == "true",
    MAIL_SSL_TLS=os.getenv(
        "MAIL_SSL_TLS",
        "false",
    ).lower() == "true",
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)