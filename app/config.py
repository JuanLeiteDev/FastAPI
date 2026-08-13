from dotenv import load_dotenv
import os

load_dotenv()

ALGORITHM = os.getenv("ALGORITHM")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY_2FA = os.getenv("SECRET_KEY_2FA")
SALT = os.getenv("SALT")
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM")
