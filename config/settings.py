from dotenv import load_dotenv
from flask import request
import mysql.connector
import os
import openai
import requests

load_dotenv(verbose=True)

BASE_DIR = "/var/www/procon34-cyber-wars-php"
HOST = os.getenv("DB_HOST")
USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
DATABASE = os.getenv("DATABASE")

openai.api_key = os.getenv("OPENAI_API_KEY")
prompt = ""
target_table = None
messages = []


def initialize():
    # 以前まで会話をリセット
    global messages
    messages.clear()

    if request.get_json()["prompt"]:
        global prompt
        prompt = request.get_json()["prompt"]

    if request.get_json()["target_table"]:
        global target_table
        target_table = request.get_json()["target_table"]
    elif request.get_json()["target_table"] == "null":
        target_table = None

    conn = mysql.connector.connect(host=HOST, user=USER, password=PASSWORD, database=DATABASE)
    cursor = conn.cursor()
    return conn, cursor, prompt, target_table