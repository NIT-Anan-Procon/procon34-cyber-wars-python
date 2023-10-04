from config.settings import *
from googletrans import Translator
import os
import re
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import subprocess


def chat(prompt):
    messages.append(
        {
            "role":    "user",
            "content": prompt
        }
    )

    response =  openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.8
    ).choices[0].message

    messages.append(response)

    return response.content


def extract_comma(input_text):
    parts = input_text.split(',')
    return parts[0]


def generate_file(text, extension, file_name=None):
    code_pattern = re.compile(r'```{}\s+(.*?)```'.format(extension), re.DOTALL)
    code = code_pattern.findall(text)
    if len(code) == 0:
        code_pattern = re.compile(r'```{}\s+(.*?)```'.format(extension.upper()), re.DOTALL)
        code = code_pattern.findall(text)
    
    if file_name:
        with open(file_name, "w") as file:
            file.write(code[0])
    else:
        return code


def is_alpha(text):
    pattern = r"^[a-zA-Z]+$"
    return bool(re.match(pattern, text)) or text == ','


def make_environment(chat, challenge_id):
    dir = BASE_DIR + "/challenge/" + challenge_id
    os.makedirs(dir, exist_ok=True)
    subprocess.run(['cp', BASE_DIR + "/.env", dir + "/.env"])
    subprocess.run(['cp', '-r', BASE_DIR + "/vendor", dir + "/vendor"])
    generate_file(chat, "php", dir + "/index.php")
    generate_file(chat, "css", dir + "/style.css")

    translator = Translator()
    hint = translator.translate(generate_file(chat, "hint")[0], dest='ja').text
    answer = extract_comma(generate_file(chat, "csv")[0])
    answer = to_comma_separated(answer)
    return hint, answer


def test(challenge_id):
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    res = requests.get("https://localhost/php/challenge/" + challenge_id + "/index.php", verify=False)
    print(res)
    if res.status_code != 200:
        return {"message": "unsuccessful"}
    else:
        return {"message": "ok"}


def to_comma_separated(input_text):
    transformed_text = input_text.replace(' ', ',')
    print(transformed_text)

    result = ""
    for i in range(len(transformed_text)):
        result += transformed_text[i]
        if i == len(transformed_text) - 1:
            continue
        if is_alpha(transformed_text[i]) == False and is_alpha(transformed_text[i + 1]) == False:
            print(transformed_text[i], transformed_text[i + 1])
            result += ','

    return result


def cleanup_challenge(challenge_id):
    subprocess.run(['rm', '-rf', BASE_DIR + "/challenge/" + str(challenge_id)])
