import os
import openai
from dotenv import load_dotenv

load_dotenv(verbose=True)

BASE_DIR = "/var/www/procon34-cyber-wars-php/"
HOST = os.getenv("DB_HOST")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
DATABASE = os.getenv("DATABASE")

openai.api_key = os.getenv("OPENAI_API_KEY")
prompt = ""