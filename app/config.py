from dotenv import load_dotenv
import os

load_dotenv()

ALGORITHM = os.getenv("ALGORITHM")
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY_2FA = os.getenv("SECRET_KEY_2FA")
SALT = os.getenv("SALT")
