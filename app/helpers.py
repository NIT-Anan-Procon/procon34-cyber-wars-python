from config.settings import *
from flask import request
from googletrans import Translator
import os
import re
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import subprocess

def chat(prompt):
    return openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": prompt
            }
        ],
        temperature=0.8
    ).choices[0].message.content

def generate_file(text, extension, file_name=None):
    code_pattern = re.compile(r'```{}\s+(.*?)```'.format(extension), re.DOTALL)
    code = code_pattern.findall(text)
    
    if file_name:
        with open(file_name, "w") as file:
            file.write(code[0])
    else:
        return code

def get_prompt():
    global prompt
    if request.get_json()["prompt"]:
        return request.get_json()["prompt"]
    else:
        return prompt

def make_environment(chat, challenge_id):
    dir = BASE_DIR + challenge_id
    os.makedirs(dir, exist_ok=True)
    subprocess.run(['cp', BASE_DIR + "/.env", dir + "/.env"])
    subprocess.run(['cp', '-r', BASE_DIR + "/vendor", dir + "/vendor"])
    generate_file(chat, "php", dir + "/index.php")
    generate_file(chat, "css", dir + "/style.css")

    translator = Translator()
    hint = translator.translate(generate_file(chat, "hint")[0], dest='ja').text
    answer = translator.translate(generate_file(chat, "answer")[0], dest='ja').text
    return hint, answer

def test(challenge_id):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    res = requests.get("https://localhost/php/" + challenge_id + "/index.php", verify=False)
    if res.status_code != 200:
        cleanup_challenge(challenge_id)
        return {"message": "unsuccessful"}
    else:
        return {"message": "ok"}

def cleanup_challenge(challenge_id):
    subprocess.run(['rm', '-rf', BASE_DIR + str(challenge_id)])