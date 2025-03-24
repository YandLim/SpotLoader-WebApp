import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = "Sy"
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")